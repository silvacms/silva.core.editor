# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.testing import TestRequest, tests

from five import grok
from zope.interface.verify import verifyObject
from zope.component import getMultiAdapter

from ..interfaces import ITextIndexEntries
from ..testing import FunctionalLayer
from ..text import Text
from ..transform.interfaces import IInputEditorFilter, ISaveEditorFilter
from ..transform.interfaces import ITransformer, ITransformerFactory
from ..transform.interfaces import ITransformationFilter


class InputTransformTestCase(unittest.TestCase):
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

    def test_input_editor_filters(self):
        """Test that there are default input editor filters, and they
        implement the proper API.
        """
        version = self.root.document.get_editable()
        transformers = grok.queryOrderedMultiSubscriptions(
            (version, TestRequest()), IInputEditorFilter)
        self.assertNotEqual(len(transformers), 0)
        for transformer in transformers:
            self.assertTrue(verifyObject(ITransformationFilter, transformer))

    def test_save_editor_filters(self):
        """Test that there are default input editor filters, and they
        implement the proper API.
        """
        version = self.root.document.get_editable()
        transformers = grok.queryOrderedMultiSubscriptions(
            (version, TestRequest()), ISaveEditorFilter)
        self.assertNotEqual(len(transformers), 0)
        for transformer in transformers:
            self.assertTrue(verifyObject(ITransformationFilter, transformer))

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
        tests.assertXMLEqual(
            intern_format,
            "<p>Simple text<i>Italic</i></p>")

        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        tests.assertXMLEqual(
            extern_format,
            "<p>Simple text<i>Italic</i></p>")

    def test_paragraph_windows_lines(self):
        """Windows new lines stays windows new lines (LXML bug).
        """
        intern_format = self.transform(
            u"<p><i>Italic</i>.\r\n\tReally dude</p>\r\n\t<p>Énd</p>\r\n",
            ISaveEditorFilter)
        tests.assertStringEqual(
            intern_format,
            u"<p><i>Italic</i>.\r\n\tReally dude</p>\r\n\t<p>&#201;nd</p>\r\n")

    def test_div(self):
        """On input, div stays unchanged.
        """
        intern_format = self.transform(
            "<div><p>Simple text</p><p>Other text</p></div>",
            ISaveEditorFilter)
        tests.assertXMLEqual(
            intern_format,
            "<div><p>Simple text</p><p>Other text</p></div>")

        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        tests.assertXMLEqual(
            extern_format,
            "<div><p>Simple text</p><p>Other text</p></div>")

    def test_multiple_root_element(self):
        """On input, mutliple root elements stays unchanged.
        """
        intern_format = self.transform(
            "<div><p>Simple text</p><p>Other text</p></div><p>Last</p>",
            ISaveEditorFilter)
        tests.assertXMLEqual(
            intern_format,
            "<div><p>Simple text</p><p>Other text</p></div><p>Last</p>")

        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        tests.assertXMLEqual(
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
   <a class="anchor" name="simple" title="Simple Anchor" href="javascript:void(0)">
     Simple Anchor
   </a>
   The ultimate store of the anchors.

   <a class="anchor" name="advanced" title="Advanced Anchor">Advanced Anchor</a>

</p>
""",
            ISaveEditorFilter)
        tests.assertXMLEqual(
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
        tests.assertXMLEqual(
            extern_format,
            """
<p>
   <a class="anchor" name="simple" title="Simple Anchor">
      Simple Anchor
   </a>
   The ultimate store of the anchors.

   <a class="anchor" name="advanced" title="Advanced Anchor">
      Advanced Anchor
   </a>
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
        tests.assertXMLEqual(
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
        tests.assertXMLEqual(
            extern_format,
            """
<p>
   <a class="anchor" name="simple" title="Simple Anchor">
      Simple Anchor
   </a>
   The ultimate survivor.
</p>
""")

    def test_empty_anchor(self):
        """On input, empty anchors are not collected.
        """
        version = self.root.document.get_editable()
        index = ITextIndexEntries(version.test)
        self.assertTrue(verifyObject(ITextIndexEntries, index))
        self.assertEqual(len(index.entries), 0)

        intern_format = self.transform(
            """
<p>
   <a class="anchor" name="missing" href="javascript:void(0)">Missing Title</a>
   The ultimate store of the anchors.
   <a class="anchor" name="empty" title="">Empty Title</a>
   <a class="anchor" name="space" title=" ">Title with a space</a>
</p>
""",
            ISaveEditorFilter)
        tests.assertXMLEqual(
            intern_format,
"""
<p>
   <a class="anchor" name="missing">Missing Title</a>
   The ultimate store of the anchors.
   <a class="anchor" name="empty" title="">Empty Title</a>
   <a class="anchor" name="space" title="">Title with a space</a>
</p>
""")

        index = ITextIndexEntries(version.test)
        self.assertEqual(len(index.entries), 0)

        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        tests.assertXMLEqual(
            extern_format,
            """
<p>
   <a class="anchor" name="missing">Missing Title</a>
   The ultimate store of the anchors.
   <a class="anchor" name="empty" title="">
     Empty Title
   </a>
   <a class="anchor" name="space" title="">
     Title with a space
   </a>
</p>
""")

    def test_sanitize_input(self):
        html = """
<p>
    <script type="text/javascript">
        function hello() {
            alert('hello');
        }
    </script>
    <a class="anchor" name="advanced" title="Advanced Anchor">Advanced <form><input type="submit" value="send" /></form>Anchor</a>
</p>
"""

        expected = """
<p>
    <a class="anchor" name="advanced" title="Advanced Anchor">Advanced Anchor</a>
</p>
"""
        sanitized = self.transform(html, ISaveEditorFilter)
        tests.assertXMLEqual(expected, sanitized)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InputTransformTestCase))
    return suite
