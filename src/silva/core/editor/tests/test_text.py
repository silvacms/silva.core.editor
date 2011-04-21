
import operator
import unittest

from five import grok
from zope.publisher.browser import TestRequest

from silva.core.editor.text import Text
from silva.core.editor.transform.interfaces import (
    IDisplayFilter, IIntroductionFilter)

from Products.Silva.testing import FunctionalLayer
from Products.Silva.tests.mockers import MockupVersion


html_chunk = \
"""
<html>
<head></head>
<body>
    <h3>Title</h3>
    <p>
        First paragraph of text, this is <strong>important</strong>
        <a href="http://infrae.com">and there is a link</a> in it.
    </p>
    <p> Second paragraph</p>
</body>
</html>"""


class TestText(unittest.TestCase):
    layer = FunctionalLayer

    def test_display(self):
        transformers = grok.queryOrderedMultiSubscriptions(
            (MockupVersion('0'), TestRequest()), IDisplayFilter)
        self.assertNotEqual(len(transformers), 0)
        self.assertTrue(
            reduce(operator.and_,
                   map(IDisplayFilter.providedBy,
                       transformers)),
            "only display filter")

    def test_intro(self):
        transformers = grok.queryOrderedMultiSubscriptions(
            (MockupVersion('0'), TestRequest()), IIntroductionFilter)
        self.assertNotEqual(len(transformers), 0)
        self.assertFalse(
            reduce(operator.and_,
                   map(IDisplayFilter.providedBy,
                       transformers)),
            "not all display filter")


class TestIntro(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('test', 'Test Content')

    def test_text_intro(self):
        text = Text("test_intro", html_chunk)
        intro = text.render_intro(
            self.root.test.get_editable(), TestRequest())
        self.assertEquals(intro,
"""<p>
        First paragraph of text, this is <strong>important</strong>
        <a href="http://infrae.com">and there is a link</a> in it.
    </p>
    """)

    def test_text_intro_truncate(self):
        text = Text("test_intro", html_chunk)
        intro = text.render_intro(
            self.root.test.get_editable(), TestRequest(), max_length=50)
        self.assertEquals(intro,
"""<p>
        First paragraph of text, this is <strong>important</strong>
        <a href="http://infrae.com">and th&#8230;</a></p>""")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestText))
    suite.addTest(unittest.makeSuite(TestIntro))
    return suite

