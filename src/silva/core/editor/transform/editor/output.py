# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.editor.interfaces import ITextIndexEntries
from silva.core.editor.transform.interfaces import ISaveEditorFilter
from silva.core.editor.transform.base import ReferenceTransformationFilter
from silva.core.editor.transform.base import TransformationFilter
from silva.core.references.reference import get_content_from_id


def clean_editor_attributes(tag):
    """Remove editor attributes.
    """

    def is_an_editor_attribute(attribute_name):
        return attribute_name.startswith('data-silva-')

    for name in filter(is_an_editor_attribute, tag.attrib.keys()):
        del tag.attrib[name]


class SilvaReferenceTransformationFilter(ReferenceTransformationFilter):
    """Base class to update a reference information out of data-silva-
    tags.
    """
    grok.baseclass()
    grok.implements(ISaveEditorFilter)
    grok.provides(ISaveEditorFilter)

    def update_reference_for(self, attributes):
        name, reference = self.get_reference(attributes['data-silva-reference'])
        if reference is not None:
            target_id = attributes.get('data-silva-target', '0')
            try:
                target_id = int(str(target_id))
                assert get_content_from_id(target_id) is not None
            except (ValueError, AssertionError):
                # Invalid target id, set it as zero (broken)
                target_id = 0
        else:
            # Invalid reference. We create a new one and mark the
            # target as broken
            name, reference = self.get_reference('new')
            target_id = 0
        if target_id != reference.target_id:
            reference.set_target_id(target_id)
        attributes['reference'] = name


class LinkTransfomer(SilvaReferenceTransformationFilter):
    """Handle link reference.
    """
    grok.order(10)
    grok.name('link')

    def __call__(self, tree):
        for link in tree.xpath('//a[@class="link"]'):
            if 'data-silva-reference' in link.attrib:
                self.update_reference_for(link.attrib)
            if 'data-silva-href' in link.attrib:
                link.attrib['href'] = link.attrib['data-silva-href']
            if 'data-silva-anchor' in link.attrib:
                link.attrib['anchor'] = link.attrib['data-silva-anchor']
            clean_editor_attributes(link)


class ImageTransfomer(SilvaReferenceTransformationFilter):
    """Handle image reference.
    """
    grok.order(10)
    grok.name('image')

    def __call__(self, tree):
        for block in tree.xpath('//div[contains(@class, "image")]'):
            images = block.xpath('//img')
            assert len(images) == 1, u"Invalid image construction"
            image = images[0]
            if 'data-silva-reference' in image.attrib:
                self.update_reference_for(image.attrib)
                del image.attrib['src']
            if 'data-silva-src' in image.attrib:
                image.attrib['src'] = image.attrib['data-silva-src']
            clean_editor_attributes(image)


class ImageLinkTransformer(SilvaReferenceTransformationFilter):
    """Handle image link reference.
    """
    grok.order(10)
    grok.name('image link')

    def __call__(self, tree):
        for block in tree.xpath('//div[contains(@class, "image")]'):
            links = block.xpath('//a[@class="image-link"]')
            assert len(links) <= 1, u"Invalid image construction"
            if links:
                link = links[0]
                if 'data-silva-reference' in link.attrib:
                    self.update_reference_for(link.attrib)
                if 'data-silva-href' in link.attrib:
                    link.attrib['href'] = link.attrib['data-silva-href']
                if 'data-silva-anchor' in link.attrib:
                    link.attrib['anchor'] = link.attrib['data-silva-anchor']
                clean_editor_attributes(link)


class AnchorCollector(TransformationFilter):
    """Collect text anchors to save indexes on a text object's
    annotation.
    """
    grok.implements(ISaveEditorFilter)
    grok.provides(ISaveEditorFilter)
    grok.order(50)

    def prepare(self, name, text):
        self.entries = ITextIndexEntries(text)

    def __call__(self, tree):
        for anchor in tree.xpath('//a[@class="anchor"]'):
            if 'name' in anchor.attrib and 'title' in anchor.attrib:
                self.entries.add(anchor.attrib['name'], anchor.attrib['title'])
