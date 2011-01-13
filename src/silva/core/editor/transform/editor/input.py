# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.editor.transform.interfaces import IInputEditorFilter
from silva.core.editor.transform.base import ReferenceTransformationFilter
from zope.traversing.browser import absoluteURL


class LinkTransfomer(ReferenceTransformationFilter):
    grok.implements(IInputEditorFilter)
    grok.provides(IInputEditorFilter)
    grok.order(10)
    grok.name('link')

    def __call__(self, tree):
        for link in tree.xpath('//a[@class="link"]'):
            if 'reference' in link.attrib:
                name, reference = self.get_reference(
                    link.attrib['reference'], read_only=True)
                if reference is not None:
                    link.attrib['_silva_reference'] = name
                    link.attrib['_silva_target'] = str(reference.target_id)
                    del link.attrib['reference']
            if 'href' in link.attrib:
                link.attrib['_silva_href'] = link.attrib['href']
            if 'anchor' in link.attrib:
                link.attrib['_silva_anchor'] = link.attrib['anchor']
                del link.attrib['anchor']
            if 'href' not in link.attrib:
                link.attrib['href'] = 'javascript:void()'


class ImageTransformationFilter(ReferenceTransformationFilter):
    grok.implements(IInputEditorFilter)
    grok.provides(IInputEditorFilter)
    grok.order(10)
    grok.name('image')

    def __call__(self, tree):
        for block in tree.xpath('//div[contains(@class, "image")]'):
            images = block.xpath('//img')
            assert len(images) == 1, u"Invalid image construction"
            image = images[0]
            if 'reference' in image.attrib:
                name, reference = self.get_reference(
                    image.attrib['reference'], read_only=True)
                if reference is not None:
                    image.attrib['_silva_reference'] = name
                    image.attrib['_silva_target'] = str(reference.target_id)
                    image.attrib['src'] = absoluteURL(reference.target, self.request)
                    del image.attrib['reference']
            elif 'src' in image.attrib:
                image.attrib['_silva_src'] = image.attrib['src']

