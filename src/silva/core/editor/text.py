# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from infrae import rest
from persistent import Persistent
from silva.core.editor.interfaces import IText, ITextIndexEntries, ITextIndexEntry
from silva.core.editor.transform import transform
from silva.core.editor.transform.interfaces import IOutputEditorFilter
from silva.core.interfaces import IVersionedContent
from silva.core.messages.interfaces import IMessageService
from zope import component


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
        assert version is not None
        for key in self.request.form.keys():
            text = getattr(version, key)
            text.save(transform(
                key,
                self.request.form[key],
                text,
                version,
                self.request,
                IOutputEditorFilter))
        service = component.getUtility(IMessageService)
        service.send("Changes saved.", self.request, namespace='feedback')
        return self.json_response({'status': 'success'})
