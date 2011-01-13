# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from infrae import rest
from persistent import Persistent
from silva.core.editor.interfaces import IText, ITextIndexEntries, ITextIndexEntry
from silva.core.editor.transform.interfaces import ITransformer, ISaveEditorFilter
from silva.core.interfaces import IVersionedContent
from silva.core.messages.interfaces import IMessageService
from silva.translations import translate as _
from zope.component import getMultiAdapter, getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


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

    def __init__(self, text=u""):
        self.__text = text

    def save(self, text):
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
        transformer = getMultiAdapter((version, self.request), ITransformer)
        for key in self.request.form.keys():
            text = getattr(version, key)
            text.save(transformer.data(
                key,
                text,
                unicode(self.request.form[key], 'utf-8'),
                ISaveEditorFilter))
        notify(ObjectModifiedEvent(version))
        service = getUtility(IMessageService)
        service.send(_("Changes saved."), self.request, namespace=u'feedback')
        return self.json_response({'status': 'success'})
