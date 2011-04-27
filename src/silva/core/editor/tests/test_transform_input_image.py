# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Acquisition import aq_chain
from Products.Silva.testing import TestCase
from Products.Silva.tests.helpers import open_test_file

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

        with open_test_file('chocobo.png', globals()) as image:
            factory.manage_addImage('chocobo', 'Chocobo', image)

        version = self.root.document.get_editable()
        version.test = Text('test')

    def transform(self, text, filter):
        """Helper to call transform.
        """
        version = self.root.document.get_editable()
        request = TestRequest()
        transformer = getMultiAdapter((version, request), ITransformer)
        return transformer.data('test', version.test, text, filter)

    def test_external_image(self):
        """External images are untouched.
        """
        intern_format = self.transform(
            """
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img src="http://infrae.com/image.jpg"
         data-silva-src="http://infrae.com/image.jpg"></img>
  </div>
</div>
""", ISaveEditorFilter)

        self.assertXMLEqual(
            intern_format,
"""
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img src="http://infrae.com/image.jpg" />
  </div>
</div>
""")

        # And changing it back to the editor format.
        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        self.assertXMLEqual(
            extern_format,
            """
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img src="http://infrae.com/image.jpg"
         data-silva-src="http://infrae.com/image.jpg" />
  </div>
</div>
""")

    def test_new_reference_image(self):
        """On input, local images are transformed to references.
        """
        version = self.root.document.get_editable()
        service = getUtility(IReferenceService)
        target_id = get_content_id(self.root.chocobo)
        # By default the document as no reference
        self.assertEqual(list(service.get_references_from(version)), [])

        intern_format = self.transform(
            """
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img src="http://localhost/root/chocobo"
         alt="image"
         data-silva-reference="new"
         data-silva-target="%s"></img>
  </div>
</div>
""" % (target_id), ISaveEditorFilter)

        # After transformation a reference is created to chocobo
        references = list(service.get_references_from(version))
        self.assertEqual(len(references), 1)
        reference = references[0]
        self.assertEqual(reference.source, version)
        self.assertEqual(aq_chain(reference.source), aq_chain(version))
        self.assertEqual(reference.target, self.root.chocobo)
        self.assertEqual(aq_chain(reference.target), aq_chain(self.root.chocobo))
        self.assertEqual(len(reference.tags), 2)
        reference_name = reference.tags[1]
        self.assertEqual(reference.tags, [u'test image', reference_name])

        self.assertXMLEqual(
            intern_format,
"""
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img alt="image"
         reference="%s" />
  </div>
</div>
""" % (reference_name))

        # Now we can rerender this for the editor
        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        self.assertXMLEqual(
            extern_format,
            """
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img alt="image"
         data-silva-reference="%s"
         data-silva-target="%s"
         src="http://localhost/root/chocobo"></img>
  </div>
</div>
""" % (reference_name, target_id))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InputTransformTestCase))
    return suite
