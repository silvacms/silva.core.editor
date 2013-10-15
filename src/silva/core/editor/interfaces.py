# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope import schema, interface
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import IFactory, getUtility
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from silva.core import conf as silvaconf
from silva.ui.interfaces import ISilvaUIDependencies
from silva.core.interfaces import ISilvaLocalService
from silva.core.references.widgets import IReferenceUIResources

from js import ckeditor
from js import jquery
from zeam import jsontemplate


class ICKEditorResources(IReferenceUIResources):
    """ Javascript resources for CKEditor.
    """
    silvaconf.resource(jquery.jquery)
    silvaconf.resource(ckeditor.ckeditor)
    silvaconf.resource(jsontemplate.jsontemplate)


class ICKEditorSilvaUIResources(ISilvaUIDependencies, ICKEditorResources):
    """Javascript resources to load a CKEditor in silva.ui.
    """
    silvaconf.resource('editor.js')


tools_vocabulary = SimpleVocabulary([
    SimpleTerm(title='-- line separator --', value='/'),
    SimpleTerm(title='-- group separator --', value='-'),
    SimpleTerm(title='Save in Silva', value='SilvaSave'),
    SimpleTerm(title='Link a Silva content', value='SilvaLink'),
    SimpleTerm(title='Remove a link', value='SilvaUnlink'),
    SimpleTerm(title='Include a Silva (or remote) image', value='SilvaImage'),
    SimpleTerm(title='Include an anchor or Silva Index entry',
               value='SilvaAnchor'),
    SimpleTerm(title='Remove an anchor or Silva Index entry',
               value='SilvaRemoveAnchor'),
    SimpleTerm(title='Format using service settings', value='SilvaFormat'),
    SimpleTerm(title='Table styles', value='SilvaTableStyles'),
    SimpleTerm(title='Add an External Source', value='SilvaExternalSource'),
    SimpleTerm(title='Remove an External Source',
               value='SilvaRemoveExternalSource'),
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


@grok.provider(IContextSourceBinder)
def skin_vocabulary(context):
    skins = [SimpleTerm(title='Kama', value='kama'),
             SimpleTerm(title='Office 2003', value='office2003'),
             SimpleTerm(title='v2', value='v2')]
    service = getUtility(ICKEditorService)
    for extension, base in service.get_custom_extensions():
        if hasattr(extension, 'skins'):
            for name, info in extension.skins.iteritems():
                path = info['path']
                if not path.endswith('/'):
                    path += '/'
                skins.append(
                    SimpleTerm(
                        title=info['title'],
                        token=name,
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


class ICKEditorTableStyle(interface.Interface):
    """CKEditor Table style.
    """
    name = schema.TextLine(
        title=u"Style name",
        required=True)
    html_class = schema.TextLine(
        title=u"Class name",
        required=True)


class CKEditorTableStyle(object):
    grok.implements(ICKEditorTableStyle)

    def __init__(self, name, html_class):
        self.name = name
        self.html_class = html_class


grok.global_utility(
    CKEditorTableStyle,
    provides=IFactory,
    name=ICKEditorTableStyle.__identifier__,
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
            'SilvaFormat', 'SilvaTableStyles', '-',
            'Bold', 'Italic', 'Strike', '-',
            'NumberedList', 'BulletedList', '-',
            'Subscript', 'Superscript', '-',
            'Outdent', 'Indent', '-',
            'SilvaLink', 'SilvaUnlink', 'SilvaAnchor', '-',
            'SilvaImage', 'SilvaExternalSource', 'Table',
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
                u'Sub Sub Heading', 'h4', []),
            CKEditorFormat(
                u'Paragraph Heading', 'h5', []),
            CKEditorFormat(
                u'Sub Paragraph Heading', 'h6', []),
            CKEditorFormat(
                u'Plain', 'p', [CKEditorHTMLAttribute('class', 'plain')]),
            CKEditorFormat(
                u'Lead', 'p', [CKEditorHTMLAttribute('class', 'lead')]),
            CKEditorFormat(
                u'Annotation', 'p', [CKEditorHTMLAttribute('class',
                                                           'annotation')]),
            CKEditorFormat(
                u'Preformatted', 'pre', []),
            ],
        required=True)
    table_styles = schema.List(
        title=u"Table styles",
        description=u"Styling for tables",
        value_type=schema.Object(
            title=u"Table styles",
            schema=ICKEditorTableStyle),
        default=[
            CKEditorTableStyle(
                u'Plain', 'plain'),
            CKEditorTableStyle(
                u'List', 'list'),
            CKEditorTableStyle(
                u'Grid', 'grid'),
            CKEditorTableStyle(
                u'Datagrid', 'datagrid'),
            ],
        required=True)
    contents_css = schema.TextLine(
        title=u"Contents CSS",
        description=u"CSS to apply to edited content in the editor",
        default=u'++static++/silva.core.editor/content.css',
        required=True)
    editor_body_class = schema.TextLine(
        title=u"Editor iframe body class",
        description=u"""Sets the class attribute to be used
                     on the body element of the editing area.""",
        default=u'ckeditor_contents',
        required=True)
    skin = schema.Choice(
        title=u"Editor skin",
        description=u"Editor theme",
        source=skin_vocabulary,
        default='silva,++static++/silva.core.editor/skins/silva/',
        required=True)
    disable_colors = schema.Bool(
        title=u"Disable colors",
        description=u"Disallow users to use colors in the editor",
        default=True,
        required=True)
    startup_show_borders = schema.Bool(
        title=u"Borders around elements",
        description=u"""Whether to automatically enable the
                     'show border' command when the editor loads""",
        default=False,
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

    def get_transformer(context, request, type=None):
        """Return an instance of a ``ITransformer`` that can be used
        to manipulate the text. ``type`` is the filter to use for the
        transformer, default to ``IDisplayFilter``.
        """

    def render(context, request, type=None):
        """Transform the stored text to the given type and return
        it. Context must be the content or version on which the text
        is set. ``type`` is the filter to use for the transformer,
        default to ``IDisplayFilter``.
        """

    def introduction(context, request, max_length=300, type=None):
        """Transform the stored text and return only the introduction:
        the ``max_length`` first characters of the first paragraph.
        """

    def fulltext(context, request, type=None):
        """Return the text fulltext as a list of strings.
        """

    def save(context, request, text, type=None):
        """Tranform the input ``text`` to the given type and save
        it. Context must be the content or version on which the text
        is set. ``type`` is the filter to use to save the text,
        default to ``ISaveEditorFilter``.
        """

    def truncate(context, request, type=None):
        """Transform and set text to an empty string. ``type`` is the
        filter to use to truncate the text, default to
        ``ISaveEditorFilter``.
        """

    def save_raw_text(text):
        """Set the raw text as current text without any
        transformation.
        """

    def __unicode__():
        """Return stored text without any transformation.
        """

    def __len__():
        """Return the size of the stored text.
        """


class ITextIndexEntries(interface.Interface):
    """Reprensent index entries in a text.
    """

    def add(anchor, title):
        """Add an new index.
        """

    def clear():
        """Clear all indexes.
        """


class IPerTagAllowedAttributes(interface.Interface):
    """An allowed HTML tag and its allowed attributes and CSS properties
    """
    html_tag = schema.TextLine(
        title=u"Allowed HTML tag",
        required=True)
    html_attributes = schema.Set(
        title=u"Allowed HTML attributes",
        value_type=schema.TextLine(),
        required=False)
    css_properties = schema.Set(
        title=u"Allowed CSS properties",
        value_type=schema.TextLine(),
        required=False)


class PerTagAllowedAttributes(object):
    grok.implements(IPerTagAllowedAttributes)

    def __init__(self, html_tag, html_attributes=set(), css_properties=set()):
        self.html_tag = html_tag
        self.html_attributes = set(html_attributes)
        self.css_properties = set(css_properties)

    def __hash__(self):
        return hash(self.html_tag)

    def __eq__(self, other):
        if not isinstance(other, PerTagAllowedAttributes):
            return NotImplemented
        return self.html_tag == other.html_tag


grok.global_utility(
    PerTagAllowedAttributes,
    provides=IFactory,
    name=IPerTagAllowedAttributes.__identifier__,
    direct=True)
