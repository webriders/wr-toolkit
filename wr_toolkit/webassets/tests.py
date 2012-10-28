import unittest
from composite_bundle import CompositeBundle


class TestCompositeBundle(unittest.TestCase):
    def test_get_merged_bundles(self):

        bundle1 = CompositeBundle(
            name = 'test_bundle',
            path = 'test',
            css = (
                'test/css/header.css',
                'test/css/footer.css',
                'test/css/page.css',
            ),
            js = (
                'test/js/jquery.js',
            )
        )

        bundle2 = CompositeBundle(
            name = 'test_bundle',
            path = 'test',
            includes = (bundle1,),
            css = (
                'test/css/common.css',
            ),
            js = (
                'test/js/jquery.js', # duplicate js
                'test/js/common.js',
            ),
            filters_css = ('cssrewrite', 'cssmin',),
            filters_js = ('jsmin',),
        )

        bundle1_css, bundle1_js = bundle1.get_merged_bundles()
        bundle2_css, bundle2_js = bundle2.get_merged_bundles()

        self.assertEqual(bundle1_css.filters, ())
        self.assertEqual(bundle1_js.filters, ())
        self.assertEqual(bundle1_css.contents, ('test/css/header.css', 'test/css/footer.css', 'test/css/page.css',))
        self.assertEqual(bundle1_js.contents, ('test/js/jquery.js',))

        self.assertEqual(len(bundle2_css.filters), 2)
        self.assertEqual(bundle2_css.filters[0].__class__.__name__, 'CSSRewriteFilter')
        self.assertEqual(bundle2_css.filters[1].__class__.__name__, 'CSSMinFilter')

        self.assertEqual(len(bundle2_js.filters), 1)
        self.assertEqual(bundle2_js.filters[0].__class__.__name__, 'JSMinFilter')

        self.assertEqual(bundle2_css.contents, ('test/css/header.css', 'test/css/footer.css',
                                                'test/css/page.css', 'test/css/common.css'))
        self.assertEqual(bundle2_js.contents, ('test/js/jquery.js', 'test/js/common.js'))


if __name__ == '__main__':
    unittest.main()
