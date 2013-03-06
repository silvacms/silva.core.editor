# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import uuid

from five import grok
from zope.component import getUtility
import lxml.etree
import lxml.sax
import lxml.html

from silva.core.editor.transform.base import TransformationFilter
from silva.core.editor.transform.editor.output import AnchorCollector
from silva.core.editor.transform.interfaces import ISilvaXMLImportFilter
from silva.core.editor.transform.silvaxml import NS_EDITOR_URI, NS_HTML_URI
from silva.core.interfaces import IVersion, ISilvaXMLHandler
from silva.core.references.interfaces import IReferenceService
from silva.core.xml import handlers


class XHTMLImportTransformer(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLHandler)
    grok.provides(ISilvaXMLImportFilter)
    grok.order(100)

    def __init__(self, context, handler):
        self.context = context
        self.handler = handler

    def __call__(self, tree):
        lxml.html.xhtml_to_html(tree)
        lxml.etree.cleanup_namespaces(tree)


class ReferenceImportTransformer(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLHandler)
    grok.provides(ISilvaXMLImportFilter)
    grok.implements(ISilvaXMLImportFilter)
    grok.order(10)

    def __init__(self, context, handler):
        self.context = context
        self.handler = handler
        self.new_reference = getUtility(IReferenceService).new_reference

    def __call__(self, tree):
        importer = self.handler.getExtra()
        for node in tree.xpath('//*[@reference]'):
            reference_type = unicode(node.attrib['reference-type'])
            reference_name = unicode(uuid.uuid1())
            path = node.attrib['reference']

            reference = self.new_reference(self.context, reference_type)
            reference.add_tag(reference_name)

            if not path:
                importer.reportProblem(
                    u'Broken reference in import file.',
                    self.context)
            else:
                importer.resolveImportedPath(
                    self.context, reference.set_target, path)

            node.attrib['reference'] = reference_name
            del node.attrib['reference-type']


# This one must be executed after XHTMLImportTransformer that cleanup
# the namespaces.
class ImportAnchorCollector(AnchorCollector):
    grok.adapts(IVersion, ISilvaXMLHandler)
    grok.provides(ISilvaXMLImportFilter)
    grok.implements(ISilvaXMLImportFilter)
    grok.order(150)


class TextHandler(handlers.SilvaHandler):
    proxy = None

    def startElementNS(self, name, qname, attrs):
        if (NS_EDITOR_URI, 'text') == name:
            # Create a proxy, with a root element.
            self.proxy = lxml.sax.ElementTreeContentHandler()
            self.proxy.startElementNS((NS_HTML_URI, 'div'), 'div', {})
        else:
            ns, localname = name
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
            if self.proxy is None:
                raise RuntimeError('Invalid HTML')
            self.proxy.endElementNS(name, qname)

