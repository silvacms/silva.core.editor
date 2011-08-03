# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.editor.transform.interfaces import (IDisplayFilter,
    IIntroductionFilter)
from silva.core.editor.transform.base import (ReferenceTransformationFilter,
    TransformationFilter)
from silva.core.editor.utils import html_truncate_node

from zope.traversing.browser import absoluteURL


class LinkTransformer(ReferenceTransformationFilter):
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
                    link.attrib['href'] = absoluteURL(
                        reference.target, self.request)
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
            images = block.xpath('descendant::img')
            assert len(images) == 1, u"Invalid image construction"
            image = images[0]
            if 'reference' in image.attrib:
                name, reference = self.get_reference(
                    image.attrib['reference'], read_only=True)
                if reference is not None and reference.target_id:
                    image.attrib['src'] = absoluteURL(
                        reference.target, self.request)
                    del image.attrib['reference']


class ImageLinkTransformationFilter(ReferenceTransformationFilter):
    grok.implements(IDisplayFilter)
    grok.provides(IDisplayFilter)
    grok.order(10)
    grok.name('image link')

    _reference_tracking = False

    def __call__(self, tree):
        for block in tree.xpath('//div[contains(@class, "image")]'):
            links = block.xpath('descendant::a[@class="image-link"]')
            assert len(links) <= 1, u"Invalid image construction"
            if links:
                link = links[0]
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


class IntroductionTransformationFilter(TransformationFilter):
    grok.implements(IIntroductionFilter)
    grok.provides(IIntroductionFilter)
    grok.order(1000)
    grok.name('intro')

    max_length = 300

    def __call__(self, tree):
        html_truncate_node(tree, self.max_length)


