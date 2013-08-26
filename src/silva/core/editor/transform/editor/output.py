# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import urlparse

from five import grok
from zope.component import queryUtility

from silva.core.references.reference import get_content_from_id

from silva.core.editor.interfaces import ITextIndexEntries, ICKEditorService
from silva.core.editor.transform.interfaces import ISaveEditorFilter
from silva.core.editor.transform.base import ReferenceTransformationFilter
from silva.core.editor.transform.base import TransformationFilter
from silva.core.editor.utils import html_sanitize_node
from silva.core.editor.utils import URL_SCHEMES_WHITELIST
from silva.core.editor.utils import URL_SCHEMES_BLACKLIST
from silva.core.editor.utils import DEFAULT_PER_TAG_WHITELISTS
from silva.core.editor.utils import DEFAULT_HTML_ATTR_WHITELIST
from silva.core.editor.utils import DEFAULT_CSS_PROP_WHITELIST


def extract_url(url, url_schemes=URL_SCHEMES_WHITELIST):
    """Analyse and return a valid URL or None.
    """
    url = url and url.strip()
    if url:
        info = urlparse.urlparse(url)
        # We just check the URL scheme at the moment.
        if not info.scheme:
            if url.startswith('/'):
                # Allow URL that starts with a '/'
                return url
            # Keep other URLs as broken
            return 'broken:' + url
        if info.scheme not in URL_SCHEMES_BLACKLIST:
            if info.scheme in url_schemes:
                return url
            # Keep other URLs as broken
            return 'broken:' + url
    return None


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
        name, reference = self.get_reference(
            attributes['data-silva-reference'])
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


class LinkTransformer(SilvaReferenceTransformationFilter):
    """Handle link reference.
    """
    grok.order(10)
    grok.name('link')

    def __call__(self, tree):
        for link in tree.xpath('//a[contains(@class, "link")]'):
            classes = link.attrib['class'].split()
            if 'link' not in classes:
                continue
            if 'broken-link' in classes:
                classes.remove('broken-link')
                link.attrib['class'] = ' '.join(classes)
            if 'href' in link.attrib:
                del link.attrib['href']
            if 'data-silva-reference' in link.attrib:
                self.update_reference_for(link.attrib)
            elif 'data-silva-url' in link.attrib:
                url = extract_url(link.attrib['data-silva-url'])
                if url is not None:
                    link.attrib['href'] = url
            if 'data-silva-anchor' in link.attrib:
                link.attrib['anchor'] = link.attrib['data-silva-anchor']
            if 'data-silva-query' in link.attrib:
                link.attrib['query'] = link.attrib['data-silva-query']
            # XXX It is possible the link looses its reference, url and anchor.
            clean_editor_attributes(link)


class ImageTransformer(SilvaReferenceTransformationFilter):
    """Handle image reference.
    """
    grok.order(10)
    grok.name('image')

    def __call__(self, tree):
        for block in tree.xpath('//div[contains(@class, "image")]'):
            images = block.xpath('descendant::img')
            assert len(images) == 1, u"Invalid image construction"
            image = images[0]
            if 'src' in image.attrib:
                del image.attrib['src']
            if 'data-silva-reference' in image.attrib:
                self.update_reference_for(image.attrib)
            if 'data-silva-url' in image.attrib:
                src = extract_url(
                    image.attrib['data-silva-url'],
                    set(['http', 'https']))
                if src is not None:
                    image.attrib['src'] = src
            if 'data-silva-resolution' in image.attrib:
                resolution = image.attrib['data-silva-resolution']
                if resolution in ('thumbnail', 'hires'):
                    image.attrib['resolution'] = resolution
            clean_editor_attributes(image)


class ImageLinkTransformer(SilvaReferenceTransformationFilter):
    """Handle image link reference.
    """
    grok.order(10)
    grok.name('image link')

    def __call__(self, tree):
        for block in tree.xpath('//div[contains(@class, "image")]'):
            links = block.xpath('descendant::a[@class="image-link"]')
            assert len(links) <= 1, u"Invalid image construction"
            if links:
                link = links[0]
                if 'data-silva-reference' in link.attrib:
                    self.update_reference_for(link.attrib)
                elif 'data-silva-url' in link.attrib:
                    url = extract_url(link.attrib['data-silva-url'])
                    if url is not None:
                        link.attrib['href'] = url
                if 'data-silva-anchor' in link.attrib:
                    link.attrib['anchor'] = link.attrib['data-silva-anchor']
                if 'data-silva-query' in link.attrib:
                    link.attrib['query'] = link.attrib['data-silva-query']
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
        self.entries.clear()

    truncate = prepare

    def __call__(self, tree):
        for anchor in tree.xpath('//a[@class="anchor"]'):
            if 'name' in anchor.attrib and 'title' in anchor.attrib:
                name = anchor.attrib['name'].strip()
                title = anchor.attrib['title'].strip()
                if name and title:
                    # Only collect entries with a name and a title
                    self.entries.add(name, title)
                # Save back stripped values
                anchor.attrib['name'] = name
                anchor.attrib['title'] = title
            if 'href' in anchor.attrib:
                # Those should not have any href, so clean them
                del anchor.attrib['href']


class SanitizeTransformer(TransformationFilter):
    grok.implements(ISaveEditorFilter)
    grok.provides(ISaveEditorFilter)
    grok.order(1000)

    _per_tag_allowed_attr = None
    _html_attributes = None
    _extra_html_attributes = set(
        ['reference', 'anchor', 'query', 'resolution'])
    _css_attributes = None

    def prepare(self, name, text):
        service = queryUtility(ICKEditorService)

        if service is not None:
            self._per_tag_allowed_attr = service.get_per_tag_allowed_attr()
            self._html_attributes = service.get_allowed_html_attributes()
            self._css_attributes = service.get_allowed_css_attributes()

        if self._per_tag_allowed_attr is None:
            self._per_tag_allowed_attr = DEFAULT_PER_TAG_WHITELISTS
        if self._html_attributes is None:
            self._html_attributes = DEFAULT_HTML_ATTR_WHITELIST
        if self._css_attributes is None:
            self._css_attributes = DEFAULT_CSS_PROP_WHITELIST

        self._html_attributes |= self._extra_html_attributes

    def __call__(self, tree):
        if (self._per_tag_allowed_attr is not None
                and self._html_attributes is not None):
            html_sanitize_node(tree,
                               self._per_tag_allowed_attr,
                               self._html_attributes,
                               self._css_attributes)
