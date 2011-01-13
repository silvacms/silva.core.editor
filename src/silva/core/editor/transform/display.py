# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.editor.transform.interfaces import IDisplayFilter
from silva.core.editor.transform.base import ReferenceTransformationFilter
from zope.traversing.browser import absoluteURL


class LinkTransfomer(ReferenceTransformationFilter):
    grok.implements(IDisplayFilter)
    grok.provides(IDisplayFilter)
    grok.order(10)
    grok.name('link')

    _reference_tracking = False

    def __call__(self, tree):
        for link in tree.xpath('//a[@class="link"]'):
            if 'reference' in link.attrib:
                name, reference = self.get_reference(
                    link.attrib['reference'], read_only=True)
                if reference is not None and reference.target_id:
                    link.attrib['href'] = absoluteURL(reference.target, self.request)
                    del link.attrib['reference']
            if 'href' not in link.attrib:
                link.attrib['href'] = ''
            if 'anchor' in link.attrib:
                link.attrib['href'] += '#' + link.attrib['anchor']


class ImageTransformationFilter(ReferenceTransformationFilter):
    grok.implements(IDisplayFilter)
    grok.provides(IDisplayFilter)
    grok.order(10)
    grok.name('image')

    _reference_tracking = False

    def __call__(self, tree):
        for block in tree.xpath('//div[contains(@class, "image")]'):
            images = block.xpath('//img')
            assert len(images) == 1, u"Invalid image construction"
            image = images[0]
            if 'reference' in image.attrib:
                name, reference = self.get_reference(
                    image.attrib['reference'], read_only=True)
                if reference is not None:
                    image.attrib['src'] = absoluteURL(reference.target, self.request)
                    del image.attrib['reference']
