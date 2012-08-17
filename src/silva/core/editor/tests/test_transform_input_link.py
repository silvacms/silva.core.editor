# -*- coding: utf-8 -*-
# Copyright (c) 2011-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Acquisition import aq_chain
from Products.Silva.testing import TestCase, TestRequest

from zope.component import getMultiAdapter, getUtility

from silva.core.references.reference import get_content_id
from silva.core.references.interfaces import IReferenceService

from ..testing import FunctionalLayer
from ..text import Text
from ..transform.interfaces import IInputEditorFilter, ISaveEditorFilter
from ..transform.interfaces import ITransformerFactory


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
        transformer = factory('test', version.test, text, filter)
        return unicode(transformer)

    def test_external_link(self):
        """On input, an external link is slightly modified.
        """
        intern_format = self.transform(
            """
<p>
   <a class="link"
      href="javascript:void()"
      title="Silva"
      data-silva-url="http://infrae.com/products/silva">
      <i>To Silva</i></a>
</p>
""", ISaveEditorFilter)

        self.assertXMLEqual(
            intern_format,
"""
<p>
   <a class="link"
       title="Silva"
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
      title="Silva"
      href="javascript:void()"
      data-silva-url="http://infrae.com/products/silva">
      <i>To Silva</i></a>
</p>
""")

    def test_anchor_link(self):
        """On input, an external link is slightly modified.
        """
        intern_format = self.transform(
            """
<p>
   <a class="link"
      href="javascript:void()"
      target="_blank"
      data-silva-anchor="bar">
      <b>To the nearest local bar</b></a>
</p>
""", ISaveEditorFilter)

        self.assertXMLEqual(
            intern_format,
"""
<p>
   <a class="link"
      target="_blank"
      anchor="bar"><b>To the nearest local bar</b></a>
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
      target="_blank"
      data-silva-anchor="bar"
      href="javascript:void()">
      <b>To the nearest local bar</b></a>
</p>
""")

    def test_new_reference_link(self):
        """On input, a new link creates a new reference.
        """
        version = self.root.document.get_editable()
        service = getUtility(IReferenceService)
        target_id = get_content_id(self.root.target)
        # By default the document as no reference
        self.assertEqual(list(service.get_references_from(version)), [])

        intern_format = self.transform(
            """
<p>
   <a class="link"
      href="javascript:void()"
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

    def test_edit_reference_link_with_anchor(self):
        """On input, a existing link sees its reference updated.
        """
        version = self.root.document.get_editable()
        service = getUtility(IReferenceService)
        reference = service.new_reference(version, name=u"test link")
        reference.set_target(self.root.other)
        reference.add_tag(u"original-link-id")
        target_id = get_content_id(self.root.target)
        # So we have a reference, the one we will edit
        self.assertEqual(list(service.get_references_from(version)), [reference])

        intern_format = self.transform(
            """
<p>
   <a class="link"
      data-silva-reference="original-link-id"
      data-silva-anchor="world"
      data-silva-target="%s">Access the world</a>
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
        self.assertEqual(reference.tags, [u'test link', u'original-link-id'])

        # And the HTML is changed
        self.assertXMLEqual(
            intern_format,
"""
<p>
   <a class="link"
      reference="original-link-id"
      anchor="world">Access the world</a>
</p>
""")

        # Now we can rerender this for the editor
        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        self.assertXMLEqual(
            extern_format,
            """
<p>
   <a class="link"
      data-silva-reference="original-link-id"
      data-silva-target="%s"
      data-silva-anchor="world"
      href="javascript:void()">
      Access the world</a>
</p>
""" % (target_id))

    def test_delete_reference_link(self):
        """On input, any existing references matching a delete link is
        removed.
        """
        version = self.root.document.get_editable()
        service = getUtility(IReferenceService)
        reference = service.new_reference(version, name=u"test link")
        reference.set_target(self.root.other)
        reference.add_tag(u"original-link-id")
        # So we have a reference, the one we will edit
        self.assertEqual(list(service.get_references_from(version)), [reference])

        intern_format = self.transform(
            """
<p>
    <b>In the past, there was a wonderful link.</b>
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
    <b>In the past, there was a wonderful link.</b>
</p>
""")

        # Nope, still gone.
        self.assertEqual(list(service.get_references_from(version)), [])

    def test_copy_reference_link(self):
        """On input, if a link is copied, a new reference is created
        for the copy.
        """
        version = self.root.document.get_editable()
        service = getUtility(IReferenceService)
        reference = service.new_reference(version, name=u"test link")
        reference.set_target(self.root.other)
        reference.add_tag(u"original-link-id")
        target_id = get_content_id(self.root.target)
        # So we have a reference, the one we will edit
        self.assertEqual(list(service.get_references_from(version)), [reference])

        intern_format = self.transform(
            """
<p>
   <a class="link"
      data-silva-reference="original-link-id"
      data-silva-anchor="world"
      data-silva-target="%s">Access the world</a>
   <a class="link"
      href="javascript:void()"
      data-silva-reference="original-link-id"
      data-silva-target="%s">Other part of the world</a>
</p>
""" % (target_id, target_id),
            ISaveEditorFilter)

        # After transformation an extra reference is created to target
        references = list(service.get_references_from(version))
        self.assertEqual(len(references), 2)
        reference_name = None
        for reference in references:
            self.assertEqual(reference.source, version)
            self.assertEqual(aq_chain(reference.source), aq_chain(version))
            self.assertEqual(reference.target, self.root.target)
            self.assertEqual(aq_chain(reference.target), aq_chain(self.root.target))
            self.assertEqual(len(reference.tags), 2)
            if reference.tags[1] != u'original-link-id':
                reference_name = reference.tags[1]
            self.assertEqual(reference.tags[0], u'test link')


        # Now we can rerender this for the editor
        extern_format = self.transform(
            intern_format,
            IInputEditorFilter)
        self.assertXMLEqual(
            extern_format,
            """
<p>
   <a class="link"
      data-silva-reference="original-link-id"
      data-silva-target="%s"
      data-silva-anchor="world"
      href="javascript:void()">Access the world</a>
   <a class="link"
      data-silva-reference="%s"
      data-silva-target="%s"
      href="javascript:void()">Other part of the world</a>
</p>
""" % (target_id, reference_name, target_id))



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InputTransformTestCase))
    return suite
