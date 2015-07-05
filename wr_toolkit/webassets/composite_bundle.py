from collections import MutableMapping
from django.core.exceptions import ImproperlyConfigured
from django_assets import Bundle, register
from settings import DEFAULT_CSS_FILTERS, DEFAULT_JS_FILTERS, DEFAULT_CSS_COMPILER, DEFAULT_JS_COMPILER, DEFAULT_ASSETS_DEBUG


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

    debug = DEFAULT_ASSETS_DEBUG

    def __init__(self, name=None, path=None, css=None, js=None, includes=None, filters_css=None, filters_js=None):
        if includes:
            assert isinstance(includes, (tuple, list)), "'includes' parameter must be list or tuple"
            assert all(isinstance(i, CompositeBundle) for i in includes), "All includes must be instance of CompositeBundle"

        self.name = name
        self.path = path

        self.css = css or []
        self.js = js or []
        self.includes = includes or []

        self.filters_css = filters_css or DEFAULT_CSS_FILTERS
        if isinstance(self.filters_css, str):
            self.filters_css = map(str.strip, self.filters_css.split(",")) if self.filters_css else []

        self.filters_js = filters_js or DEFAULT_JS_FILTERS
        if isinstance(self.filters_js, str):
            self.filters_js = map(str.strip, self.filters_js.split(",")) if self.filters_js else []

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
        files_by_ext = self.get_files_by_ext()

        for js_or_css in files_by_ext.values():
            for ext_files in js_or_css.values():
                ext_files["files"] = self._clean_duplicates(ext_files.get("files", []))
                ext_files["filters"] = self._clean_duplicates(ext_files.get("filters", []))

        css_bundles = []
        js_bundles = []

        for js_or_css, js_or_css_files in files_by_ext.items():
            bundles = css_bundles if js_or_css == "css" else js_bundles
            for ext, js_css in js_or_css_files.items():
                if js_css["filters"] is None:
                    raise ImproperlyConfigured('You need to specify ASSETS_DEFAULT_CSS_FILTERS in your Django settings file')
                elif js_css["filters"] == '':
                    bundles.append(Bundle(*js_css["files"], output="%s/js/%s_%s.%s" % (self.path, self.name, ext, js_or_css), debug=self.debug))
                else:
                    bundles.append(Bundle(*js_css["files"], filters=js_css["filters"], output="%s/js/%s_%s.%s" % (self.path, self.name, ext, js_or_css), debug=self.debug))

        return css_bundles, js_bundles

    def get_files_by_ext(self, files_by_ext=None):
        """
        Example:
        >> {
        >>     "css": {
        >>         "scss": {"files":["test/css/style.scss"], "filters":[]},
        >>         "css": {"files":["test/css/style.css"], "filters":[]}
        >>      },
        >>      "js": {
        >>          "js": {"files": ["test/js/main.js"], "filters":[]}
        >>      }
        >> }
        """

        if files_by_ext is None:
            files_by_ext = {
                "css": {},
                "js": {}
            }

        if len(self.includes) > 0:
            for incl in self.includes:
                incl.get_files_by_ext(files_by_ext)

        for css in self.css:
            ext = css.split(".")[-1]
            if files_by_ext["css"].get(ext) is None:
                files_by_ext["css"][ext] = {
                    "files": [],
                    "filters": []
                }

            files_by_ext["css"][ext]["files"].append(css)
            files_by_ext["css"][ext]["filters"].extend(self.filters_css)

        for js in self.js:
            ext = js.split(".")[-1]
            if files_by_ext["js"].get(ext) is None:
                files_by_ext["js"][ext] = {
                    "files": [],
                    "filters": []
                }

            files_by_ext["js"][ext]["files"].append(js)
            files_by_ext["js"][ext]["filters"].extend(self.filters_js)

        return files_by_ext

    @staticmethod
    def _clean_duplicates(items):
        """
        Clean duplicates with saving order
        """
        unique_files = []
        for item in items:
            if item not in unique_files:
                unique_files.append(item)
        return unique_files

    @staticmethod
    def _get_list_filters(filters_str):
        if filters_str:
            if isinstance(filters_str, str):
                return map(lambda f: f.strip().lower(), filters_str.split(","))
            return filters_str
        else:
            return []


class CompiledBundle(CompositeBundle):
    debug = False

    def __init__(self, name=None, path=None, css=None, js=None, includes=None, filters_css=None, filters_js=None):
        css_compile_filters = self._get_list_filters(DEFAULT_CSS_COMPILER)
        css_filters = self._get_list_filters(DEFAULT_CSS_FILTERS)
        css_compile_filters.extend(css_filters)

        js_compile_filters = self._get_list_filters(DEFAULT_JS_COMPILER)
        js_filters = self._get_list_filters(DEFAULT_JS_FILTERS)
        js_compile_filters.extend(js_filters)

        filters_css = self._clean_duplicates(css_compile_filters)
        filters_js = self._clean_duplicates(js_compile_filters)

        super(CompiledBundle, self).__init__(
            name, path, css, js, includes, filters_css=filters_css, filters_js=filters_js
        )