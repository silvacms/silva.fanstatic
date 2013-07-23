
from fanstatic import compat, Inclusion

def inject_replace(pattern):

    def inject(html, resources):
        return html.replace(
            compat.as_bytestring(pattern),
            compat.as_bytestring(resources))

    return inject

def inject_before(pattern):

    def inject(html, resources):
        return html.replace(
            compat.as_bytestring(pattern),
            compat.as_bytestring(resources + pattern))

    return inject

def inject_after(pattern):

    def inject(html, resources):
        return html.replace(
            compat.as_bytestring(pattern),
            compat.as_bytestring(pattern + resources))

    return inject

def check_url(pattern):

    def check(resource, html, request):
        return pattern in request.path

    return check


INJECTORS = {
    'before': inject_before,
    'after': inject_after,
    'replace': inject_replace,
    None: inject_replace}

SELECTORS = {
    'all': None,
    'bottom': lambda r, h, _: getattr(r, 'bottom', False),
    'top': lambda r, h, _: not getattr(r, 'bottom', False),
    }

TESTS = {
    'url': check_url,
    }


def convert_lines_to_list(value, at_least=3):
    if isinstance(value, compat.basestring):
        result = []
        for lineno, line in enumerate(value.splitlines()):
            items = filter(None, map(lambda s: s.strip(), line.split(',')))
            if len(items):
                # We ignore empty lines
                if len(items) < at_least:
                    raise ValueError(
                        "Line %d doesn't have at least %d elements" % (
                            lineno + 1, at_least))
                result.append(items)
        return result
    return []


def parse_rules(config):
    """Parse injection configuration. This will return a list
    containing a tuple with two test methods and a method to inject
    the resources. This list is sorted from the most custom to the
    most generic test method.
    """
    injector_config = config.get('rules', None)
    if injector_config is None:
        if config.get('bottom', False):
            injector_config = [['all', 'all', 'before:</head>'],
                               ['bottom', 'js', 'before:</body>']]
        elif config.get('force_bottom', False):
            injector_config = [['all', 'all', 'before:</head>'],
                               ['all', 'js', 'before:</body>']]
        else:
            injector_config = [['all', 'all', 'before:</head>']]
    else:
        injector_config = convert_lines_to_list(injector_config)
    for key in ('bottom', 'force_bottom', 'rules'):
        if key in config:
            del config[key]

    number_of_tests = max(map(len, injector_config)) - 1
    rules = []
    for inject_rule in injector_config:
        tests = []
        inject_point = inject_rule.pop()
        inject_method = None
        if ':' in inject_point:
            inject_method, inject_point = inject_point.split(':', 1)
        if inject_method not in INJECTORS:
            raise ValueError('Unknown injection method: %s.', inject_method)

        # First is bottom/top test
        selector = inject_rule.pop(0)
        if selector not in SELECTORS:
            raise ValueError('Unknown selector: %s.', selector)
        tests.append(SELECTORS[selector])

        # Second is extension test
        category = inject_rule.pop(0)
        if category == 'all':
            tests.append(None)
        else:
            tests.append((lambda c: lambda r, h, _:
                              getattr(r, 'ext', None) == ('.' + c))(category))

        # Other custom tests
        for test in inject_rule:
            if ':' not in test:
                raise ValueError('Malformed test')
            name, pattern = test.split(':', 1)
            if name not in TESTS:
                raise ValueError('Unknown test %s.' % name)
            tests.append(TESTS[name](pattern))

        # Add missing tests
        while len(tests) < number_of_tests:
            tests.append(None)

        rules.append((list(reversed(tests)),
                      INJECTORS[inject_method](inject_point)))
    return list(reversed(sorted(rules, key=lambda r: r[0])))


class RuleBasedInjector(object):
    name = 'rules'

    def __init__(self, options):
        self.rules = parse_rules(options)

    def __call__(self, html, needed, request, response=None):
        includes = {}
        for resource in needed.resources():
            for tests, injector in self.rules:
                for test in tests:
                    if test is not None and not test(resource, html, request):
                        break
                else:
                    includes.setdefault(injector, []).append(resource)
                    break
        for injector, resources in includes.items():
            html = injector(html, Inclusion(needed, resources).render())
        return html
