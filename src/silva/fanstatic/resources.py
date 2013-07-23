
from fanstatic.core import inclusion_renderers, get_needed, normalize_groups
from fanstatic.core import UnknownResourceExtensionError
from fanstatic.core import Renderable


class DummyLibrary(object):

    def __init__(self, library_nr):
        self.name = 'dummy'
        self.library_nr = library_nr

    def init_library_nr(self):
        pass

    def signature(self, **options):
        return u''


class ExternalResource(Renderable):

    def __init__(self, url, category='js', depends=None, bottom=False):
        """External resource. category can be js, css or ico.
        """
        dependency_nr = 0
        self.url = url
        self.ext = '.' + category
        self.depends = set()
        self.resources = set([self])
        if depends is not None:
            self.depends.update(normalize_groups(depends))
            for depend in self.depends:
                self.resources.update(depend.resources)
                dependency_nr = max(depend.dependency_nr + 1,
                                    dependency_nr)
        self.supersedes = []
        self.rollups = []
        self.relpath = None     # Used by sort_components
        self.library = DummyLibrary(dependency_nr)
        self.dependency_nr = dependency_nr
        self.bottom = bottom
        self.dont_bundle = True # We can never bundle this
        if self.ext not in inclusion_renderers:
            raise UnknownResourceExtensionError(
                "Unknown resource extension %s for url %s" % (
                    self.ext, url))
        self.order, self.renderer = inclusion_renderers[self.ext]

    def __hash__(self):
        # Include resource url inside the hash
        return hash(('ExternalResource', self.url))

    def __eq__(self, other):
        if isinstance(other, ExternalResource):
            return other.url == self.url
        return False

    def mode(self, mode):
        return self

    def render(self, _):
        return self.renderer(self.url)

    def need(self):
        needed = get_needed()
        needed.need(self, None)

    def __repr__(self):
        return "<ExternalResource '%s'>" % (self.url)


class Snippet(Renderable):
    TEMPLATES = {
        '.js': '<script type="text/javascript">%s</script>',
        '.css': '<style type="text/css">%s</style>',
        }

    def __init__(self, snippet, category='js', depends=None, bottom=False):
        """A snippet. Category can be js or css.
        """
        dependency_nr = 0
        self.snippet = snippet
        self.ext = '.' + category
        self.depends = set()
        self.resources = set([self])
        if depends is not None:
            self.depends.update(normalize_groups(depends))
            for depend in self.depends:
                self.resources.update(depend.resources)
                dependency_nr = max(depend.dependency_nr + 1,
                                    dependency_nr)
        self.supersedes = []
        self.rollups = []
        self.relpath = None     # Used by sort_components
        self.library = DummyLibrary(dependency_nr)
        self.dependency_nr = dependency_nr
        self.bottom = bottom
        self.dont_bundle = True # We can never bundle this
        if self.ext not in inclusion_renderers:
            raise UnknownResourceExtensionError(
                "Unknown resource type %s" % self.ext)
        self.order, _ = inclusion_renderers[self.ext]

    def __hash__(self):
        # Include resource url inside the hash
        return hash(('Snippet', self.snippet))

    def __eq__(self, other):
        if isinstance(other, Snippet):
            return other.snippet == self.snippet
        return False

    def mode(self, mode):
        return self

    def render(self, _):
        template = self.TEMPLATES.get(self.ext)
        if template is not None:
            return template % self.snippet
        return ''

    def need(self):
        needed = get_needed()
        needed.need(self, None)

    def __repr__(self):
        return "<Snippet for %s>" % (self.ext[1:])
