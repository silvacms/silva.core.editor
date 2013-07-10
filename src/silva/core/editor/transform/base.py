# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import uuid
import lxml.html

from five import grok
from zope.interface import Interface
from silva.core.editor.transform.interfaces import ITransformer
from silva.core.editor.transform.interfaces import ITransformerFactory
from silva.core.editor.transform.interfaces import ITransformationFilter
from silva.core.interfaces import IVersion, ISilvaXMLHandler
from silva.core.references.interfaces import IReferenceService
from zope import component


class TransformerFactory(grok.MultiAdapter):
    grok.implements(ITransformerFactory)
    grok.provides(ITransformerFactory)
    grok.adapts(IVersion, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, name, text, data, interface):
        transformers = grok.queryOrderedMultiSubscriptions(
            (self.context, self.request), interface)
        return Transformer(
            transformers,
            data,
            prepare=(name, text),
            xhtml=ISilvaXMLHandler.providedBy(self.request))


class Transformer(object):
    """Apply transformers to an input data.
    """
    grok.implements(ITransformer)

    def __init__(self, transformers, data, prepare, xhtml=False):
        self.__xhtml = xhtml
        self.__transformers = transformers
        self.__prepare = prepare
        self.__trees = []
        self.__processed = False
        if data is not None:
            data = '<div id="sce-transform-root">' + data + '</div>'
            if xhtml:
                self.__trees = [lxml.etree.fromstring(data)]
            else:
                self.__trees = [lxml.html.fromstring(data)]

    def restrict(self, xpath):
        restrictions = []
        for tree in self.__trees:
            restrictions.extend(tree.xpath(xpath))
        self.__trees = restrictions

    def visit(self, function):
        map(function, self.__trees)

    def transform(self):
        if not self.__processed:
            for transformer in self.__transformers:
                transformer.prepare(*self.__prepare)
            for tree in self.__trees:
                for transformer in self.__transformers:
                    transformer(tree)
            for transformer in self.__transformers:
                transformer.finalize()
            self.__processed = True

    @property
    def trees(self):
        for tree in self.__trees:
            if tree.attrib.get('id') == 'sce-transform-root':
                # Ignore transformation root
                for child in tree:
                    yield child
            else:
                yield tree

    def __call__(self):
        self.transform()
        return self.trees

    def truncate(self):
        for transformer in self.__transformers:
            transformer.truncate(*self.__prepare)
        return u''

    def __unicode__(self):
        return u"".join(map(lxml.html.tostring, self.__call__()))


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

    def truncate(self, name, text):
        pass


class ReferenceTransformationFilter(TransformationFilter):
    grok.baseclass()
    grok.name('reference')

    _read_only = False
    _reference_tracking = True

    def __init__(self, context, request):
        super(ReferenceTransformationFilter, self).__init__(context, request)
        self._reference_service = component.getUtility(IReferenceService)
        self._references_used = set()
        self._references = {}

    def _get_reference_name(self, name):
        return u' '.join((name, grok.name.bind().get(self.__class__)))

    def get_reference(self, link_name):
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
            if self._read_only:
                raise KeyError(u"Missing reference %s tagged %s" % (
                        self._reference_name, link_name))
            return self.new_reference()
        reference = self._references.get(link_name, None)
        if reference is not None:
            self._references_used.add(link_name)
        else:
            # This can happen if we copied direct html
            if self._read_only:
                raise KeyError(u"Missing reference %s tagged %s" % (
                        self._reference_name, link_name))
            return self.new_reference()
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
        self._reference_name = self._get_reference_name(name)
        self._references_used = set()
        self._references = dict(map(
                lambda r: (r.tags[1], r),
                filter(
                    lambda r: r.tags[0] == self._reference_name,
                    self._reference_service.get_references_from(
                        self.context,
                        name=self._reference_name))))

    def __call__(self, tree):
        pass

    def finalize(self):
        super(ReferenceTransformationFilter, self).finalize()
        if self._reference_tracking:
            for link_name, reference in self._references.items():
                if link_name not in self._references_used:
                    # Reference has not been used, remove it.
                    del self._reference_service.references[reference.__name__]

    def truncate(self, name, text):
        if not self._read_only:
            self._reference_service.delete_references(
                self.context, name=self._get_reference_name(name))
