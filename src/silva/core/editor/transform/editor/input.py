# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.traversing.browser import absoluteURL
from zope.component import getUtility

from silva.core.editor.interfaces import ICKEditorService
from silva.core.editor.transform.interfaces import IInputEditorFilter
from silva.core.editor.transform.base import ReferenceTransformationFilter, TransformationFilter
from silva.core.editor.utils import html_sanitize_node


class LinkTransformer(ReferenceTransformationFilter):
    grok.implements(IInputEditorFilter)
    grok.provides(IInputEditorFilter)
    grok.order(10)
    grok.name('link')

    _read_only = True

    def __call__(self, tree):
        for link in tree.xpath('//a[@class="link"]'):
            if 'reference' in link.attrib:
                name, reference = self.get_reference(link.attrib['reference'])
                if reference is not None:
                    link.attrib['data-silva-reference'] = name
                    link.attrib['data-silva-target'] = str(reference.target_id)
                    del link.attrib['reference']
            if 'href' in link.attrib:
                link.attrib['data-silva-url'] = link.attrib['href']
            if 'anchor' in link.attrib:
                link.attrib['data-silva-anchor'] = link.attrib['anchor']
                del link.attrib['anchor']
            # Ensure href is always disabled.
            link.attrib['href'] = 'javascript:void()'


class ImageTransformer(ReferenceTransformationFilter):
    grok.implements(IInputEditorFilter)
    grok.provides(IInputEditorFilter)
    grok.order(10)
    grok.name('image')

    _read_only = True

    def __call__(self, tree):
        for block in tree.xpath('//div[contains(@class, "image")]'):
            images = block.xpath('descendant::img')
            assert len(images) == 1, u"Invalid image construction"
            image = images[0]
            if 'reference' in image.attrib:
                name, reference = self.get_reference(image.attrib['reference'])
                if reference is not None:
                    image.attrib['data-silva-reference'] = name
                    if reference.target_id:
                        target = str(reference.target_id)
                        url = absoluteURL(reference.target, self.request)
                    else:
                        target = '0'
                        url = './++static++/silva.core.editor/broken-link.jpg'
                    image.attrib['data-silva-target'] = target
                    image.attrib['src'] = url
                    del image.attrib['reference']
            elif 'src' in image.attrib:
                image.attrib['data-silva-url'] = image.attrib['src']


class ImageLinkTransformer(ReferenceTransformationFilter):
    grok.implements(IInputEditorFilter)
    grok.provides(IInputEditorFilter)
    grok.order(10)
    grok.name('image link')

    _read_only = True

    def __call__(self, tree):
        for block in tree.xpath('//div[contains(@class, "image")]'):
            links = block.xpath('descendant::a[@class="image-link"]')
            assert len(links) <= 1, u"Invalid image construction"
            if links:
                link = links[0]
                if 'reference' in link.attrib:
                    name, reference = self.get_reference(
                        link.attrib['reference'])
                    if reference is not None:
                        link.attrib['data-silva-reference'] = name
                        link.attrib['data-silva-target'] = str(
                            reference.target_id)
                        del link.attrib['reference']
                elif 'href' in link.attrib:
                    link.attrib['data-silva-url'] = link.attrib['href']
                if 'query' in link.attrib:
                    link.attrib['data-silva-query'] = link.attrib['query']
                    del link.attrib['query']
                if 'anchor' in link.attrib:
                    link.attrib['data-silva-anchor'] = link.attrib['anchor']
                    del link.attrib['anchor']
                # Ensure link is always disabled.
                link.attrib['href'] = 'javascript:void()'


class SanitizeTransformer(TransformationFilter):
    grok.implements(IInputEditorFilter)
    grok.provides(IInputEditorFilter)
    grok.order(1000000)
    grok.name('sanitizer')

    extra_attributes = set(['data-silva-reference',
                            'data-silva-target',
                            'data-silva-url',
                            'data-silva-anchor'])

    def __call__(self, tree):
        service = getUtility(ICKEditorService)
        html_sanitize_node(
            tree,
            service.get_allowed_html_tags(),
            service.get_allowed_html_attributes() | self.extra_attributes)
