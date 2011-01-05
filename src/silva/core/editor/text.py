# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


import lxml
import uuid

from five import grok
from infrae import rest
from silva.core.editor.interfaces import ISavingFilter
from silva.core.interfaces import ISilvaObject, IVersion
from zope import component
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.publisher.interfaces.browser import IBrowserRequest
from silva.core.references.interfaces import IReferenceService
from silva.core.references.reference import get_content_from_id


class Text(object):
    grok.implements(IAttributeAnnotatable)

    def __init__(self, text=u""):
        self.__text = text

    def save(self, text):
        self.__text = text

    def __str__(self):
        return str(self.__text)

    def __unicode__(self):
        return self.__text


class Transformer(grok.MultiSubscriber):
    grok.baseclass()
    grok.implements(ISavingFilter)
    grok.provides(ISavingFilter)
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


class ReferenceTransformer(Transformer):
    grok.baseclass()
    reference_tag = 'reference'

    def __init__(self, context, request):
        super(ReferenceTransformer, self).__init__(context, request)
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
        super(ReferenceTransformer, self).prepare(name, text)
        self._reference_name = u' '.join((name, self.reference_tag))
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
        super(ReferenceTransformer, self).finalize()
        for link_name, reference in self._references.items():
            if link_name not in self._references_used:
                # Reference has not been used, remove it.
                del self._reference_service.references[reference.__name__]


class LinkTransfomer(ReferenceTransformer):
    grok.order(10)
    reference_tag = 'link'

    def __call__(self, tree):
        for link in tree.xpath('//a[@class="link"]'):
            if 'silva_reference' in link.attrib:
                name, reference = self.get_reference(
                    link.attrib['silva_reference'])
                if reference is not None:
                    target_id = link.attrib['silva_target']
                    try:
                        target_id = int(str(target_id))
                        assert get_content_from_id(target_id) is not None
                    except (ValueError, AssertionError):
                        # Invalid target id, set it as zero (broken)
                        target_id = 0
                else:
                    # Invalid reference. We create a new one and mark the
                    # target as broken
                    name, reference = self.get_reference('new')
                    target_id = 0
                if target_id != reference.target_id:
                    reference.set_target_id(target_id)
                link.attrib['silva_reference'] = name



class CKEditorRESTSave(rest.REST):
    """Save the editor result.
    """
    grok.context(ISilvaObject)
    grok.name('silva.core.editor.save')


    def POST(self):
        version = self.context.get_editable()
        saved = {}
        assert version is not None
        transformers = grok.queryOrderedSubscribers(
            (version, self.request), ISavingFilter)
        for key in self.request.form.keys():
            text = getattr(version, key)
            tree = lxml.html.fromstring(unicode(self.request.form[key]))
            for transformer in transformers:
                transformer.prepare(key, text)
            for transformer in transformers:
                transformer(tree)
            for transformer in transformers:
                transformer.finalize()
            saved[key] = lxml.html.tostring(tree)
        print saved
        return self.json_response(saved)
