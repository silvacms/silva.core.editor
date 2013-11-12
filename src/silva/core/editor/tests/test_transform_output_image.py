# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.testing import TestCase
from Products.Silva.testing import TestRequest

from zope.component import getMultiAdapter


from ..testing import FunctionalLayer
from ..text import Text
from ..transform.interfaces import ISaveEditorFilter
from ..transform.interfaces import ITransformerFactory


class OutputTransformTestCase(TestCase):
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
        factory = getMultiAdapter((version, request), ITransformerFactory)
        transformer = factory('test', version.test, text, filter)
        return unicode(transformer)

    def test_link_in_caption(self):
        """ There should be no link wrapped around caption text.
        """
        editor_image_block = """
        <div class="image ">
            <a class="image-link"
               data-silva-anchor="Infrae"
               data-silva-url="http://infrae.com"
               target="_self"
               title="Silva 3.0 Documentation">
                   <img alt="IMAGE ALT TEXT" data-silva-url="http://infrae.com/contact/infrae_qr_vcard.png" />
            </a>
            <span class="image-caption">
                <a class="image-link"
                   data-silva-anchor="Infrae"
                   data-silva-url="http://infrae.com"
                   target="_self"
                   title="Silva 3.0 Documentation">THIS CAPTION TEXT IS WRAPPED IN A LINK, IT SHOULDN'T.
                </a>
            </span>
        </div>
        """

        actual_image_block = self.transform(editor_image_block,
                                            ISaveEditorFilter)

        expected_image_block = """
        <div class="image ">
            <a class="image-link"
               target="_self"
               title="Silva 3.0 Documentation"
               href="http://infrae.com"
               anchor="Infrae">
                <img alt="IMAGE ALT TEXT" src="http://infrae.com/contact/infrae_qr_vcard.png">
            </a>
            <span class="image-caption">THIS CAPTION TEXT IS WRAPPED IN A LINK, IT SHOULDN'T.</span>
        </div>
        """
        self.assertXMLEqual(expected_image_block, actual_image_block)

    def test_double_image_wrapper(self):
        """ The div image block (@class="image")
            shouldn't be nested in a div with the same class.
        """
        editor_image_block = """
        <div class="image ">
            <div class="image ">
                <a class="image-link"
                   data-silva-anchor="Infrae"
                   data-silva-url="http://infrae.com"
                   target="_self"
                   title="Silva 3.0 Documentation">
                       <img alt="IMAGE ALT TEXT" data-silva-url="http://infrae.com/contact/infrae_qr_vcard.png" />
                </a>
                <span class="image-caption">CAPTION</span>
            </div>
        </div>
        """

        actual_image_block = self.transform(editor_image_block,
                                            ISaveEditorFilter)

        expected_image_block = """
        <div class="image ">
            <a class="image-link"
               target="_self"
               title="Silva 3.0 Documentation"
               href="http://infrae.com"
               anchor="Infrae">
                <img alt="IMAGE ALT TEXT" src="http://infrae.com/contact/infrae_qr_vcard.png">
            </a>
            <span class="image-caption">CAPTION</span>
        </div>
        """
        self.assertXMLEqual(expected_image_block, actual_image_block)

    def test_multiple_links(self):
        """ Only one link is allowed inside an image block.
        """
        editor_image_block = """
            <div class="image ">
                <a class="image-link"
                   data-silva-anchor="Infrae"
                   data-silva-url="http://infrae.com"
                   target="_self"
                   title="Silva 3.0 Documentation">
                <a class="image-link"
                   data-silva-anchor="Infrae"
                   data-silva-url="http://infrae.com"
                   target="_self"
                   title="Silva 3.0 Documentation">
                <a class="image-link"
                   data-silva-anchor="Infrae"
                   data-silva-url="http://infrae.com"
                   target="_self"
                   title="Silva 3.0 Documentation">
                       <img alt="IMAGE ALT TEXT" data-silva-url="http://infrae.com/contact/infrae_qr_vcard.png" />
                </a>
                </a>
                </a>
                <a class="image-link"
                   data-silva-anchor="Infrae"
                   data-silva-url="http://infrae.com"
                   target="_self"
                   title="Silva 3.0 Documentation">
                <span class="image-caption">CAPTION</span>
                </a>
                <a class="image-link"
                   data-silva-anchor="Infrae"
                   data-silva-url="http://infrae.com"
                   target="_self"
                   title="Silva 3.0 Documentation">
                </a>
            </div>
        """

        actual_image_block = self.transform(editor_image_block,
                                            ISaveEditorFilter)

        expected_image_block = """
        <div class="image ">
            <a class="image-link"
               target="_self"
               title="Silva 3.0 Documentation"
               href="http://infrae.com"
               anchor="Infrae">
                <img alt="IMAGE ALT TEXT" src="http://infrae.com/contact/infrae_qr_vcard.png">
            </a>
            <span class="image-caption">CAPTION</span>
        </div>
        """
        self.assertXMLEqual(expected_image_block, actual_image_block)

    def test_multiple_images(self):
            """ Only one image is allowed inside an image block.
            """
            editor_image_block = """
            <div class="image ">
                <img alt="IMAGE ALT TEXT" data-silva-url="http://infrae.com/contact/infrae_qr_vcard.png" />
                    <a class="image-link"
                       data-silva-anchor="Infrae"
                       data-silva-url="http://infrae.com"
                       target="_self"
                       title="Silva 3.0 Documentation">
                           <img alt="IMAGE ALT TEXT" data-silva-url="http://infrae.com/contact/infrae_qr_vcard.png" />
                    </a>
                    <img alt="IMAGE ALT TEXT" data-silva-url="http://infrae.com/contact/infrae_qr_vcard.png" />
                    <span class="image-caption">CAPTION</span>
                    <img alt="IMAGE ALT TEXT" data-silva-url="http://infrae.com/contact/infrae_qr_vcard.png" />
                    <img alt="IMAGE ALT TEXT" data-silva-url="http://infrae.com/contact/infrae_qr_vcard.png" />
            </div>
            """

            actual_image_block = self.transform(editor_image_block,
                                                ISaveEditorFilter)

            expected_image_block = """
            <div class="image ">
                <img alt="IMAGE ALT TEXT" src="http://infrae.com/contact/infrae_qr_vcard.png">
                <span class="image-caption">CAPTION</span>
            </div>
            """
            self.assertXMLEqual(expected_image_block, actual_image_block)

    def test_nested_paragraphs(self):
            """ Only one <a>, one <img> and one <span> are allowed inside an image block.
            """
            editor_image_block = """
            <div class="image ">
                    <p>This P is nested inside the image block structure, it shouldn't be here.</p>
                    <a class="image-link"
                       data-silva-anchor="Infrae"
                       data-silva-url="http://infrae.com"
                       target="_self"
                       title="Silva 3.0 Documentation">
                           <img alt="IMAGE ALT TEXT" data-silva-url="http://infrae.com/contact/infrae_qr_vcard.png" />
                    </a>
                    <p>This P is nested inside the image block structure, it shouldn't be here.</p>
                    <span class="image-caption">CAPTION</span>
            </div>
            """

            actual_image_block = self.transform(editor_image_block,
                                                ISaveEditorFilter)

            expected_image_block = """
            <div class="image ">
                    <a class="image-link"
                       target="_self"
                       title="Silva 3.0 Documentation"
                       href="http://infrae.com"
                       anchor="Infrae">
                       <img alt="IMAGE ALT TEXT" src="http://infrae.com/contact/infrae_qr_vcard.png">
                    </a>
                <span class="image-caption">CAPTION</span>
            </div>
            """
            self.assertXMLEqual(expected_image_block, actual_image_block)

    def test_multiple_wrappers(self):
            """ There should be only one div image block wrapper.
            """
            editor_image_block = """
            <div class="image ">
                <div class="image "><div class="image "></div>
                <div class="image "><div class="image "><div class="image "></div></div>
                    <a class="image-link"
                       data-silva-anchor="Infrae"
                       data-silva-url="http://infrae.com"
                       target="_self"
                       title="Silva 3.0 Documentation">
                           <img alt="IMAGE ALT TEXT" data-silva-url="http://infrae.com/contact/infrae_qr_vcard.png" />
                           <div class="image "><img alt="IMAGE ALT TEXT" data-silva-url="http://infrae.com/contact/infrae_qr_vcard.png" /><div class="image "></div>
                    </a>
                </div>
            </div>
            """

            actual_image_block = self.transform(editor_image_block,
                                                ISaveEditorFilter)

            expected_image_block = """
            <div class="image ">
                    <a class="image-link"
                       target="_self"
                       title="Silva 3.0 Documentation"
                       href="http://infrae.com"
                       anchor="Infrae">
                       <img alt="IMAGE ALT TEXT" src="http://infrae.com/contact/infrae_qr_vcard.png">
                    </a>
            </div>
            """

            self.assertXMLEqual(expected_image_block, actual_image_block)

    def test_wrong_classes(self):
            """ Link inside image block should have 'image-link' class
                while caption span should have 'image-caption' class
            """
            editor_image_block = """
            <div class="image ">
                    <a class="wrong-class"
                       data-silva-anchor="Infrae"
                       data-silva-url="http://infrae.com"
                       target="_self"
                       title="Silva 3.0 Documentation">
                           <img alt="IMAGE ALT TEXT" data-silva-url="http://infrae.com/contact/infrae_qr_vcard.png" />
                    </a>
                    <span class="wrong-class">CAPTION</span>
            </div>
            """

            actual_image_block = self.transform(editor_image_block,
                                                ISaveEditorFilter)

            expected_image_block = """
            <div class="image ">
                    <a class="image-link"
                       target="_self"
                       title="Silva 3.0 Documentation"
                       href="http://infrae.com"
                       anchor="Infrae">
                       <img alt="IMAGE ALT TEXT" src="http://infrae.com/contact/infrae_qr_vcard.png">
                    </a>
                    <span class="image-caption">CAPTION</span>
            </div>
            """

            self.assertXMLEqual(expected_image_block, actual_image_block)

    def test_block_without_img(self):
            """ An image block without an image inside has to be removed.
            """
            editor_image_block = """
            <div class="image ">
                    <a class="wrong-class"
                       data-silva-anchor="Infrae"
                       data-silva-url="http://infrae.com"
                       target="_self"
                       title="Silva 3.0 Documentation">
                    </a>
                    <span class="wrong-class">CAPTION</span>
            </div>
            """

            actual_image_block = self.transform(editor_image_block,
                                                ISaveEditorFilter)

            expected_image_block = ""

            self.assertXMLEqual(expected_image_block, actual_image_block)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(OutputTransformTestCase))
    return suite
