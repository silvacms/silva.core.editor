# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import uuid
import lxml

from five import grok
from silva.core.editor.transform.interfaces import ITransformer
from silva.core.editor.transform.interfaces import ITransformationFilter
from silva.core.interfaces import IVersion
from silva.core.references.interfaces import IReferenceService
from zope import component
from zope.publisher.interfaces.browser import IBrowserRequest


class Transfomer(grok.MultiAdapter):
    grok.implements(ITransformer)
    grok.provides(ITransformer)
    grok.adapts(IVersion, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def data(self, name, text, data, interface):
        transformers = grok.queryOrderedSubscribers(
            (self.context, self.request), interface)
        tree = lxml.html.fromstring(data)
        for transformer in transformers:
            transformer.prepare(name, text)
        for transformer in transformers:
            transformer(tree)
        for transformer in transformers:
            transformer.finalize()
        return lxml.html.tostring(tree)

    def attribute(self, name, interface):
        text = getattr(self.context, name)
        return self.data(name, text, unicode(text), interface)


class TransformationFilter(grok.MultiSubscriber):
    grok.baseclass()
    grok.implements(ITransformationFilter)
    grok.provides(ITransformationFilter)
    grok.adapts(IVersion, IBrowserRequest)
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
