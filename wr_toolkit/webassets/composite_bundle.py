from django.core.exceptions import ImproperlyConfigured
from django_assets import Bundle, register
from settings import DEFAULT_CSS_FILTERS, DEFAULT_JS_FILTERS


class CompositeBundleError(Exception):
    pass


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
            "blog/js/blog_list.js",
        )
        filters_css = 'custom_filters_for_css',
        filters_js = 'custom_filters_for_js',
    ).register()

    """
    def __init__(self, name=None, path=None, css=None, js=None, includes=None, filters_css=None, filters_js=None):
        if includes:
            assert isinstance(includes, (tuple, list)), "'includes' parameter must be list or tuple"
            assert all(isinstance(i, CompositeBundle) for i in includes), "All includes must be instance of CompositeBundle"

        self.name = name
        self.path = path

        self.css = css or []
        self.js = js or []
        self.includes = includes or []

        self.filters_css = filters_css
        self.filters_js = filters_js

    @property
    def name_css(self):
        return self.name + '_css'

    @property
    def name_js(self):
        return self.name + '_js'

    def register(self):
        if not self.name or not self.path:
            raise CompositeBundleError("both 'name' and 'path' must be filled")

        bundles_css, bundles_js = self.get_merged_bundles()

        if bundles_css:
            register(self.name_css, *bundles_css, output="%s/css/%s.css" % (self.path, self.name))

        if bundles_js:
            register(self.name_js, *bundles_js, output="%s/js/%s.js" % (self.path, self.name))

    def get_merged_bundles(self):
        bundle_css, bundle_js = self._get_current_bundles()
        css_bundles = []
        js_bundles = []

        for incl in self.includes:
            incl_css_bundle, incl_js_bundle = incl.get_merged_bundles()
            css_bundles.append(incl_css_bundle)
            js_bundles.append(incl_js_bundle)

        if bundle_css:
            css_bundles.append(bundle_css)
        if bundle_js:
            js_bundles.append(bundle_js)
        return css_bundles, js_bundles

    def _get_current_bundles(self):
        contents_css, contents_js = self.css, self.js
        contents_css = self._clean_duplicates(contents_css)
        contents_js = self._clean_duplicates(contents_js)

        if contents_css:
            filters_css = self.filters_css or DEFAULT_CSS_FILTERS

            if filters_css is None:
                raise ImproperlyConfigured('You need to specify ASSETS_DEFAULT_CSS_FILTERS in your Django settings file')
            elif filters_css == '':
                bundle_css = Bundle(*contents_css)
            else:
                bundle_css = Bundle(*contents_css, filters=filters_css)
        else:
            bundle_css = None

        if contents_js:
            filters_js = self.filters_js or DEFAULT_JS_FILTERS

            if filters_js is None:
                raise ImproperlyConfigured('You need to specify ASSETS_DEFAULT_JS_FILTERS in your Django settings file')
            elif filters_js == '':
                bundle_js = Bundle(*contents_js)
            else:
                bundle_js = Bundle(*contents_js, filters=filters_js)
        else:
            bundle_js = None

        return bundle_css, bundle_js

    def _clean_duplicates(self, items):
        items_set = set(items)
        unique_items = []

        for item in reversed(items):
            if item in items_set:
                items_set.remove(item)
                unique_items.append(item)

        unique_items.reverse()
        return unique_items
