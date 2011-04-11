
import unittest
from silva.core.editor.utils import html_truncate


class TestStrip(unittest.TestCase):

    def test_html_truncate(self):
        html = """<p>some text<a href="#somelink">link</a> and some<span> tail<div></div></span>asdf</p>"""

        self.assertEquals(
            """<p>some text<a href="#somelink">link</a> and&#8230;</p>""",
            html_truncate(17, html))

        self.assertEquals(
            """<p>some text<a href="#somelink">link</a> and some<span> t&#8230;</span></p>""",
            html_truncate(24, html))

        self.assertEquals(
            """<p>some text<a href="#somelink">link</a> and some<span> tail<div></div></span>a&#8230;</p>""",
            html_truncate(28, html))

        self.assertEquals(
            """<p>&#8230;</p>""",
            html_truncate(0, html))

        self.assertEquals(
            """<p>some text<img src="#somewhere"> an&#8230;</p>""",
            html_truncate(12,
                """<p>some text<img src="#somewhere" /> and some tail</p>"""))


    def test_spaces_does_not_count(self):
        html = """<p>some     text<a href="#somelink">link</a>
        \t\n\t\n  and some
        	<span> tail<div></div></span>as      df</p>"""

        self.assertEquals(
            '<p>some     text<a href="#somelink">link</a> and&#8230;</p>',
            html_truncate(17, html))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestStrip))
    return suite


