# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.traversing.browser import absoluteURL

from silva.core.interfaces import IImageIncluable

from ..base import ReferenceTransformationFilter, TransformationFilter
from ..interfaces import IInputEditorFilter


class LinkTransformer(ReferenceTransformationFilter):
    grok.implements(IInputEditorFilter)
    grok.provides(IInputEditorFilter)
    grok.order(10)
    grok.name('link')

    _read_only = True

    def __call__(self, tree):
        for link in tree.xpath('//a[contains(@class, "link")]'):
            classes = link.attrib['class'].split()
            if 'link' not in classes:
                continue
            if 'reference' in link.attrib:
                name, reference = self.get_reference(link.attrib['reference'])
                if reference is not None:
                    link.attrib['data-silva-reference'] = name
                    link.attrib['data-silva-target'] = str(reference.target_id)
                    del link.attrib['reference']
                    if not reference.target_id and 'broken-link' not in classes:
                        classes.append('broken-link')
                        link.attrib['class'] = ' '.join(classes)
            if 'href' in link.attrib:
                href = link.attrib['href']
                link.attrib['data-silva-url'] = href
                if href.startswith('broken:') or href.startswith('/'):
                    classes.append('broken-link')
                    link.attrib['class'] = ' '.join(classes)
            if 'query' in link.attrib:
                link.attrib['data-silva-query'] = link.attrib['query']
                del link.attrib['query']
            if 'anchor' in link.attrib:
                link.attrib['data-silva-anchor'] = link.attrib['anchor']
                del link.attrib['anchor']
            # Ensure href is always disabled.
            link.attrib['href'] = 'javascript:void(0)'


class AnchorTransformer(TransformationFilter):
    grok.implements(IInputEditorFilter)
    grok.provides(IInputEditorFilter)
    grok.order(10)

    def __call__(self, tree):
        for anchor in tree.xpath('//a[@class="anchor"]'):
            # You can set href here (or it will be extermitated by
            # CKEDITOR.htmlParser.fragment.fromHtml).
            if 'href' in anchor.attrib:
                del anchor.attrib['href']


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
            if 'resolution' in image.attrib:
                image.attrib['data-silva-resolution'] = image.attrib['resolution']
                del image.attrib['resolution']
            if 'reference' in image.attrib:
                name, reference = self.get_reference(image.attrib['reference'])
                if reference is not None:
                    target_id = '0'
                    url = './++static++/silva.core.editor/broken-link.jpg'
                    if reference.target_id:
                        target_id = str(reference.target_id)
                        target = reference.target
                        if IImageIncluable.providedBy(target):
                            url = absoluteURL(target, self.request)
                    image.attrib['data-silva-reference'] = name
                    image.attrib['data-silva-target'] = target_id
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
                link.attrib['href'] = 'javascript:void(0)'
