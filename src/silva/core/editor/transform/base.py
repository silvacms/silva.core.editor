# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import uuid
import lxml.html

from five import grok
from zope.interface import Interface
from silva.core.editor.transform.interfaces import ITransformer
from silva.core.editor.transform.interfaces import ITransformationFilter
from silva.core.interfaces import IVersion, ISilvaXMLImportHandler
from silva.core.references.interfaces import IReferenceService
from zope import component


class Transformer(grok.MultiAdapter):
    grok.implements(ITransformer)
    grok.provides(ITransformer)
    grok.adapts(IVersion, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __transform(self, name, text, tree, interface):
        transformers = grok.queryOrderedMultiSubscriptions(
            (self.context, self.request), interface)
        for transformer in transformers:
            transformer.prepare(name, text)
        for transformer in transformers:
            transformer(tree)
        for transformer in transformers:
            transformer.finalize()

    def data(self, name, text, data, interface):
        tree = self._parse(data)
        self.__transform(name, text, tree, interface)
        return self._stringify(tree)

    def part(self, name, text, data, xpath, interface):
        trees = self._parse(data).xpath(xpath)
        results = []
        for tree in trees:
            self.__transform(name, text, tree, interface)
            results.append(self._stringify(tree))
        return results

    def _parse(self, data):
        # importers provides xhtml
        if ISilvaXMLImportHandler.providedBy(self.request):
            return lxml.etree.fromstring(data)

        data = '<div id="sce-transform-root">' + data + '</div>'
        return lxml.html.fromstring(data)

    def _stringify(self, tree):
        if tree.tag == 'div' and \
                tree.attrib.get('id') == 'sce-transform-root':
            strings = [lxml.html.tostring(c) for c in tree]
            return "\n".join(strings)

        return lxml.html.tostring(tree)


class TransformationFilter(grok.MultiSubscription):
    grok.baseclass()
    grok.implements(ITransformationFilter)
    grok.provides(ITransformationFilter)
    grok.adapts(IVersion, Interface)
    grok.order(20)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def prepare(self, name, text):
        pass

    def __call__(self, tree):
        pass

    def finalize(self):
        pass


class ReferenceTransformationFilter(TransformationFilter):
    grok.baseclass()
    grok.name('reference')

    _reference_tracking = True

    def __init__(self, context, request):
        super(ReferenceTransformationFilter, self).__init__(context, request)
        self._reference_service = component.getUtility(IReferenceService)
        self._references_used = set()
        self._references = {}

    def get_reference(self, link_name, read_only=False):
        """Retrieve an existing reference used in the XML.

        If read_only is set to True, when it will fail if the asked
        link is a new one or if it has already been asked.

        Don't call this method twice with the same link name and
        read_only set to False, or it will return a new reference (to
        handle copies).
        """
        if link_name == 'new' or link_name in self._references_used:
            # This is a new reference, or one that have already been
            # edited. In that case we create a new one, as it might be
            # a copy.
            if read_only:
                raise KeyError(u"Missing reference %s tagged %s" % (
                        self._reference_name, link_name))
            return self.new_reference()
        reference = self._references.get(link_name, None)
        if reference is not None:
            self._references_used.add(link_name)
        return link_name, reference

    def new_reference(self):
        """Create a new reference to be used in the XML.
        """
        reference = self._reference_service.new_reference(
            self.context, self._reference_name)
        link_name = unicode(uuid.uuid1())
        reference.add_tag(link_name)
        self._references[link_name] = reference
        self._references_used.add(link_name)
        return link_name, reference

    def prepare(self, name, text):
        super(ReferenceTransformationFilter, self).prepare(name, text)
        self._reference_name = u' '.join(
            (name, grok.name.bind().get(self.__class__)))
        self._references_used = set()
        self._references = dict(map(
                lambda r: (r.tags[1], r),
                filter(
                    lambda r: r.tags[0] == self._reference_name,
                    self._reference_service.get_references_from(
                        self.context))))

    def __call__(self, tree):
        pass

    def finalize(self):
        super(ReferenceTransformationFilter, self).finalize()
        if self._reference_tracking:
            for link_name, reference in self._references.items():
                if link_name not in self._references_used:
                    # Reference has not been used, remove it.
                    del self._reference_service.references[reference.__name__]
