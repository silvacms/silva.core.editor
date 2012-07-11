# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
import collections

from five import grok
from infrae import rest
from persistent import Persistent
from silva.core.editor.interfaces import IText
from silva.core.editor.interfaces import ITextIndexEntries
from silva.core.editor.transform.interfaces import ITransformerFactory
from silva.core.editor.transform.interfaces import IDisplayFilter
from silva.core.editor.transform.interfaces import ISaveEditorFilter
from silva.core.editor.transform.interfaces import IInputEditorFilter
from silva.core.editor.utils import html_truncate_node
from silva.core.interfaces import IVersionedContent
from silva.core.messages.interfaces import IMessageService
from silva.core.references.interfaces import IReferenceService
from silva.translations import translate as _
from zope.component import getMultiAdapter, getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


IndexEntry = collections.namedtuple('IndexEntry', ['anchor', 'title'])

class TextIndexEntries(grok.Annotation):
    grok.implements(ITextIndexEntries)
    grok.context(IText)

    def __init__(self, *args):
        super(TextIndexEntries, self).__init__(*args)
        self.entries = []

    def add(self, anchor, title):
        self.entries.append(IndexEntry(anchor, title))

    def clear(self):
        if self.entries:
            self.entries = []


class Text(Persistent):
    grok.implements(IText)

    def __init__(self, name, text=u""):
        self.__name = name
        self.__text = text

    def get_transformer(self, context, request, type=None):
        if type is None:
            type = IDisplayFilter
        factory = getMultiAdapter((context, request), ITransformerFactory)
        return factory(self.__name, self, unicode(self), type)

    def render(self, context, request, type=None):
        return unicode(self.get_transformer(context, request, type))

    def render_introduction(self, context, request, max_length=300, type=None):
        transformer = self.get_transformer(context, request, type)
        transformer.restrict('//p[1]')
        transformer.visit(lambda node: html_truncate_node(node, max_length))
        return unicode(transformer)

    def save(self, context, request, text, type=None):
        if type is None:
            type = ISaveEditorFilter
        factory = getMultiAdapter((context, request), ITransformerFactory)
        return self.save_raw_text(factory(self.__name, self, text, type))

    def save_raw_text(self, text):
        self.__text = unicode(text)
        return self.__text

    def truncate(self, context, request, type=None):
        if type is None:
            type = ISaveEditorFilter
        factory = getMultiAdapter((context, request), ITransformerFactory)
        transformer = factory(self.__name, self, None, type)
        self.save_raw_text(transformer.truncate())

    def __str__(self):
        return str(self.__text)

    def __unicode__(self):
        return self.__text


class CKEditorRESTSave(rest.REST):
    """Save the editor result.
    """
    grok.context(IVersionedContent)
    grok.name('silva.core.editor.save')

    def POST(self):
        version = self.context.get_editable()
        if version is None:
            return self.json_response(
                {'status': 'failure', 'alert': 'No editable version !'})

        # Transform and save text.
        for key in self.request.form.keys():
            text = getattr(version, key)
            assert IText.providedBy(text), u'Trying to save text to non text attribute'
            text.save(
                version,
                self.request,
                unicode(self.request.form[key], 'utf-8'),
                type=ISaveEditorFilter)
        notify(ObjectModifiedEvent(version))
        service = getUtility(IMessageService)
        service.send(_("Changes saved."), self.request, namespace=u'feedback')

        # Transform and input saved text (needed to get update to date
        # reference information)
        response = {'status': 'success'}
        for key in self.request.form.keys():
            text = getattr(version, key)
            response[key] = text.render(
                version, self.request, type=IInputEditorFilter)
        return self.json_response(response)


