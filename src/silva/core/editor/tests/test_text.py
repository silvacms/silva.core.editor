# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from Products.Silva.testing import TestCase, TestRequest

from ..interfaces import IText
from ..text import Text
from ..testing import FunctionalLayer


HTML_CHUNK = """
<html>
<head></head>
<body>
    <h3>Title</h3>
    <p>
        First paragraph of text, this is <strong>important</strong>
        <a href="http://infrae.com">and there is a link</a> in it.
    </p>
    <p> Second paragraph.</p><p>Last somewhat longer <b>para</b>graph.</p>
    <img alt="Infrae" src="infrae.png" />
</body>
</html>"""


class TextTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_text(self):
        text = Text('test_text', '')
        self.assertTrue(verifyObject(IText, text))


class IntroductionTestCase(TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('test', 'Test Content')

    def test_text_introduction(self):
        text = Text("test_intro", HTML_CHUNK)
        intro = text.introduction(
            self.root.test.get_editable(), TestRequest())
        self.assertXMLEqual("""<p>
        First paragraph of text, this is <strong>important</strong>
        <a href="http://infrae.com">and there is a link</a> in it.
        </p>""", intro)

    def test_text_introduction_truncate(self):
        text = Text("test_intro", HTML_CHUNK)
        intro = text.introduction(
            self.root.test.get_editable(), TestRequest(), max_length=50)
        self.assertXMLEqual("""<p>
        First paragraph of text, this is <strong>important</strong>
        <a href="http://infrae.com">and th&#8230;</a></p>""", intro)

        intro = text.introduction(
            self.root.test.get_editable(), TestRequest(), max_length=20)
        self.assertXMLEqual("""<p>First paragraph of &#8230;</p>""", intro)


class FullTextTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('test', 'Test Content')

    def test_text_fulltext(self):
        text = Text("test_fulltext", HTML_CHUNK)
        fulltext = text.fulltext(self.root.test.get_editable(), TestRequest())

        self.assertItemsEqual(
            fulltext,
            ['Title', 'First paragraph of text, this is', 'important',
             'and there is a link', 'in it.', 'Second paragraph.',
             'Last somewhat longer', 'para', 'graph.', 'Infrae'])

    def test_fulltext_unicode(self):
        text = Text("test_fulltext_unicode", u"<b>tête<b>")
        fulltext = text.fulltext(self.root.test.get_editable(), TestRequest())
        self.assertItemsEqual(
            fulltext,
            [u"tête"])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TextTestCase))
    suite.addTest(unittest.makeSuite(IntroductionTestCase))
    suite.addTest(unittest.makeSuite(FullTextTestCase))
    return suite

