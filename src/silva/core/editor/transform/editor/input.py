# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.editor.transform.interfaces import IInputEditorFilter
from silva.core.editor.transform.base import ReferenceTransformer


class LinkTransfomer(ReferenceTransformer):
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

