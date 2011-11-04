# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
import lxml

from zope.component import getUtility
from zope.publisher.browser import TestRequest
from silva.core.editor.transform.silvaxml import xmlexport
from silva.core.references.interfaces import IReferenceService
from silva.core.references.reference import get_content_id
from silva.core.editor.transform.silvaxml import NS_HTML_URI
from Products.Silva.tests.helpers import open_test_file
from Products.Silva.testing import FunctionalLayer
from Products.Silva.silvaxml.xmlexport import SilvaExportRoot
from Products.Silva.silvaxml.xmlexport import ExportSettings, ExportContext


class TestExport(unittest.TestCase):
    layer = FunctionalLayer
    html = """
<div>
  <h1>
    Example</h1>
  <p>
    here is a paragraph...</p>
  <p>
    then comes a <a class="link" target="_self"
    reference="93094ba8-70bd-11e0-b805-c42c0338b1a2">link</a></p>
  <p>
    then comes an image :</p>
  <div class="image default">
    <img alt="location.png"
    reference="a5c84b4a-70bd-11e0-8c0a-c42c0338b1a2">
    <span class="image-caption">location.png</span></div>
</div>
"""

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addMockupVersionedContent('example', 'Example')
        self.version = self.root.example.get_editable()

        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('other', 'Other')

        with open_test_file('content-listing.png', globals()) as image_file:
            factory.manage_addImage('image', 'Image', image_file)

        reference_service = getUtility(IReferenceService)
        reference = reference_service.get_reference(
            self.version, name=u"document link", add=True)
        reference.add_tag(u"93094ba8-70bd-11e0-b805-c42c0338b1a2")
        reference.set_target_id(get_content_id(self.root.folder.other))
        reference = reference_service.get_reference(
            self.version, name=u"document image", add=True)
        reference.add_tag(u"a5c84b4a-70bd-11e0-8c0a-c42c0338b1a2")
        reference.set_target_id(get_content_id(self.root.folder.image))

    def test_export_reference_filter(self):
        producer = SilvaExportRoot(self.root)
        producer.getSettings = lambda: ExportSettings()
        producer.getInfo = lambda: ExportContext(self.root, request=TestRequest())

        reference_filter = xmlexport.ReferenceExportTransformer(
            self.version, producer)
        tree = lxml.html.fromstring(self.html)
        xmlexport.XHTMLExportTransformer(self.version, producer)(tree)
        reference_filter(tree)

        def lookup(expression):
            results = tree.xpath(expression, namespaces={'html': NS_HTML_URI})
            self.assertEqual(len(results), 1)
            return results[0]

        link = lookup('//html:a[@class="link"][1]')
        image = lookup('//html:img[1]')

        self.assertEqual(link.attrib['reference'], 'root/folder/other')
        self.assertEqual(link.attrib['reference-type'], 'document link')
        self.assertEqual(image.attrib['reference'], 'root/folder/image')
        self.assertEqual(image.attrib['reference-type'], 'document image')

