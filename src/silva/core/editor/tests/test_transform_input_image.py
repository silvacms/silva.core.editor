# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Acquisition import aq_chain
from Products.Silva.testing import TestCase
from Products.Silva.testing import TestRequest

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

        with self.layer.open_fixture('chocobo.png') as image:
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
        factory = getMultiAdapter((version, request), ITransformerFactory)
        transformer = factory('test', version.test, text, filter)
        return unicode(transformer)

    def test_external_image(self):
        """External images are untouched.
        """
        intern_format = self.transform(
            """
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img src="http://infrae.com/image.jpg"
         data-silva-url="http://infrae.com/image.jpg"></img>
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
         data-silva-url="http://infrae.com/image.jpg" />
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
         data-silva-resolution="hires"
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
         reference="%s"
         resolution="hires" />
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
         data-silva-resolution="hires"
         data-silva-reference="%s"
         data-silva-target="%s"
         src="http://localhost/root/chocobo"></img>
  </div>
</div>
""" % (reference_name, target_id))

    def test_edit_broken_reference_image(self):
        """On input, broken references for images are replaced with a
        broken logo. The reference 0 is used to identify them.
        """

        version = self.root.document.get_editable()
        service = getUtility(IReferenceService)
        reference = service.new_reference(version, name=u"test image")
        reference.add_tag(u"original-image-id")
        # Reference target is not set.

        # Now if we display this in the editor we get a broken image:
        intern_format = """
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img alt="image"
         reference="original-image-id" />
  </div>
</div>
"""
        extern_format = self.transform(intern_format, IInputEditorFilter)
        self.assertXMLEqual(
            extern_format, """
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img alt="image"
         data-silva-reference="original-image-id"
         data-silva-target="0"
         src="./++static++/silva.core.editor/broken-link.jpg"></img>
  </div>
</div>
""")

        # Now if we save it, we get back the original format. The
        # reference is preserved.
        saved_format = self.transform(extern_format, ISaveEditorFilter)
        saved_references = list(service.get_references_from(version))
        self.assertEqual(len(saved_references), 1)
        saved_reference = saved_references[0]
        self.assertEqual(saved_reference.source, version)
        self.assertIs(saved_reference.target, None)
        self.assertEqual(
            saved_reference.tags,
            [u"test image", u"original-image-id"])
        self.assertXMLEqual(
            saved_format, """
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img alt="image"
         reference="original-image-id" />
  </div>
</div>
""")

    def test_edit_invalid_reference_image(self):
        """On input, images that doesn't point to an includable image
        content uses a broken logo as image source (but the reference
        is kept).
        """
        with self.layer.open_fixture('chocobo.png') as stream:
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFile('peco', 'Peco Peco', stream)
            factory.manage_addGhostAsset('image', None, haunted=self.root.peco)

        version = self.root.document.get_editable()
        service = getUtility(IReferenceService)
        reference = service.new_reference(version, name=u"test image")
        reference.set_target(self.root.image)
        reference.add_tag(u"original-image-id")
        target_id = get_content_id(self.root.image)

        # Now if we display this in the editor we get a broken image:
        self.assertXMLEqual(
            self.transform("""
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img alt="image"
         reference="original-image-id" />
  </div>
</div>
""", IInputEditorFilter), """
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img alt="image"
         data-silva-reference="original-image-id"
         data-silva-target="%s"
         src="./++static++/silva.core.editor/broken-link.jpg"></img>
  </div>
</div>
""" % (target_id))

        # If you fix the ghost to an image, everything works:
        reference.set_target(self.root.chocobo)
        target_id = get_content_id(self.root.chocobo)
        self.assertXMLEqual(
            self.transform("""
<div>
  <p>Some description about the world</p>
  <div class="image">
    <img alt="image"
         reference="original-image-id" />
  </div>
</div>
""", IInputEditorFilter), """
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
        self.assertEqual(
            list(service.get_references_from(version)),
            [reference])

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
        self.assertEqual(
            list(service.get_references_from(version)),
            [reference])
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
        self.assertEqual(
            list(service.get_references_from(version)),
            [reference])

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
                self.assertEqual(reference_name, None)
                reference_name = reference.tags[1]
                self.assertEqual(reference.target, self.root.ultimate_chocobo)
                self.assertEqual(
                    aq_chain(reference.target),
                    aq_chain(self.root.ultimate_chocobo))
            else:
                self.assertEqual(reference.target, self.root.chocobo)
                self.assertEqual(
                    aq_chain(reference.target),
                    aq_chain(self.root.chocobo))
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

    def test_new_reference_image_link(self):
        """On input, images with link are converted to references
        (both of them).
        """
        version = self.root.document.get_editable()
        service = getUtility(IReferenceService)
        document_target_id = get_content_id(self.root.target)
        image_target_id = get_content_id(self.root.chocobo)
        # By default the document as no reference
        self.assertEqual(list(service.get_references_from(version)), [])

        intern_format = self.transform(
            """
<div>
  <p>Some description about the world</p>
  <div class="image">
    <a class="image-link"
       data-silva-reference="new"
       data-silva-target="%s">
      <img src="http://localhost/root/chocobo"
           alt="image"
           data-silva-reference="new"
           data-silva-target="%s"></img>
    </a>
  </div>
</div>
""" % (document_target_id, image_target_id), ISaveEditorFilter)

        # After transformation a reference is created to chocobo
        references = list(service.get_references_from(version))
        self.assertEqual(len(references), 2)
        document_reference_name = None
        image_reference_name = None
        for reference in references:
            self.assertEqual(reference.source, version)
            self.assertEqual(aq_chain(reference.source), aq_chain(version))
            self.assertEqual(len(reference.tags), 2)
            if reference.tags[0] == u'test image':
                self.assertEqual(image_reference_name, None)
                self.assertEqual(reference.target, self.root.chocobo)
                self.assertEqual(
                    aq_chain(reference.target),
                    aq_chain(self.root.chocobo))
                image_reference_name = reference.tags[1]
            else:
                self.assertEqual(document_reference_name, None)
                self.assertEqual(reference.target, self.root.target)
                self.assertEqual(
                    aq_chain(reference.target),
                    aq_chain(self.root.target))
                document_reference_name = reference.tags[1]
                self.assertEqual(reference.tags[0], u'test image link')

        self.assertXMLEqual(
            intern_format,
"""
<div>
  <p>Some description about the world</p>
  <div class="image">
    <a class="image-link"
       reference="%s">
      <img alt="image"
           reference="%s" />
    </a>
  </div>
</div>
""" % (document_reference_name, image_reference_name))

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
    <a class="image-link"
       data-silva-reference="%s"
       data-silva-target="%s"
       href="javascript:void(0)">
      <img alt="image"
           data-silva-reference="%s"
           data-silva-target="%s"
           src="http://localhost/root/chocobo"></img>
    </a>
  </div>
</div>
""" % (document_reference_name, document_target_id,
       image_reference_name, image_target_id))

    def test_new_reference_image_link_hires(self):
        """On input, images with link are converted to references
        (both of them). Hires can be provided using the query option.
        """
        version = self.root.document.get_editable()
        service = getUtility(IReferenceService)
        document_target_id = get_content_id(self.root.target)
        image_target_id = get_content_id(self.root.chocobo)
        # By default the document as no reference
        self.assertEqual(list(service.get_references_from(version)), [])

        intern_format = self.transform(
            """
<div>
  <p>Some description about the world</p>
  <div class="image">
    <a class="image-link"
       data-silva-reference="new"
       data-silva-target="%s"
       data-silva-query="hires">
      <img src="http://localhost/root/chocobo"
           alt="image"
           data-silva-reference="new"
           data-silva-target="%s"></img>
    </a>
  </div>
</div>
""" % (document_target_id, image_target_id), ISaveEditorFilter)

        # After transformation a reference is created to chocobo
        references = list(service.get_references_from(version))
        self.assertEqual(len(references), 2)
        document_reference_name = None
        image_reference_name = None
        for reference in references:
            self.assertEqual(reference.source, version)
            self.assertEqual(aq_chain(reference.source), aq_chain(version))
            self.assertEqual(len(reference.tags), 2)
            if reference.tags[0] == u'test image':
                self.assertEqual(image_reference_name, None)
                self.assertEqual(reference.target, self.root.chocobo)
                self.assertEqual(
                    aq_chain(reference.target),
                    aq_chain(self.root.chocobo))
                image_reference_name = reference.tags[1]
            else:
                self.assertEqual(document_reference_name, None)
                self.assertEqual(reference.target, self.root.target)
                self.assertEqual(
                    aq_chain(reference.target),
                    aq_chain(self.root.target))
                document_reference_name = reference.tags[1]
                self.assertEqual(reference.tags[0], u'test image link')

        self.assertXMLEqual(
            intern_format,
"""
<div>
  <p>Some description about the world</p>
  <div class="image">
    <a class="image-link"
       reference="%s"
       query="hires">
      <img alt="image"
           reference="%s" />
    </a>
  </div>
</div>
""" % (document_reference_name, image_reference_name))

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
    <a class="image-link"
       data-silva-reference="%s"
       data-silva-target="%s"
       data-silva-query="hires"
       href="javascript:void(0)">
      <img alt="image"
           data-silva-reference="%s"
           data-silva-target="%s"
           src="http://localhost/root/chocobo"></img>
    </a>
  </div>
</div>
""" % (document_reference_name, document_target_id,
       image_reference_name, image_target_id))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InputTransformTestCase))
    return suite
