# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import sys
import uuid

from five import grok
from zope.component import getUtility
import lxml.etree
import lxml.sax
import lxml.html

from silva.core.references.interfaces import IReferenceService
from Products.Silva.silvaxml import xmlimport
from silva.core.interfaces import IVersion, ISilvaXMLImportHandler
from silva.core.editor.transform.silvaxml import NS_EDITOR_URI, NS_HTML_URI
from silva.core.editor.transform.interfaces import ISilvaXMLImportFilter
from silva.core.editor.transform.base import TransformationFilter


class XHTMLImportTransformer(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLImportHandler)
    grok.provides(ISilvaXMLImportFilter)
    grok.order(sys.maxint)

    def __init__(self, context, handler):
        self.context = context
        self.handler = handler

    def __call__(self, tree):
        lxml.html.xhtml_to_html(tree)
        lxml.etree.cleanup_namespaces(tree)


class ReferenceImportTransformer(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLImportHandler)
    grok.provides(ISilvaXMLImportFilter)

    def __init__(self, context, handler):
        self.context = context
        self.handler = handler
        self.new_reference = getUtility(IReferenceService).new_reference

    def __call__(self, tree):
        info = self.handler.getInfo()
        for node in tree.xpath('//*[@reference]'):
            reference_type = unicode(node.attrib['reference-type'])
            reference_name = unicode(uuid.uuid1())
            path = node.attrib['reference']

            reference = self.new_reference(self.context, reference_type)
            reference.add_tag(reference_name)

            info.addAction(
                xmlimport.resolve_path,
                [reference.set_target, info, path])

            node.attrib['reference'] = reference_name
            del node.attrib['reference-type']


class TextHandler(xmlimport.SilvaBaseHandler):
    proxy = None

    def startElementNS(self, name, qname, attrs):
        if (NS_EDITOR_URI, 'text') == name:
            # Create a proxy, with a root element.
            self.proxy = lxml.sax.ElementTreeContentHandler()
            self.proxy.startElementNS((NS_HTML_URI, 'div'), 'div', {})
        else:
            ns, localname = name
            if ns == NS_HTML_URI:
                if self.proxy is None:
                    raise RuntimeError('Invalid construction')
                self.proxy.startElementNS(name, qname, attrs)

    def characters(self, input_text):
        if self.proxy is not None:
            self.proxy.characters(input_text)

    def endElementNS(self, name, qname):
        if (NS_EDITOR_URI, 'text') == name:
            # Close the root tag
            self.proxy.endElementNS((NS_HTML_URI, 'div'), 'div')

            # Find the version. It is should the result of on the parent handler
            version = None
            handler = self.parentHandler()
            while handler:
                result = handler.result()
                if IVersion.providedBy(result):
                    version = result
                    break
                handler = handler.parentHandler()

            if version is None:
                raise RuntimeError(
                    'expected an IVersion in handler parent chain results')

            # Get the text to save without the root element we added.
            text = u'\n'.join(
                map(lxml.etree.tostring, self.proxy.etree.getroot()))

            # Save the text and clear the proxy.
            self.parent().save(version, self, text, ISilvaXMLImportFilter)
            self.proxy = None
        else:
            ns, localname = name
            if ns == NS_HTML_URI:
                if self.proxy is None:
                    raise RuntimeError('Invalid HTML')
                self.proxy.endElementNS(name, qname)

