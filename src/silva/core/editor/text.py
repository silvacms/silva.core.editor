# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from infrae import rest
from persistent import Persistent
from silva.core.editor.interfaces import IText, ITextIndexEntries, ITextIndexEntry
from silva.core.editor.transform.interfaces import ITransformer, IDisplayFilter
from silva.core.editor.transform.interfaces import ISaveEditorFilter, IInputEditorFilter
from silva.core.interfaces import IVersionedContent
from silva.core.messages.interfaces import IMessageService
from silva.translations import translate as _
from zope.component import getMultiAdapter, getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from silva.core.editor.utils import html_truncate


class TextIndexEntry(object):
    grok.implements(ITextIndexEntry)

    def __init__(self, anchor, title):
        self.anchor = anchor
        self.title = title


class TextIndexEntries(grok.Annotation):
    grok.implements(ITextIndexEntries)
    grok.context(IText)

    def __init__(self, *args):
        super(TextIndexEntries, self).__init__(*args)
        self.entries = []

    def add(self, anchor, title):
        self.entries.append(TextIndexEntry(anchor, title))

    def clear(self):
        if self.entries:
            self.entries = []


class Text(Persistent):
    grok.implements(IText)

    def __init__(self, name, text=u""):
        self.__name = name
        self.__text = text

    def render(self, context, request, type=None):
        if type is None:
            type = IDisplayFilter
        transformer = getMultiAdapter((context, request), ITransformer)
        return transformer.data(self.__name, self, unicode(self), type)

    def render_intro(self, context, request, type=None, max_length=None):
        if type is None:
            type = IDisplayFilter
        transformer = getMultiAdapter((context, request), ITransformer)
        rendered = transformer.part(
            self.__name, self, unicode(self), '//p[1]', type)
        if max_length is not None:
            return html_truncate(max_length, rendered)
        return rendered

    def save_raw_text(self, text):
        self.__text = text

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
        transformer = getMultiAdapter((version, self.request), ITransformer)
        for key in self.request.form.keys():
            text = getattr(version, key)
            assert IText.providedBy(text), u'Trying to save text to non text attribute'
            text.save_raw_text(transformer.data(
                key,
                text,
                unicode(self.request.form[key], 'utf-8'),
                ISaveEditorFilter))
        notify(ObjectModifiedEvent(version))
        service = getUtility(IMessageService)
        service.send(_("Changes saved."), self.request, namespace=u'feedback')

        # Transform and input saved text (needed to get update to date
        # reference information)
        response = {'status': 'success'}
        for key in self.request.form.keys():
            text = getattr(version, key)
            response[key] = transformer.data(key, text, unicode(text), IInputEditorFilter)
        return self.json_response(response)
