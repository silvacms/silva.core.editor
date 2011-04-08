import unittest

from zope.publisher.browser import TestRequest

from silva.core.editor.text import Text
from silva.core.editor.testing import FakeTarget
from infrae.testing import ZCMLLayer
import silva.core.editor

html_chunk = \
"""
<html>
<head></head>
<body>
    <p></p>
    <span>some span text</span>
    <h3>Title</h3>
    <p>
        First paragraph of text, this is <strong>important</strong>
        <a href="http://infrae.com">and there is a link</a> in it.
    </p>
    <p></p>
</body>
</html>"""

html_chunk_simple = \
"""
<html>
<head></head>
<body>
    <h3>Title</h3>
    <p>
        First paragraph of text, this is <strong>important</strong>
        <a href="http://infrae.com">and there is a link</a> in it.
    </p>
</body>
</html>"""


class TestIntro(unittest.TestCase):
    layer = ZCMLLayer(silva.core.editor)

    def test_text_intro_simple(self):
        text = Text("test_intro", html_chunk_simple)
        intro = text.render_intro(FakeTarget(), TestRequest())
        self.assertEquals(intro,
"""<p>
        First paragraph of text, this is <strong>important</strong>
        <a href="http://infrae.com">and there is a link</a> in it.
    </p>
""")

    def test_text_intro_simple_truncate(self):
        text = Text("test_intro", html_chunk_simple)
        intro = text.render_intro(FakeTarget(), TestRequest(), max_length=50)
        self.assertEquals(intro,
"""<p>
        First paragraph of text, this is <strong>important</strong>
        <a href="http://infrae.com">and th&#8230;</a></p>""")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestIntro))
    return suite

