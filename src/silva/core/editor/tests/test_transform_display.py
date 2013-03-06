# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from five import grok
from zope.interface.verify import verifyObject
from zope.component import getMultiAdapter

from Products.Silva.testing import TestRequest, tests

from ..testing import FunctionalLayer, save_editor_text
from ..text import Text
from ..transform.interfaces import ITransformationFilter, IDisplayFilter
from ..transform.interfaces import ITransformerFactory


class DisplayTransformTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', 'Document')
        factory.manage_addMockupVersionedContent('other', 'Other document')
        with self.layer.open_fixture('chocobo.png') as image:
            factory.manage_addImage('chocobo', 'Chocobo', image)

        version = self.root.document.get_editable()
        version.test = Text('test')

    def test_display_filters(self):
        """Test that there are default display filters, and they
        implement the proper API.
        """
        version = self.root.document.get_editable()
        transformers = grok.queryOrderedMultiSubscriptions(
            (version, TestRequest()), IDisplayFilter)
        self.assertNotEqual(len(transformers), 0)
        for transformer in transformers:
            self.assertTrue(verifyObject(ITransformationFilter, transformer))

    def test_self_closing_tags(self):
        version = self.root.document.get_editable()
        save_editor_text(version.test, """
<h2>This is simple piece of text</h2>
<p>That contains <br>a paragraph.</p>
""")

        factory = getMultiAdapter((version, TestRequest()), ITransformerFactory)
        transformer = factory(
            'test', version.test, unicode(version.test), IDisplayFilter)
        tests.assertXMLEqual(
            unicode(transformer),
            u"""
<h2>This is simple piece of text</h2>
<p>That contains <br>a paragraph.</p>""")

    def test_render(self):
        """Render a simple piece of text for the public.
        """
        version = self.root.document.get_editable()
        save_editor_text(version.test, """
<h2>This is simple piece of text</h2>
<p>That contains a paragraph.</p>
""")

        factory = getMultiAdapter((version, TestRequest()), ITransformerFactory)
        transformer = factory(
            'test', version.test, unicode(version.test), IDisplayFilter)
        tests.assertXMLEqual(
            unicode(transformer),
            u"""
<h2>This is simple piece of text</h2>
<p>That contains a paragraph.</p>""")

    def test_render_reference_link_with_anchor(self):
        """Test render a piece of text with a link that is a reference
        to an another content in Silva, with an extra anchor.
        """
        version = self.root.document.get_editable()
        save_editor_text(
            version.test, u"""
<h2>This is simple piece of text</h2>
<p>
   This simple piece of text contains a simple piece of link:
   <a class="link" target="_self" reference="{link}" anchor="top">paragraph</a>.
</p>""",
            content=version,
            link_content=self.root.other,
            link_name=u'test link')

        factory = getMultiAdapter((version, TestRequest()), ITransformerFactory)
        transformer = factory(
            'test', version.test, unicode(version.test), IDisplayFilter)
        tests.assertXMLEqual(
            unicode(transformer),
            u"""
<h2>This is simple piece of text</h2>
<p>
  This simple piece of text contains a simple piece of link:
  <a class="link" target="_self" href="http://localhost/root/other#top">
    paragraph
  </a>.
</p>""")

    def test_render_external_link_with_anchor(self):
        """Test render a piece of text with a link that is an external
        URL with an extra anchor.
        """
        version = self.root.document.get_editable()
        save_editor_text(
            version.test, u"""
<h2>This is simple piece of text</h2>
<p>
  This simple piece of text contains a simple piece of link:
  <a class="link" href="http://infrae.com" anchor="top">paragraph</a>.
</p>""")

        factory = getMultiAdapter((version, TestRequest()), ITransformerFactory)
        transformer = factory(
            'test', version.test, unicode(version.test), IDisplayFilter)
        tests.assertXMLEqual(
            unicode(transformer),
            u"""
<h2>This is simple piece of text</h2>
<p>
  This simple piece of text contains a simple piece of link:
  <a class="link" href="http://infrae.com#top">paragraph</a>.
</p>""")

    def test_render_anchor_link(self):
        """Test render a piece of text with a link that is just
        refering an anchor on the same page.
        """
        version = self.root.document.get_editable()
        save_editor_text(
            version.test, u"""
<h2>This is simple piece of text</h2>
<p>
  This simple piece of text contains a simple piece of link:
  <a class="link" target="_self" anchor="top">paragraph</a>.
</p>""")

        factory = getMultiAdapter((version, TestRequest()), ITransformerFactory)
        transformer = factory(
            'test', version.test, unicode(version.test), IDisplayFilter)
        tests.assertXMLEqual(
            unicode(transformer),
            u"""
<h2>This is simple piece of text</h2>
<p>
  This simple piece of text contains a simple piece of link:
  <a class="link" target="_self" href="#top">paragraph</a>.
</p>""")

    def test_render_image(self):
        """Test render a piece of text with an image that is refering
        an asset in Silva.
        """
        version = self.root.document.get_editable()
        save_editor_text(
            version.test, u"""
<h2>This is simple piece of text</h2>
<p>
  This simple piece of text contains a magic chocobo:
</p>
<div class="image">
  <img alt="Chocobo" reference="{image}" />
</div>""",
            content=version,
            image_content=self.root.chocobo,
            image_name=u'test image')

        factory = getMultiAdapter((version, TestRequest()), ITransformerFactory)
        transformer = factory(
            'test', version.test, unicode(version.test), IDisplayFilter)
        tests.assertXMLEqual(
            unicode(transformer),
            u"""
<h2>This is simple piece of text</h2>
<p>
  This simple piece of text contains a magic chocobo:
</p>
<div class="image">
  <img alt="Chocobo" height="256" width="256"
       src="http://localhost/root/chocobo" />
</div>""")

    def test_render_image_resolution(self):
        """Test render a piece of text with an image that is refering
        an asset in Silva.
        """
        version = self.root.document.get_editable()
        save_editor_text(
            version.test, u"""
<h2>This is simple piece of text</h2>
<p>
  This simple piece of text contains a magic chocobo:
</p>
<div class="image">
  <img alt="Chocobo" resolution="thumbnail" reference="{image}" />
</div>""",
            content=version,
            image_content=self.root.chocobo,
            image_name=u'test image')

        factory = getMultiAdapter((version, TestRequest()), ITransformerFactory)
        transformer = factory(
            'test', version.test, unicode(version.test), IDisplayFilter)
        tests.assertXMLEqual(
            unicode(transformer),
            u"""
<h2>This is simple piece of text</h2>
<p>
  This simple piece of text contains a magic chocobo:
</p>
<div class="image">
  <img alt="Chocobo" height="120" width="120"
       src="http://localhost/root/chocobo?thumbnail" />
</div>""")

    def test_render_image_with_internal_link_and_anchor(self):
        """Test render a piece of text with an image that is referring
        an asset in Silva, and with a link referring an another
        document in Silva, and an anchor.
        """
        version = self.root.document.get_editable()
        save_editor_text(
            version.test, u"""
<h2>This is simple piece of text</h2>
<p>
  This simple piece of text contains a magic chocobo:
</p>
<div class="image">
  <a class="image-link" anchor="top" reference={link}>
    <img alt="Chocobo" reference="{image}" />
  </a>
</div>""",
            content=version,
            link_content=self.root.other,
            link_name=u'test image link',
            image_content=self.root.chocobo,
            image_name=u'test image')

        factory = getMultiAdapter((version, TestRequest()), ITransformerFactory)
        transformer = factory(
            'test', version.test, unicode(version.test), IDisplayFilter)
        tests.assertXMLEqual(
            unicode(transformer),
            u"""
<h2>This is simple piece of text</h2>
<p>
  This simple piece of text contains a magic chocobo:
</p>
<div class="image">
  <a class="image-link" href="http://localhost/root/other#top">
    <img alt="Chocobo" height="256" width="256"
         src="http://localhost/root/chocobo" />
  </a>
</div>""")

    def test_render_image_with_internal_link_and_anchor_and_query(self):
        """Test render a piece of text with an image that is referring
        an asset in Silva, and with a link referring an another
        document in Silva, an anchor and an extra query.
        """
        version = self.root.document.get_editable()
        save_editor_text(
            version.test, u"""
<h2>This is simple piece of text</h2>
<p>
  This simple piece of text contains a magic chocobo:
</p>
<div class="image">
  <a class="image-link" anchor="top" reference={link} query="malabar">
    <img alt="Chocobo" reference="{image}" />
  </a>
</div>""",
            content=version,
            link_content=self.root.other,
            link_name=u'test image link',
            image_content=self.root.chocobo,
            image_name=u'test image')

        factory = getMultiAdapter((version, TestRequest()), ITransformerFactory)
        transformer = factory(
            'test', version.test, unicode(version.test), IDisplayFilter)
        tests.assertXMLEqual(
            unicode(transformer),
            u"""
<h2>This is simple piece of text</h2>
<p>
  This simple piece of text contains a magic chocobo:
</p>
<div class="image">
  <a class="image-link" href="http://localhost/root/other?malabar#top">
    <img alt="Chocobo" height="256" width="256"
         src="http://localhost/root/chocobo" />
  </a>
</div>""")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DisplayTransformTestCase))
    return suite
