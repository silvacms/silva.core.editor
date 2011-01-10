# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.editor.transform.interfaces import IDisplayFilter
from silva.core.editor.transform.base import ReferenceTransformer
from zope.traversing.browser import absoluteURL


class LinkTransfomer(ReferenceTransformer):
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

