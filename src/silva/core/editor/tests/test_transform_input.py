# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


import unittest

from Products.Silva.testing import TestCase

from zope.interface.verify import verifyObject
from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest

from silva.core.editor.testing import FunctionalLayer
from silva.core.editor.text import Text
from silva.core.editor.transform.interfaces import IInputEditorFilter
from silva.core.editor.transform.interfaces import ISaveEditorFilter
from silva.core.editor.transform.interfaces import ITransformer
from silva.core.editor.transform.interfaces import ITransformerFactory
from silva.core.editor.interfaces import ITextIndexEntries


class InputTransformTestCase(TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', 'Document')
        factory.manage_addMockupVersionedContent('target', 'Document Target')
        factory.manage_addMockupVersionedContent('other', 'Other Target')

        version = self.root.document.get_editable()
        version.test = Text('test')

    def transform(self, text, filter):
        """Helper to call transform.
        """
        version = self.root.document.get_editable()
        request = TestRequest()
        factory = getMultiAdapter((version, request), ITransformerFactory)
        self.assertTrue(verifyObject(ITransformerFactory, factory))
        transformer = factory('test', version.test, text, filter)
        self.assertTrue(verifyObject(ITransformer, transformer))
        return unicode(transformer)

    def test_paragraph(self):
        """On input, text stays unmodified.
        """
        intern_format = self.transform(
            "<p>Simple text<i>Italic</i></p>",
            ISaveEditorFilter)
        self.assertXMLEqual(
            intern_format,
            "<p>Simple text<i>Italic</i></p>")

        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        self.assertXMLEqual(
            extern_format,
            "<p>Simple text<i>Italic</i></p>")

    def test_div(self):
        """On input, div stays unchanged.
        """
        intern_format = self.transform(
            "<div><p>Simple text</p><p>Other text</p></div>",
            ISaveEditorFilter)
        self.assertXMLEqual(
            intern_format,
            "<div><p>Simple text</p><p>Other text</p></div>")

        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        self.assertXMLEqual(
            extern_format,
            "<div><p>Simple text</p><p>Other text</p></div>")

    def test_multiple_root_element(self):
        """On input, mutliple root elements stays unchanged.
        """
        intern_format = self.transform(
            "<div><p>Simple text</p><p>Other text</p></div><p>Last</p>",
            ISaveEditorFilter)
        self.assertXMLEqual(
            intern_format,
            "<div><p>Simple text</p><p>Other text</p></div><p>Last</p>")

        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        self.assertXMLEqual(
            extern_format,
            "<div><p>Simple text</p><p>Other text</p></div><p>Last</p>")

    def test_new_anchor(self):
        """On input, anchors are collected, and the HTML stays the same.
        """
        version = self.root.document.get_editable()
        index = ITextIndexEntries(version.test)
        self.assertTrue(verifyObject(ITextIndexEntries, index))
        self.assertEqual(len(index.entries), 0)

        intern_format = self.transform(
            """
<p>
   <a class="anchor" name="simple" title="Simple Anchor">Simple Anchor</a>
   The ultimate store of the anchors.

   <a class="anchor" name="advanced" title="Advanced Anchor">Advanced Anchor</a>

</p>
""",
            ISaveEditorFilter)
        self.assertXMLEqual(
            intern_format,
"""
<p>
   <a class="anchor" name="simple" title="Simple Anchor">Simple Anchor</a>
   The ultimate store of the anchors.

   <a class="anchor" name="advanced" title="Advanced Anchor">Advanced Anchor</a>
</p>
""")

        index = ITextIndexEntries(version.test)
        self.assertEqual(len(index.entries), 2)
        self.assertEqual(index.entries[0].anchor, u'simple')
        self.assertEqual(index.entries[0].title, u'Simple Anchor')
        self.assertEqual(index.entries[1].anchor, u'advanced')
        self.assertEqual(index.entries[1].title, u'Advanced Anchor')

        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        self.assertXMLEqual(
            extern_format,
            """
<p>
   <a class="anchor" name="simple" title="Simple Anchor">Simple Anchor</a>
   The ultimate store of the anchors.

   <a class="anchor" name="advanced" title="Advanced Anchor">Advanced Anchor</a>
</p>
""")

    def test_edit_anchor(self):
        """On input, unused anchors are removed.
        """
        version = self.root.document.get_editable()
        index = ITextIndexEntries(version.test)
        index.add(u'simple', u'Simple Anchor')
        index.add(u'useless', u'Useless Anchor')
        index.add(u'really_useless', u'Really Useless Anchor')
        self.assertTrue(verifyObject(ITextIndexEntries, index))
        self.assertEqual(len(index.entries), 3)

        intern_format = self.transform(
            """
<p>
   <a class="anchor" name="simple" title="Simple Anchor">Simple Anchor</a>
   The ultimate survivor.
</p>
""",
            ISaveEditorFilter)
        self.assertXMLEqual(
            intern_format,
"""
<p>
   <a class="anchor" name="simple" title="Simple Anchor">Simple Anchor</a>
   The ultimate survivor.
</p>
""")

        index = ITextIndexEntries(version.test)
        self.assertEqual(len(index.entries), 1)
        self.assertEqual(index.entries[0].anchor, u'simple')
        self.assertEqual(index.entries[0].title, u'Simple Anchor')

        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        self.assertXMLEqual(
            extern_format,
            """
<p>
   <a class="anchor" name="simple" title="Simple Anchor">Simple Anchor</a>
   The ultimate survivor.
</p>
""")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InputTransformTestCase))
    return suite
