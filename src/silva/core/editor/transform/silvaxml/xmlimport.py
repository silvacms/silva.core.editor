# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import sys
import uuid

from five import grok
from zope import component
import lxml.etree
import lxml.sax
import lxml.html

from silva.core.references.interfaces import IReferenceService
from Products.Silva.silvaxml import xmlimport
from silva.core.interfaces import IVersion, ISilvaXMLImportHandler
from silva.core.editor.transform.silvaxml import NS_URI
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
        self.service = component.getUtility(IReferenceService)

    def __call__(self, tree):
        for node in tree.xpath('//html:*[@reference]',
                namespaces={'html': 'http://www.w3.org/1999/xhtml'}):
            reference_type = node.attrib['reference-type']
            reference_name = unicode(uuid.uuid1())

            path = node.attrib['reference']
            reference = self.service.new_reference(self.context, reference_type)
            reference.add_tag(reference_name)
            # reference is broken at this point
            reference.set_target_id(0)

            def setter(target):
                reference.set_target(target)

            info = self.handler.getInfo()
            info.addAction(xmlimport.resolve_path, [setter, info, path])

            node.attrib['reference'] = reference_name
            del node.attrib['reference-type']

class TextHandler(xmlimport.SilvaBaseHandler):

    def startElementNS(self, name, qname, attrs):
        if hasattr(self, 'proxy_handler'):
            uri, localname = name
            if NS_URI == uri:
                self.proxy_handler.startElement(localname, attrs)
            else:
                self.proxy_handler.startElementNS(name, qname, attrs)

            if not hasattr(self, 'ready'):
                self.ready = name

            return

        if (NS_URI, 'text') == name:
            self.proxy_handler = lxml.sax.ElementTreeContentHandler()
            # set default namespace
            # self.proxy_handler.startPrefixMapping(None, NS_URI)
            self.text = self.parent()
            self.input_text = u''
            handler = self.parentHandler()
            self.version = None
            while handler:
                handler = handler.parentHandler()
                parent = handler.result()
                if IVersion.providedBy(parent):
                    self.version = parent
                    break

            if self.version is None:
                raise RuntimeError(
                    'expected an IVersion in handler parent chain results')

    def characters(self, input_text):
        if hasattr(self, 'proxy_handler') and getattr(self, 'ready', False):
            self.proxy_handler.characters(input_text)
            return

    def endElementNS(self, name, qname):
        if (NS_URI, 'text') == name:
            document = self.proxy_handler.etree
            self.text.save(self.version,
                self,
                lxml.etree.tostring(document),
                type=ISilvaXMLImportFilter)

            del self.version
            del self.text
            del self.input_text
            del self.proxy_handler
            del self.ready

        elif hasattr(self, 'proxy_handler'):
            uri, localname = name
            if NS_URI == uri:
                self.proxy_handler.endElement(localname)
            else:
                self.proxy_handler.endElementNS(name, qname)

            if name == self.ready:
                self.ready = False


