# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.editor.transform.interfaces import IInputEditorFilter
from silva.core.editor.transform.base import ReferenceTransformationFilter
from zope.traversing.browser import absoluteURL


class LinkTransformer(ReferenceTransformationFilter):
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
                    link.attrib['data-silva-reference'] = name
                    link.attrib['data-silva-target'] = str(reference.target_id)
                    del link.attrib['reference']
            if 'href' in link.attrib:
                link.attrib['data-silva-href'] = link.attrib['href']
            if 'anchor' in link.attrib:
                link.attrib['data-silva-anchor'] = link.attrib['anchor']
                del link.attrib['anchor']
            if 'href' not in link.attrib:
                link.attrib['href'] = 'javascript:void()'


class ImageTransformer(ReferenceTransformationFilter):
    grok.implements(IInputEditorFilter)
    grok.provides(IInputEditorFilter)
    grok.order(10)
    grok.name('image')

    def __call__(self, tree):
        for block in tree.xpath('//div[contains(@class, "image")]'):
            images = block.xpath('descendant::img')
            assert len(images) == 1, u"Invalid image construction"
            image = images[0]
            if 'reference' in image.attrib:
                name, reference = self.get_reference(
                    image.attrib['reference'], read_only=True)
                if reference is not None:
                    image.attrib['data-silva-reference'] = name
                    image.attrib['data-silva-target'] = str(reference.target_id)
                    image.attrib['src'] = absoluteURL(reference.target, self.request)
                    del image.attrib['reference']
            elif 'src' in image.attrib:
                image.attrib['data-silva-src'] = image.attrib['src']


class ImageLinkTransformer(ReferenceTransformationFilter):
    grok.implements(IInputEditorFilter)
    grok.provides(IInputEditorFilter)
    grok.order(10)
    grok.name('image link')

    def __call__(self, tree):
        for block in tree.xpath('//div[contains(@class, "image")]'):
            links = block.xpath('descendant::a[@class="image-link"]')
            assert len(links) <= 1, u"Invalid image construction"
            if links:
                link = links[0]
                if 'reference' in link.attrib:
                    name, reference = self.get_reference(
                        link.attrib['reference'], read_only=True)
                    if reference is not None:
                        link.attrib['data-silva-reference'] = name
                        link.attrib['data-silva-target'] = str(reference.target_id)
                        del link.attrib['reference']
                if 'href' in link.attrib:
                    link.attrib['data-silva-href'] = link.attrib['href']
                if 'anchor' in link.attrib:
                    link.attrib['data-silva-anchor'] = link.attrib['anchor']
                    del link.attrib['anchor']
                if 'href' not in link.attrib:
                    link.attrib['href'] = 'javascript:void()'
