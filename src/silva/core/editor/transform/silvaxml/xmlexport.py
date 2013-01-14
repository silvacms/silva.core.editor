# -*- coding: utf-8 -*-
# Copyright (c) 2011-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
import lxml.sax
import lxml.html

from silva.core.editor.transform.base import TransformationFilter
from silva.core.editor.transform.interfaces import ISilvaXMLExportFilter
from silva.core.editor.transform.silvaxml import NS_EDITOR_URI
from silva.core.interfaces import IVersion, ISilvaXMLProducer
from silva.core.interfaces.errors import ExternalReferenceError
from silva.core.references.interfaces import IReferenceService
from silva.core.references.utils import canonical_path
from silva.core.xml.xmlexport import registry
from silva.translations import translate as _
from zope.component import getUtility


# Transformers

class XHTMLExportTransformer(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLProducer)
    grok.provides(ISilvaXMLExportFilter)
    grok.order(0)

    def __init__(self, context, handler):
        self.context = context
        self.handler = handler

    def __call__(self, tree):
        lxml.html.html_to_xhtml(tree)


class ReferenceExportTransformer(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLProducer)
    grok.provides(ISilvaXMLExportFilter)

    def __init__(self, context, handler):
        self.context = context
        self.handler = handler
        self.get_reference = getUtility(IReferenceService).get_reference

    def __call__(self, tree):
        exporter = self.handler.getExported()
        options = self.handler.getOptions()
        root = exporter.root
        for node in tree.xpath('//*[@reference]'):
            name = unicode(node.attrib['reference'])
            reference = self.get_reference(self.context, name=name)
            node.attrib['reference-type'] = reference.tags[0]
            node.attrib['reference'] = ''
            if reference.target_id:
                if not reference.is_target_inside_container(root):
                    if options.external_references:
                        exporter.reportProblem(
                            u'Text contains a reference pointing outside of '
                            u'the export ({0}).'.format(
                                '/'.join(reference.relative_path_to(root))),
                            content=self.context)
                        continue
                    else:
                        raise ExternalReferenceError(
                            _(u"External reference"),
                            self.context, reference.target, root)

                # Give the relative, prepended with the root id.
                node.attrib['reference'] = canonical_path(
                    '/'.join([root.getId()] + reference.relative_path_to(root)))
            else:
                exporter.reportProblem(
                    u'Text contains a broken reference in the export.',
                    content=self.context)


class ProxyHandler(lxml.sax.ElementTreeContentHandler):

    def __init__(self, producer):
        lxml.sax.ElementTreeContentHandler.__init__(self)
        self.producer = producer
        self.__prefixes = {}
        self.__namespaces = registry.getNamespaces()

    def startPrefixMapping(self, prefix, uri):
        if uri not in self.__namespaces:
            # This is an not known prefix.
            self.producer.handler.startPrefixMapping(prefix, uri)

        lxml.sax.ElementTreeContentHandler.startPrefixMapping(
            self, prefix, uri)

    def startElementNS(self, name, qname, attributes):
        prefix, localname = name
        if prefix in self.__prefixes:
            prefix = self.__prefixes[prefix]
        self.producer.startElementNS(prefix, localname, attributes)

    def endElementNS(self, name, qname):
        prefix, localname = name
        if prefix in self.__prefixes:
            prefix = self.__prefixes[prefix]
        self.producer.endElementNS(prefix, localname)

    def characters(self, content):
        self.producer.handler.characters(content)


class TextProducerProxy(object):

    def __init__(self, context, text):
        self.context = context
        self.text = text

    def sax(self, producer):
        producer.startElementNS(NS_EDITOR_URI, 'text')
        proxy= ProxyHandler(producer)
        transformer = self.text.get_transformer(
            self.context, producer, ISilvaXMLExportFilter)
        for part in transformer():
            lxml.sax.saxify(part, proxy)
        producer.endElementNS(NS_EDITOR_URI, 'text')


