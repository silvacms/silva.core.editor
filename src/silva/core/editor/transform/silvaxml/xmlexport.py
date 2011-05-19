from five import grok
import lxml.sax
import lxml.html


from zope import component
from silva.core.interfaces import IVersion, ISilvaXMLExportHandler
from silva.core.editor.transform.base import TransformationFilter
from silva.core.editor.transform import interfaces as itransform
from silva.core.editor.transform.silvaxml import NS_URI
from silva.core.references.interfaces import IReferenceService
from silva.core.references.reference import canonical_path, get_content_from_id
from Products.Silva.silvaxml import xmlexport



# Transformers

class XHTMLExportTransformer(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLExportHandler)
    grok.provides(itransform.ISilvaXMLExportFilter)
    grok.order(0)

    def __init__(self, context, handler):
        self.context = context
        self.handler = handler

    def __call__(self, tree):
        lxml.html.html_to_xhtml(tree)


class ReferenceExportTransformer(TransformationFilter):
    grok.adapts(IVersion, ISilvaXMLExportHandler)
    grok.provides(itransform.ISilvaXMLExportFilter)

    def __init__(self, context, handler):
        self.context = context
        self.handler = handler
        self._reference_service = component.getUtility(IReferenceService)

    def __call__(self, tree):
        for node in tree.xpath('//html:*[@reference]',
                namespaces={'html': 'http://www.w3.org/1999/xhtml'}):
            name = unicode(node.attrib['reference'])
            reference = self._reference_service.get_reference(
                self.context, name=name)
            del node.attrib['reference']
            if reference.target_id:
                target = get_content_from_id(reference.target_id)
                if target is not None:
                    root = self.handler.getSettings().getExportRoot()
                    relative_path = [root.getId()] + \
                        reference.relative_path_to(root)
                    node.attrib['reference-name'] = name
                    node.attrib['reference'] = canonical_path(
                        "/".join(relative_path))


xmlexport.theXMLExporter.registerNamespace('silvacoreeditor', NS_URI)


class ProxyHandler(lxml.sax.ElementTreeContentHandler):
    def __init__(self, producer):
        lxml.sax.ElementTreeContentHandler.__init__(self)
        self.producer = producer

    def startPrefixMapping(self, prefix, uri):
        self.producer.handler.startPrefixMapping(prefix, uri)
        lxml.sax.ElementTreeContentHandler.startPrefixMapping(
            self, prefix, uri)

    def startElementNS(self, name, qname, attributes):
        uri, localname = name
        self.producer.startElementNS(uri, localname, attributes)

    def endElementNS(self, name, qname):
        uri, localname = name
        self.producer.endElementNS(uri, localname)

    def characters(self, content):
        self.producer.handler.characters(content)


class TextProducerProxy(object):

    def __init__(self, context, text):
        self.context = context
        self.text = text

    def sax(self, producer):
        producer.startElement('text', {'xmlns': NS_URI})
        xml_text = self.text.render(
            self.context, producer,
            itransform.ISilvaXMLExportFilter)
        handler = ProxyHandler(producer)
        lxml.sax.saxify(lxml.etree.fromstring(xml_text), handler)
        producer.endElement('text')


