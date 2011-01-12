# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.editor.transform.interfaces import IOutputEditorFilter
from silva.core.editor.transform.base import (
    ReferenceTransformer, Transformer)
from silva.core.references.reference import get_content_from_id


def clean_editor_attributes(tag):
    """Remove editor attributes.
    """

    def is_an_editor_attribute(attribute_name):
        return attribute_name.startswith('_silva_')

    for name in filter(is_an_editor_attribute, tag.attrib.keys()):
        del tag.attrib[name]



class LinkTransfomer(ReferenceTransformer):
    grok.implements(IOutputEditorFilter)
    grok.provides(IOutputEditorFilter)
    grok.order(10)
    grok.name('link')

    def __call__(self, tree):
        for link in tree.xpath('//a[@class="link"]'):
            if '_silva_reference' in link.attrib:
                name, reference = self.get_reference(
                    link.attrib['_silva_reference'])
                if reference is not None:
                    target_id = link.attrib['_silva_target']
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
                link.attrib['reference'] = name
            if '_silva_href' in link.attrib:
                link.attrib['href'] = link.attrib['_silva_href']
            if '_silva_anchor' in link.attrib:
                link.attrib['anchor'] = link.attrib['_silva_anchor']
            clean_editor_attributes(link)

