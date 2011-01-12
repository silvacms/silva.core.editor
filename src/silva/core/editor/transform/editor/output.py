# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.editor.transform.interfaces import IOutputEditorFilter
from silva.core.editor.transform.base import ReferenceTransformer
from silva.core.references.reference import get_content_from_id


def clean_editor_attributes(tag):
    """Remove editor attributes.
    """

    def is_an_editor_attribute(attribute_name):
        return attribute_name.startswith('_silva_')

    for name in filter(is_an_editor_attribute, tag.attrib.keys()):
        del tag.attrib[name]


class SilvaReferenceTransformer(ReferenceTransformer):
    grok.baseclass()
    grok.implements(IOutputEditorFilter)
    grok.provides(IOutputEditorFilter)

    def update_reference_for(self, attributes):
        name, reference = self.get_reference(attributes['_silva_reference'])
        if reference is not None:
            target_id = attributes.get('_silva_target', '0')
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


class LinkTransfomer(SilvaReferenceTransformer):
    grok.order(10)
    grok.name('link')

    def __call__(self, tree):
        for link in tree.xpath('//a[@class="link"]'):
            if '_silva_reference' in link.attrib:
                self.update_reference_for(link.attrib)
            if '_silva_href' in link.attrib:
                link.attrib['href'] = link.attrib['_silva_href']
            if '_silva_anchor' in link.attrib:
                link.attrib['anchor'] = link.attrib['_silva_anchor']
            clean_editor_attributes(link)


class ImageTransfomer(SilvaReferenceTransformer):
    grok.order(10)
    grok.name('image')

    def __call__(self, tree):
        for block in tree.xpath('//div[contains(@class, "image")]'):
            images = block.xpath('//img')
            assert len(images) == 1, u"Invalid image construction"
            image = images[0]
            if '_silva_reference' in image.attrib:
                self.update_reference_for(image.attrib)
                del image.attrib['src']
            if '_silva_src' in image.attrib:
                image.attrib['src'] = image.attrib['_silva_src']
            clean_editor_attributes(image)
