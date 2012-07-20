# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from five import grok

from silva.core.editor.text import Text
from silva.core.editor.transform.interfaces import IDisplayFilter

from silva.core.editor.testing import FunctionalLayer
from Products.Silva.testing import TestCase, TestRequest

HTML_CHUNK = """
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


class TextTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', 'Document')

    def test_display(self):
        version = self.root.document.get_editable()
        transformers = grok.queryOrderedMultiSubscriptions(
            (version, TestRequest()), IDisplayFilter)
        self.assertNotEqual(len(transformers), 0)


class IntroductionTestCase(TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('test', 'Test Content')

    def test_text_introduction(self):
        text = Text("test_intro", HTML_CHUNK)
        intro = text.render_introduction(
            self.root.test.get_editable(), TestRequest())
        self.assertXMLEqual("""<p>
        First paragraph of text, this is <strong>important</strong>
        <a href="http://infrae.com">and there is a link</a> in it.
        </p>""", intro)

    def test_text_introduction_truncate(self):
        text = Text("test_intro", HTML_CHUNK)
        intro = text.render_introduction(
            self.root.test.get_editable(), TestRequest(), max_length=50)
        self.assertXMLEqual("""<p>
        First paragraph of text, this is <strong>important</strong>
        <a href="http://infrae.com">and th&#8230;</a></p>""", intro)

        intro = text.render_introduction(
            self.root.test.get_editable(), TestRequest(), max_length=20)
        self.assertXMLEqual("""<p>First paragraph of &#8230;</p>""", intro)


class FullTextTestCase(TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('test', 'Test Content')

    def test_text_fulltext(self):
        text = Text("test_fulltext", HTML_CHUNK)
        fulltext = text.fulltext(self.root.test.get_editable(), TestRequest())
        text = """



    Title
    
        First paragraph of text, this is important
        and there is a link in it.
    
     Second paragraph

"""
        self.assertEquals(fulltext, text)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TextTestCase))
    suite.addTest(unittest.makeSuite(IntroductionTestCase))
    suite.addTest(unittest.makeSuite(FullTextTestCase))
    return suite

