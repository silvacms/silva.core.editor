# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import getSecurityManager

from five import grok
from silva.core import conf as silvaconf
from silva.core.interfaces import ISilvaLocalService
from silva.core.layout.jquery import IJQueryResources
from silva.core.layout.jsontemplate import IJsonTemplateResources
from zope import schema, interface
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import IFactory, getUtility
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class ICKEditorResources(IJQueryResources, IJsonTemplateResources):
    """ Javascript resources for CKEditor.
    """
    silvaconf.resource('ckeditor/ckeditor_source.js')


class ICKEditorViewResources(ICKEditorResources):
    """Javascript resources to load a CKEditor in a view.
    """
    silvaconf.resource('ckeditor/adapters/jquery.js')
    silvaconf.resource('editor.js')


tools_vocabulary = SimpleVocabulary([
    SimpleTerm(title='-- line separator --', value='/'),
    SimpleTerm(title='-- group separator --', value='-'),
    SimpleTerm(title='Save in Silva', value='SilvaSave'),
    SimpleTerm(title='Link a Silva content', value='SilvaLink'),
    SimpleTerm(title='Remove a link', value='SilvaUnlink'),
    SimpleTerm(title='Include a Silva (or remote) image', value='SilvaImage'),
    SimpleTerm(title='Include an anchor or Silva Index entry', value='SilvaAnchor'),
    SimpleTerm(title='Format using service settings', value='SilvaFormat'),
    SimpleTerm(title='Add an External Source', value='SilvaExternalSource'),
    SimpleTerm(title='Cut', value='Cut'),
    SimpleTerm(title='Copy', value='Copy'),
    SimpleTerm(title='Paste', value='Paste'),
    SimpleTerm(title='Paste Plain Text', value='PasteText'),
    SimpleTerm(title='Paste from Word', value='PasteFromWord'),
    SimpleTerm(title='Styles', value='Styles'),
    SimpleTerm(title='Font', value='Font'),
    SimpleTerm(title='Font Size', value='FontSize'),
    SimpleTerm(title='Bold', value='Bold'),
    SimpleTerm(title='Italic', value='Italic'),
    SimpleTerm(title='Underline', value='Underline'),
    SimpleTerm(title='Strike', value='Strike'),
    SimpleTerm(title='Numbered List', value='NumberedList'),
    SimpleTerm(title='Bulleted List', value='BulletedList'),
    SimpleTerm(title='Subscript', value='Subscript'),
    SimpleTerm(title='Superscript', value='Superscript'),
    SimpleTerm(title='Outdent', value='Outdent'),
    SimpleTerm(title='Indent', value='Indent'),
    SimpleTerm(title='Blockquote', value='Blockquote'),
    SimpleTerm(title='Special Characters', value='SpecialChar'),
    SimpleTerm(title='Undo', value='Undo'),
    SimpleTerm(title='Redo', value='Redo'),
    SimpleTerm(title='Find', value='Find'),
    SimpleTerm(title='Replace', value='Replace'),
    SimpleTerm(title='Select All', value='SelectAll'),
    SimpleTerm(title='Remove Formating', value='RemoveFormat'),
    SimpleTerm(title='Table', value='Table'),
    SimpleTerm(title='Horizontal Rule', value='HorizontalRule'),
    SimpleTerm(title='Smiley', value='Smiley'),
    SimpleTerm(title='Page Break', value='PageBreak'),
    SimpleTerm(title='Source', value='Source'),
    SimpleTerm(title='Maximize editor size', value='Maximize'),
    SimpleTerm(title='Online Spell Checker', value='Scayt'),
    SimpleTerm(title='About', value='About')])


def get_request():
    """!#@!$#!$#!@#!$!!!
    """
    return getSecurityManager().getUser().REQUEST


@grok.provider(IContextSourceBinder)
def skin_vocabulary(context):
    skins = [
            SimpleTerm(title='Kama', value='kama'),
            SimpleTerm(title='Office 2003', value='office2003'),
            SimpleTerm(title='v2', value='v2')]
    service = getUtility(ICKEditorService)
    # zope.schema sucks big times.
    request = get_request()
    for extension, base in service.get_custom_extensions(request):
        if hasattr(extension, 'skins'):
            for name, info in extension.skins.iteritems():
                path = info['path']
                if not path.endswith('/'):
                    path += '/'
                skins.append(
                    SimpleTerm(
                        title=info['title'],
                        value='%s,%s/%s' % (name, base, path)))
    return SimpleVocabulary(skins)


class ICKEditorHTMLAttribute(interface.Interface):
    """Describe an HTML attribute.
    """
    name = schema.TextLine(
        title=u"Attribute name",
        required=True)
    value = schema.TextLine(
        title=u"Attribute value",
        required=True)


class CKEditorHTMLAttribute(object):
    grok.implements(ICKEditorHTMLAttribute)

    def __init__(self, name, value):
        self.name = name
        self.value = value


grok.global_utility(
    CKEditorHTMLAttribute,
    provides=IFactory,
    name=ICKEditorHTMLAttribute.__identifier__,
    direct=True)


class ICKEditorFormat(interface.Interface):
    """Describe a CKEditor Format style.
    """
    name = schema.TextLine(
        title=u"Format name",
        required=True)
    element = schema.TextLine(
        title=u"HTML Element",
        required=True)
    attributes = schema.List(
        title=u"HTML Attributes",
        value_type=schema.Object(
            title=u"HTML Attribute",
            schema=ICKEditorHTMLAttribute),
        required=False)


class CKEditorFormat(object):
    grok.implements(ICKEditorFormat)

    def __init__(self, name, element, attributes):
        self.name = name
        self.element = element
        self.attributes = attributes


grok.global_utility(
    CKEditorFormat,
    provides=IFactory,
    name=ICKEditorFormat.__identifier__,
    direct=True)


class ICKEditorSettings(interface.Interface):

    toolbars = schema.List(
        title=u"Toolbars",
        description=u"Select tools to appear in the toolbars",
        value_type=schema.Choice(source=tools_vocabulary),
        default=[
            'SilvaSave', 'Source', '-',
            'Cut', 'Copy', 'Paste', 'PasteFromWord', '-',
            'Undo', 'Redo', '-',
            'Find', 'Replace', '-', 'Maximize', '/',
            'SilvaFormat', '-', 'Bold', 'Italic', 'Strike', '-',
            'NumberedList', 'BulletedList', '-',
            'Subscript', 'Superscript', '-',
            'Outdent', 'Indent', '-',
            'SilvaLink', 'SilvaUnlink', 'SilvaAnchor', 'SilvaImage',
            'SilvaExternalSource', 'Table',
            ],
        required=True)
    formats = schema.List(
        title=u"Formats",
        description=u"Styling formats",
        value_type=schema.Object(
            title=u"Format",
            schema=ICKEditorFormat),
        default=[
            CKEditorFormat(
                u'Title', 'h1', []),
            CKEditorFormat(
                u'Heading', 'h2', []),
            CKEditorFormat(
                u'Sub Heading', 'h3', []),
            CKEditorFormat(
                u'Paragraph Heading', 'h4', []),
            CKEditorFormat(
                u'Sub Paragraph Heading', 'h5', []),
            CKEditorFormat(
                u'Plain', 'p', [CKEditorHTMLAttribute('class', 'plain')]),
            CKEditorFormat(
                u'Lead', 'p', [CKEditorHTMLAttribute('class', 'lead')]),
            CKEditorFormat(
                u'Annotation', 'p', [CKEditorHTMLAttribute('class', 'annotation')]),
            ],
        required=True)
    contents_css = schema.TextLine(
        title=u"Contents CSS",
        description=u"CSS to apply to edited content in the editor",
        default=u'++static++/silva.core.editor/content.css',
        required=True)
    skin = schema.Choice(
        title=u"Editor skin",
        description=u"Editor theme",
        source=skin_vocabulary,
        required=True)


class ICKEditorService(ISilvaLocalService):
    """Service to store editor preferences.
    """

    def get_custom_extensions(request=None):
        """Return a generator, extension definition, base resource
        path for all CKEditor registered extension.
        """


class IText(IAttributeAnnotatable):
    """Editor rich text.
    """


class ITextIndexEntry(interface.Interface):
    """Reprensent an index entry in a text.
    """
    anchor = schema.TextLine(title=u"Anchor")
    title = schema.TextLine(title=u"Index title")


class ITextIndexEntries(interface.Interface):
    """Reprensent index entries in a text.
    """
    entries = schema.List(
        title=u"Index entries",
        value_type=schema.Object(schema=ITextIndexEntry))

    def add(anchor, title):
        """Add an new index.
        """

    def clear():
        """Clear all indexes.
        """
