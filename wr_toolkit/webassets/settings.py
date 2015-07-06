
try:
    from django.conf import settings

    DEFAULT_CSS_FILTERS = getattr(settings, 'ASSETS_DEFAULT_CSS_FILTERS', '')
    DEFAULT_JS_FILTERS = getattr(settings, 'ASSETS_DEFAULT_JS_FILTERS', '')
    DEFAULT_CSS_COMPILER = getattr(settings, 'ASSETS_DEFAULT_CSS_COMPILER', '')
    DEFAULT_JS_COMPILER = getattr(settings, 'ASSETS_DEFAULT_JS_COMPILER', '')
    DEFAULT_ASSETS_DEBUG = getattr(settings, 'ASSETS_DEBUG', True)
except ImportError:
    DEFAULT_CSS_FILTERS = ''
    DEFAULT_JS_FILTERS = ''
    DEFAULT_CSS_COMPILER = ''
    DEFAULT_JS_COMPILER = ''
    DEFAULT_ASSETS_DEBUG = True