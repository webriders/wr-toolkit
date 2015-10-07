import unittest
import sys

PY3 = sys.version_info[0] == 3


class TestCompositeBundle(unittest.TestCase):
    def setUp(self):
        if PY3:
            from django.conf import settings
            settings.configure()

    def test_get_merged_bundles(self):
        from composite_bundle import CompositeBundle, CompiledBundle

        bundle1 = CompositeBundle(
            name='test_bundle',
            path='test',
            css=(
                'test/css/header.css',
                'test/css/footer.css',
                'test/css/page.css',
            ),
            js=(
                'test/js/jquery.js',
            )
        )

        bundle2 = CompositeBundle(
            name='test_bundle2',
            path='test',
            includes=(bundle1,),
            css=(
                'test/css/common.css',
            ),
            js=(
                'test/js/jquery.js',  # duplicate js
                'test/js/common.js',
            ),
            filters_css=('cssrewrite', 'cssmin',),
            filters_js=('jsmin',),
        )

        bundle_compiled = CompiledBundle(
            name='test_compiled',
            path='test',
            css=(
                'test/css/style.scss',
                'test/css/common.scss',
            )
        )

        bundle3 = CompositeBundle(
            name='test_bundle3',
            path='test',
            includes=(bundle2, bundle_compiled,),
            css=(
                'test/css/common.css',
                'test/css/my.css'
            ),
            js=(
                'test/js/test.js'
            )
        )

        bundles1_css, bundles1_js = bundle1.get_merged_bundles()
        bundles2_css, bundles2_js = bundle2.get_merged_bundles()
        bundles3_css, bundles3_js = bundle3.get_merged_bundles()

        self.assertEqual(len(bundles1_css), 1)
        self.assertEqual(len(bundles1_css[0].filters), 0)
        self.assertEqual(len(bundles1_js), 1)
        self.assertEqual(len(bundles1_js[0].filters), 0)
        self.assertEqual(bundles1_css[0].contents, ('test/css/header.css', 'test/css/footer.css', 'test/css/page.css',))
        self.assertEqual(bundles1_js[0].contents, ('test/js/jquery.js',))

        self.assertEqual(len(bundles2_css), 1)
        self.assertEqual(len(bundles2_css[0].filters), 2)
        self.assertEqual(bundles2_css[0].filters[0].__class__.__name__, 'CSSRewrite' if PY3 else 'CSSRewriteFilter')
        self.assertEqual(bundles2_css[0].filters[1].__class__.__name__, 'CSSMin' if PY3 else 'CSSMinFilter')

        self.assertEqual(len(bundles2_js), 1)
        self.assertEqual(len(bundles2_js[0].filters), 1)
        self.assertEqual(bundles2_js[0].filters[0].__class__.__name__, 'JSMin' if PY3 else 'JSMinFilter')

        self.assertEqual(bundles2_css[0].contents,
                         ('test/css/header.css', 'test/css/footer.css', 'test/css/page.css', 'test/css/common.css'))
        self.assertEqual(bundles2_js[0].contents, ('test/js/jquery.js', 'test/js/common.js'))

        bundles3_css = sorted(bundles3_css, key=lambda x: len(x.filters))
        self.assertEqual(len(bundles3_css), 2)
        self.assertEqual(len(bundles3_css[0].filters), 0)
        self.assertEqual(bundles3_css[0].contents, ('test/css/style.scss', 'test/css/common.scss'))
        self.assertEqual(len(bundles3_css[1].filters), 2)
        self.assertEqual(bundles3_css[1].filters[0].__class__.__name__, 'CSSRewrite' if PY3 else 'CSSRewriteFilter')
        self.assertEqual(bundles3_css[1].filters[1].__class__.__name__, 'CSSMin' if PY3 else 'CSSMinFilter')
        self.assertEqual(bundles3_css[1].contents, (
            'test/css/header.css', 'test/css/footer.css', 'test/css/page.css', 'test/css/common.css',
            'test/css/my.css'))


if __name__ == '__main__':
    unittest.main()
