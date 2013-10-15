# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt
import collections

from five import grok
from infrae import rest
from persistent import Persistent
from zope.component import getMultiAdapter, getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from silva.core.interfaces import IVersionedContent
from silva.core.messages.interfaces import IMessageService
from silva.translations import translate as _

from .interfaces import IText
from .interfaces import ITextIndexEntries
from .transform.interfaces import ITransformerFactory
from .transform.interfaces import IDisplayFilter
from .transform.interfaces import ISaveEditorFilter
from .transform.interfaces import IInputEditorFilter
from .utils import html_truncate_words, html_truncate_characters
from .utils import html_extract_text, downgrade_title_nodes


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

    def render(self, context, request, downgrade_titles=False, type=None):
        transformer = self.get_transformer(context, request, type)
        if downgrade_titles:
            transformer.transform()
            transformer.visit(downgrade_title_nodes)
        return unicode(transformer)

    def introduction(self, context, request, max_length=300, max_words=None, type=None):
        if max_words is not None:
            count = max_words
            truncate = html_truncate_words
        else:
            count = max_length
            truncate = html_truncate_characters
        transformer = self.get_transformer(context, request, type)
        transformer.restrict('//p[1]')
        transformer.visit(lambda node: truncate(node, count))
        return unicode(transformer)

    def fulltext(self, context, request, type=None):
        transformer = self.get_transformer(context, request, type)
        fulltext = []
        transformer.visit(lambda node: html_extract_text(node, fulltext))
        return fulltext

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

    def __len__(self):
        return len(self.__text)

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
        # This view should be only available on versioned content have
        # a text block.
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


