# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


import unittest

from Acquisition import aq_chain
from Products.Silva.testing import TestCase

from zope.component import getMultiAdapter, getUtility
from zope.publisher.browser import TestRequest

from silva.core.editor.testing import FunctionalLayer
from silva.core.editor.text import Text
from silva.core.editor.transform.interfaces import IInputEditorFilter
from silva.core.editor.transform.interfaces import ISaveEditorFilter
from silva.core.editor.transform.interfaces import ITransformer
from silva.core.references.reference import get_content_id
from silva.core.references.interfaces import IReferenceService


class InputTransformTestCase(TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', 'Document')
        factory.manage_addMockupVersionedContent('target', 'Document Target')

        version = self.root.document.get_editable()
        version.test = Text('test')

    def transform(self, text, filter):
        """Helper to call transform.
        """
        version = self.root.document.get_editable()
        request = TestRequest()
        transformer = getMultiAdapter((version, request), ITransformer)
        return transformer.data('test', version.test, text, filter)

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

    def test_new_external_link(self):
        """On input, an external link is slightly modified.
        """
        intern_format = self.transform(
            """
<p>
   <a class="link"
      href="http://somewhere.com"
      data-silva-href="http://infrae.com/products/silva">
      <i>To Silva</i></a>
</p>
""", ISaveEditorFilter)

        self.assertXMLEqual(
            intern_format,
"""
<p>
   <a class="link"
       href="http://infrae.com/products/silva"><i>To Silva</i></a>
</p>
""")

        # And changing it back to the editor format.
        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        self.assertXMLEqual(
            extern_format,
            """
<p>
   <a class="link"
      href="http://infrae.com/products/silva"
      data-silva-href="http://infrae.com/products/silva">
      <i>To Silva</i></a>
</p>
""")

    def test_new_reference_link(self):
        """On input, a new link is modified to a reference.
        """
        # At the begining the document as no reference
        target_id = get_content_id(self.root.target)
        version = self.root.document.get_editable()
        service = getUtility(IReferenceService)
        self.assertEqual(list(service.get_references_from(version)), [])

        intern_format = self.transform(
            """
<p>
   <a class="link"
      href="http://somewhere.com"
      data-silva-reference="new"
      data-silva-target="%s">To Target</a>
</p>
""" % (target_id),
            ISaveEditorFilter)

        # After transformation a reference is created to target
        references = list(service.get_references_from(version))
        self.assertEqual(len(references), 1)
        reference = references[0]
        self.assertEqual(reference.source, version)
        self.assertEqual(aq_chain(reference.source), aq_chain(version))
        self.assertEqual(reference.target, self.root.target)
        self.assertEqual(aq_chain(reference.target), aq_chain(self.root.target))
        self.assertEqual(len(reference.tags), 2)
        reference_name = reference.tags[1]
        self.assertEqual(reference.tags, [u'test link', reference_name])

        # And the HTML is changed
        self.assertXMLEqual(
            intern_format,
"""
<p>
   <a class="link"
      reference="%s">To Target</a>
</p>
""" % (reference_name))

        # Now we can rerender this for the editor
        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        self.assertXMLEqual(
            extern_format,
            """
<p>
   <a class="link"
      data-silva-reference="%s"
      data-silva-target="%s"
      href="javascript:void()">
      To Target</a>
</p>
""" % (reference_name, target_id))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InputTransformTestCase))
    return suite
