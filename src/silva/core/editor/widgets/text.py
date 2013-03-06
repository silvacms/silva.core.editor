# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt


from five import grok
from zope.interface import Interface

from silva.core.conf import schema as silvaschema
from silva.core.interfaces import IVersion

from zeam.form.ztk.fields import SchemaField, SchemaFieldWidget
from zeam.form.ztk.fields import registerSchemaField


class HTMLSchemaField(SchemaField):
    """ Field to input HTML
    """


class HTMLInputWidget(SchemaFieldWidget):
    grok.adapts(HTMLSchemaField, Interface, Interface)
    grok.name(u'input')

    def valueToUnicode(self, value):
        return unicode(value)

    def update(self):
        super(HTMLInputWidget, self).update()
        content = self.form.context
        if IVersion.providedBy(content):
            content = content.get_silva_object()
        self.configuration = content.meta_type


def register():
    registerSchemaField(HTMLSchemaField, silvaschema.IHTMLText)
