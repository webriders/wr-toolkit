
try:
    from django.conf import settings

    DEFAULT_CSS_FILTERS = getattr(settings, 'ASSETS_DEFAULT_CSS_FILTERS', '')
    DEFAULT_JS_FILTERS = getattr(settings, 'ASSETS_DEFAULT_JS_FILTERS', '')
except ImportError:
    DEFAULT_CSS_FILTERS = ''
    DEFAULT_JS_FILTERS = ''