from django.conf import settings
from django_assets import Bundle, register

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
        css = (
            "blog/css/blog.css",
            "blog/css/blog_list.css",
        ),
        js = (
            "blog/js/blog.js",
            jquery_composite_bundle.js # you can include another composite bundles this way
        )
    ).register()

    """
    def __init__(self, name, path, css=None, js=None):
        self.name = name
        self.path = path

        if isinstance(css, (tuple, list)):
            self.css = CssBundle(*css)
        else:
            self.css = css

        if isinstance(js, (tuple, list)):
            self.js = CssBundle(*js)
        else:
            self.js = js

    @property
    def name_css(self):
        return self.name + '_css'

    @property
    def name_js(self):
        return self.name + '_js'

    def register(self):
        if self.css:
            register(self.name_css, self.css, output="%s/css/%s.css" % (self.path, self.name))
        if self.js:
            register(self.name_js, self.js, output="%s/js/%s.js" % (self.path, self.name))
