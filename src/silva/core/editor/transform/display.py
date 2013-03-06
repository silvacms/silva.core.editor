# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from silva.core.interfaces import IImage
from silva.core.editor.transform.interfaces import IDisplayFilter
from silva.core.editor.transform.base import ReferenceTransformationFilter

from zope.traversing.browser import absoluteURL


class LinkTransformer(ReferenceTransformationFilter):
    grok.implements(IDisplayFilter)
    grok.provides(IDisplayFilter)
    grok.order(10)
    grok.name('link')

    _read_only = True
    _reference_tracking = False

    def __call__(self, tree):
        for link in tree.xpath('//a[@class="link"]'):
            if 'reference' in link.attrib:
                name, reference = self.get_reference(link.attrib['reference'])
                if reference is not None and reference.target_id:
                    link.attrib['href'] = absoluteURL(
                        reference.target, self.request)
                del link.attrib['reference']
            elif 'href' not in link.attrib:
                link.attrib['href'] = ''
            if 'query' in link.attrib:
                link.attrib['href'] += '?' + link.attrib['query']
                del link.attrib['query']
            if 'anchor' in link.attrib:
                link.attrib['href'] += '#' + link.attrib['anchor']
                del link.attrib['anchor']


class ImageTransformationFilter(ReferenceTransformationFilter):
    grok.implements(IDisplayFilter)
    grok.provides(IDisplayFilter)
    grok.order(10)
    grok.name('image')

    _read_only = True
    _reference_tracking = False

    def __call__(self, tree):
        for block in tree.xpath('//div[contains(@class, "image")]'):
            images = block.xpath('descendant::img')
            assert len(images) == 1, u"Invalid image construction"
            image = images[0]
            if 'reference' in image.attrib:
                name, reference = self.get_reference(image.attrib['reference'])
                if reference is not None and reference.target_id:
                    content = reference.target
                    image_url = absoluteURL(content, self.request)
                    if IImage.providedBy(content):
                        resolution = None
                        if 'resolution' in image.attrib:
                            resolution = image.attrib['resolution']
                            del image.attrib['resolution']
                        if resolution == 'hires':
                            image_url += '?hires'
                            size = content.get_dimensions(hires=True)
                        elif resolution == 'thumbnail':
                            image_url += '?thumbnail'
                            size = content.get_dimensions(thumbnail=True)
                        else:
                            size = content.get_dimensions()
                        if size.height and size.width:
                            image.attrib['height'] = str(size.height)
                            image.attrib['width'] = str(size.width)
                    image.attrib['src'] = image_url
                del image.attrib['reference']


class ImageLinkTransformationFilter(ReferenceTransformationFilter):
    grok.implements(IDisplayFilter)
    grok.provides(IDisplayFilter)
    grok.order(10)
    grok.name('image link')

    _read_only = True
    _reference_tracking = False

    def __call__(self, tree):
        for block in tree.xpath('//div[contains(@class, "image")]'):
            links = block.xpath('descendant::a[@class="image-link"]')
            assert len(links) <= 1, u"Invalid image construction"
            if links:
                link = links[0]
                if 'reference' in link.attrib:
                    name, reference = self.get_reference(
                        link.attrib['reference'])
                    if reference is not None and reference.target_id:
                        content = reference.target
                        link.attrib['href'] = absoluteURL(content, self.request)
                    del link.attrib['reference']
                if 'href' not in link.attrib:
                    link.attrib['href'] = ''
                if 'query' in link.attrib:
                    link.attrib['href'] += '?' + link.attrib['query']
                    del link.attrib['query']
                if 'anchor' in link.attrib:
                    link.attrib['href'] += '#' + link.attrib['anchor']
                    del link.attrib['anchor']



