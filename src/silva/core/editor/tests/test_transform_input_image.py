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
            image.seek(0)
            factory.manage_addImage('ultimate_chocobo', 'Ultimate Chocobo', image)

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

    def test_edit_reference_image(self):
        """On input, updated local images update their references.
        """
        version = self.root.document.get_editable()
        service = getUtility(IReferenceService)
        reference = service.new_reference(version, name=u"test image")
        reference.set_target(self.root.ultimate_chocobo)
        reference.add_tag(u"original-image-id")
        target_id = get_content_id(self.root.chocobo)
        # So we have a reference, the one we will edit
        self.assertEqual(list(service.get_references_from(version)), [reference])

        intern_format = self.transform(
            """
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img src="http://localhost/root/ultimate_chocobo"
         alt="image"
         data-silva-reference="original-image-id"
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
        self.assertEqual(reference.tags, [u'test image', u'original-image-id'])

        self.assertXMLEqual(
            intern_format,
"""
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img alt="image"
         reference="original-image-id" />
  </div>
</div>
""")

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
         data-silva-reference="original-image-id"
         data-silva-target="%s"
         src="http://localhost/root/chocobo"></img>
  </div>
</div>
""" % (target_id))

    def test_delete_reference_image(self):
        """On input, delete local images remove corresponding
        references.
        """
        version = self.root.document.get_editable()
        service = getUtility(IReferenceService)
        reference = service.new_reference(version, name=u"test image")
        reference.set_target(self.root.ultimate_chocobo)
        reference.add_tag(u"original-image-id")
        # So we have a reference, the one we will edit
        self.assertEqual(list(service.get_references_from(version)), [reference])
        intern_format = self.transform(
            """
<p>
    <b>In the past, there was a wonderful chocobo over here.</b>
</p>
""", ISaveEditorFilter)

        # The reference is gone now.
        self.assertEqual(list(service.get_references_from(version)), [])

        # Now we can rerender this for the editor
        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        self.assertXMLEqual(
            extern_format,
            """
<p>
    <b>In the past, there was a wonderful chocobo over here.</b>
</p>
""")

        # Nope, still gone.
        self.assertEqual(list(service.get_references_from(version)), [])

    def test_copy_reference_image(self):
        """On input, copy of local images create new references.
        """
        version = self.root.document.get_editable()
        service = getUtility(IReferenceService)
        reference = service.new_reference(version, name=u"test image")
        reference.set_target(self.root.ultimate_chocobo)
        reference.add_tag(u"original-image-id")
        target_id = get_content_id(self.root.chocobo)
        ultimate_target_id = get_content_id(self.root.ultimate_chocobo)
        # So we have a reference, the one we will edit
        self.assertEqual(list(service.get_references_from(version)), [reference])

        intern_format = self.transform(
            """
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img src="http://localhost/root/chocobo"
         data-silva-reference="original-image-id"
         data-silva-target="%s"></img>
  </div>
  <div class="image">
    <img src="http://localhost/root/ultimate_chocobo"
         alt="ultimate awesome"
         data-silva-reference="original-image-id"
         data-silva-target="%s"></img>
  </div>
</div>
""" % (target_id, ultimate_target_id), ISaveEditorFilter)

        # After transformation a reference is created to chocobo
        references = list(service.get_references_from(version))
        self.assertEqual(len(references), 2)
        reference_name = None
        for reference in references:
            self.assertEqual(reference.source, version)
            self.assertEqual(aq_chain(reference.source), aq_chain(version))
            self.assertEqual(len(reference.tags), 2)
            if reference.tags[1] != u'original-image-id':
                reference_name = reference.tags[1]
                self.assertEqual(reference.target, self.root.ultimate_chocobo)
                self.assertEqual(aq_chain(reference.target), aq_chain(self.root.ultimate_chocobo))
            else:
                self.assertEqual(reference.target, self.root.chocobo)
                self.assertEqual(aq_chain(reference.target), aq_chain(self.root.chocobo))
            self.assertEqual(reference.tags[0], u'test image')

        self.assertXMLEqual(
            intern_format,
"""
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img reference="original-image-id" />
  </div>
  <div class="image">
    <img alt="ultimate awesome"
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
    <img data-silva-reference="original-image-id"
         data-silva-target="%s"
         src="http://localhost/root/chocobo"></img>
  </div>
  <div class="image">
    <img alt="ultimate awesome"
         data-silva-reference="%s"
         data-silva-target="%s"
         src="http://localhost/root/ultimate_chocobo"></img>
  </div>
</div>
""" % (target_id, reference_name, ultimate_target_id))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InputTransformTestCase))
    return suite
