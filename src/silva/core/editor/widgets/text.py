

from five import grok
from zope.interface import Interface

from silva.core.conf import schema as silvaschema

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



def register():
    registerSchemaField(HTMLSchemaField, silvaschema.IHTMLText)
