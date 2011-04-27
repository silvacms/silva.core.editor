# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import operator
import unittest

from five import grok
from zope.publisher.browser import TestRequest

from silva.core.editor.text import Text
from silva.core.editor.transform.interfaces import (
    IDisplayFilter, IIntroductionFilter)

from silva.core.editor.testing import FunctionalLayer


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
        self.assertTrue(
            reduce(operator.and_,
                   map(IDisplayFilter.providedBy,
                       transformers)),
            "only display filter")

    def test_intro(self):
        version = self.root.document.get_editable()
        transformers = grok.queryOrderedMultiSubscriptions(
            (version, TestRequest()), IIntroductionFilter)
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
    suite.addTest(unittest.makeSuite(TextTestCase))
    suite.addTest(unittest.makeSuite(TestIntro))
    return suite

