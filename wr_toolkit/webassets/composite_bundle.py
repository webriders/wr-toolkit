from django.conf import settings
from django_assets import Bundle, register


class CompositeBundleError(Exception):
    pass


class AbstractBundle(Bundle):
    DEFAULT_FILTERS = None

    def __init__(self, *contents, **options):
        filters = options.get('filters', None)
        if not filters:
            filters = self.DEFAULT_FILTERS
        options['filters'] = filters
        super(AbstractBundle, self).__init__(*contents, **options)


class CssBundle(AbstractBundle):
    DEFAULT_FILTERS = settings.ASSETS_CSS_FILTERS


class JsBundle(AbstractBundle):
    DEFAULT_FILTERS = settings.ASSETS_JS_FILTERS


class CompositeBundle(object):
    """
    Composite bundle groups js and css bundles in one and remove duplicates in multiple bundle code.

    Example usage:

    CompositeBundle(
        name = 'blog_list_all',
        path = 'blog',
        includes = (
            other_composite_bundle,
        ),
        css = (
            "blog/css/blog.css",
            "blog/css/blog_list.css",
        ),
        js = (
            "blog/js/blog.js",
            jquery_composite_bundle.js
        )
    ).register()

    """
    def __init__(self, name=None, path=None, css=None, js=None, includes=None):
        if includes:
            assert isinstance(includes, (tuple, list)), "'includes' parameter must be list or tuple"
            assert all(isinstance(i, CompositeBundle) for i in includes), "All includes must be instance of CompositeBundle"

        self.name = name
        self.path = path

        self.css = css or []
        self.js = js or []
        self.includes = includes or []

    @property
    def name_css(self):
        return self.name + '_css'

    @property
    def name_js(self):
        return self.name + '_js'

    def get_merged_bundles_list(self):
        merged_css = []
        merged_js = []

        for incl in self.includes:
            css, js = incl.get_merged_bundles_list()
            merged_css.extend(css)
            merged_css.extend(js)

        merged_css.extend(self.css)
        merged_css.extend(self.js)

        return merged_css, merged_js

    def get_merged_bundles(self):
        css, js = self.get_merged_bundles_list()
        return CssBundle(*css), JsBundle(*js)

    def register(self):
        if not self.name or not self.path:
            raise CompositeBundleError("both 'name' and 'path' must be filled")

        merged_css, merged_js = self.get_merged_bundles()

        if merged_css:
            register(self.name_css, merged_css, output="%s/css/%s.css" % (self.path, self.name))

        if merged_js:
            register(self.name_js, merged_js, output="%s/js/%s.js" % (self.path, self.name))
