
from fanstatic import compat, Inclusion
import re

class Test(object):
    pass


class URLTest(Test):
    name = 'the url ends with (path)'
    expr = re.compile(r'the url ends with (?P<path>.*)')

    def __init__(self, path):
        self.path = path

    def context(self):
        return {}

    def test(self, request, response, html):
        return request.path.endswith(self.path)


class ContainsTest(Test):
    name = 'there is (pattern)'
    expr = re.compile('there is (?P<value>.*)')

    def __init__(self, value):
        self.value = value

    def context(self):
        return {'context': self.value}

    def test(self, request, response, html):
        return self.value in html


TESTS = [URLTest, ContainsTest]


class Action(object):
    pass


class ReplaceAction(Action):
    name = 'replace (tag) with'
    expr = re.compile(r'replace ((?P<tag>.*) )?with')

    def __init__(self, tag=None):
        self.tag = tag

    def inject(self, html, resources, context):
        if self.tag is None:
            tag = context.get('context')
        else:
            tag = self.tag
        return html.replace(
            compat.as_bytestring(tag),
            compat.as_bytestring(resources))


class InjectBeforeAction(Action):
    name = 'insert before (tag)'
    expr = re.compile(r'insert before( (?P<tag>.*))?')

    def __init__(self, tag=None):
        self.tag = tag

    def inject(self, html, resources, context):
        if self.tag is None:
            tag = context.get('context')
        else:
            tag = self.tag
        return html.replace(
            compat.as_bytestring(tag),
            compat.as_bytestring(resources + '\n'+ tag))


class InjectAfterAction(Action):
    name = 'insert after (tag)'
    expr = re.compile(r'insert after( (?P<tag>.*))?')

    def __init__(self, tag=None):
        self.tag = tag

    def inject(self, html, resources, context):
        if self.tag is None:
            tag = context.get('context')
        else:
            tag = self.tag
        return html.replace(
            compat.as_bytestring(tag),
            compat.as_bytestring(tag + '\n'+ resources))

ACTIONS = [ReplaceAction, InjectBeforeAction, InjectAfterAction]


class ResourceSelector(object):
    pass


class BottomSelector(ResourceSelector):
    selector = 'bottom'

    def test(self, resource):
        return resource.bottom is True


class TopSelector(ResourceSelector):
    selector = 'top'

    def test(self, resource):
        return resource.bottom is False


class JSSelector(ResourceSelector):
    selector = 'js'

    def test(self, resource):
        return resource.ext == '.js'


class CSSSelector(ResourceSelector):
    selector = 'css'

    def test(self, resource):
        return resource.ext == '.css'

class ICOSelector(ResourceSelector):
    selector = 'ico'

    def test(self, resource):
        return resource.ext == '.ico'


SELECTORS = [BottomSelector,TopSelector,
             JSSelector, CSSSelector, ICOSelector]


class DefaultRule(object):
    default = True

    def __init__(self, action):
        self._action = action

    def context(self):
        return {}

    def inject(self, html, resources):
        return self._action.inject(html, resources, self.context())


class Rule(DefaultRule):
    default = False

    def __init__(self, action, selectors, tests):
        super(Rule, self).__init__(action)
        self._tests = tests
        self._selectors = selectors

    def context(self):
        context = {}
        for test in self._tests:
            context.update(test.context())
        return context

    def should_use(self, request, response, html):
        for test in self._tests:
            if not test.test(request, response, html):
                return False
        return True

    def do_resource_match(self, resource):
        for test in self._selectors:
            if not test.test(resource):
                return False
        return True


class ParseError(ValueError):

    def __init__(self, msg, lineno, detail=None):
        self.msg = msg
        self.lineno = lineno
        self.detail = detail

    def doc(self):
        msg = '\n\nError while reading rules of the resource injector:\n' + \
            '%s at line %d of the configuration.' % (self.msg, self.lineno)
        if self.detail:
            msg += '\n(%s.)' % (self.detail)
        return msg

    __str__ = doc


class RuleParser(object):

    def __init__(self):
        self._action = None
        self._tests = []
        self._selectors = []
        self._default = None

    def set_default(self, lineno, line):
        if self._default is not None:
            raise ParseError(
                'Duplicate default rule',
                lineno)
        if len(self._tests):
            raise ParseError(
                'Default rule specified in addition of tests',
                lineno)
        self._default = True

    def set_test(self, lineno, line):
        if self._default is not None:
            raise ParseError(
                'Test specified in addition of default rule',
                lineno)
        test = line.lstrip('if').strip()
        found_tests = []
        for provider in TESTS:
            match = provider.expr.match(test)
            if match:
                found_tests.append(provider(**match.groupdict()))
        if not len(found_tests):
            candidates = ', '.join(map(lambda a: '"%s"' % a.name, TESTS))
            raise ParseError(
                'Could not understand test "%s"'%  test,
                lineno,
                'Available tests are %s' % candidates)
        if len(found_tests) > 1:
            candidates = ', '.join(map(lambda a: a.name, found_tests))
            raise ParseError(
                'Ambiguous test "%s", ' % test,
                lineno,
                'the candidates are %s' % candidates)
        self._tests.append(found_tests[0])

    def set_action(self, lineno, action):
        if self._action is not None:
            raise ParseError(
                'Duplicate action',
                lineno)
        if 'all' in action:
            action, selectors = action.rsplit('all', 1)
            action = action.strip()
            for selector in selectors.rstrip('resources').split(' ')[1:]:
                selector = selector.strip()
                if selector:
                    for provider in SELECTORS:
                        if provider.selector == selector:
                            self._selectors.append(provider())
                            break
                    else:
                        raise ParseError(
                            'Unkown resource selector "%s"' % selector,
                            lineno)
        found_actions = []
        for provider in ACTIONS:
            match = provider.expr.match(action)
            if match:
                found_actions.append(provider(**match.groupdict()))
        if not len(found_actions):
            candidates = ', '.join(map(lambda a: '"%s"' % a.name, ACTIONS))
            raise ParseError(
                'Could not understand action "%s"' % action,
                lineno,
                'Available actions are %s' % candidates)
        if len(found_actions) > 1:
            candidates = ', '.join(map(lambda a: a.name, found_actions))
            raise ParseError(
                'Ambiguous action "%s", ' % action,
                lineno,
                'The candidates are %s' % candidates)
        self._action = found_actions[0]

    def emit(self, lineno):
        if self._action is None:
            raise ParseError('Missing action for rule', lineno)
        if self._default is True:
            if len(self._selectors):
                raise ParseError(
                    'Resource selector used in addition of the default rule',
                    lineno)
            return DefaultRule(self._action)
        return Rule(self._action, self._selectors, self._tests)


def parse_rules(config):
    if config is None:
        raise ParseError('Missing rules configuration', 0)
    current = None
    rules = []
    default = None
    for lineno, line in enumerate(config.splitlines()):
        line = line.strip()
        if not line:
            continue
        if line.startswith('if'):
            if current is None:
                current = RuleParser()
            current.set_test(lineno, line)
        elif line == 'otherwise':
            if current is None:
                current = RuleParser()
            current.set_default(lineno, line)
        else:
            if default is not None:
                raise ParseError(
                    'Rule defined after default rule', lineno)
            if current is None:
                raise ParseError(
                    'Could not understand line "%s"' % line,
                    lineno)
            current.set_action(lineno, line)
            result = current.emit(lineno)
            if result.default:
                default = result
            else:
                rules.append(result)
            current = None
    if current is not None:
        raise ParseError(
            'Unfinished rule on the last line', lineno)
    return default, rules


class RuleBasedInjector(object):
    name = 'rules'

    def __init__(self, options):
        self.default, self.rules = parse_rules(options.pop('rules'))

    def __call__(self, html, needed, request, response=None):
        rules = []
        for rule in self.rules:
            if rule.should_use(request, response, html):
                rules.append(rule)
        includes = {}
        for resource in needed.resources():
            for rule in rules:
                if rule.do_resource_match(resource):
                    includes.setdefault(rule.inject, []).append(resource)
                    break
            else:
                if self.default is not None:
                    includes.setdefault(self.default.inject, []).append(resource)
        for injector, resources in includes.items():
            html = injector(html, Inclusion(needed, resources).render())
        return html
