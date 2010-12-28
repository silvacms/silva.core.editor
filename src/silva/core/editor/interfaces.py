# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf
from silva.core.layout.jquery.interfaces import IJQueryResources
from silva.core.interfaces import ISilvaLocalService
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope import schema, interface


class ICKEditorResources(IJQueryResources):
    """ Resource for CKEditor.
    """
    silvaconf.resource('json-template.js')
    silvaconf.resource('ckeditor/ckeditor_source.js')
    silvaconf.resource('ckeditor/adapters/jquery.js')
    silvaconf.resource('editor.js')


tools_vocabulary = SimpleVocabulary([
    SimpleTerm(title='-- line separator --', value='/'),
    SimpleTerm(title='-- group separator --', value='-'),
    SimpleTerm(title='Save in Silva', value='SilvaSave'),
    SimpleTerm(title='Link a Silva content', value='SilvaLink'),
    SimpleTerm(title='Include a Silva (or remote) image', value='SilvaImage'),
    SimpleTerm(title='Include an anchor or Silva Index entry', value='SilvaAnchor'),
    SimpleTerm(title='Cut', value='Cut'),
    SimpleTerm(title='Copy', value='Copy'),
    SimpleTerm(title='Paste', value='Paste'),
    SimpleTerm(title='Paste Plain Text', value='PasteText'),
    SimpleTerm(title='Paste from Word', value='PasteFromWord'),
    SimpleTerm(title='Styles', value='Styles'),
    SimpleTerm(title='Format', value='Format'),
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

skin_vocabulary = SimpleVocabulary([
    SimpleTerm(title='Kama', value='kama'),
    SimpleTerm(title='Office 2003', value='office2003'),
    SimpleTerm(title='v2', value='v2')])


class ICKEditorSettings(interface.Interface):

    toolbars = schema.List(
        title=u"Toolbars",
        description=u"Select tools to appear in the toolbars",
        value_type=schema.Choice(source=tools_vocabulary),
        default=['SilvaSave', 'Source', '-',
                 'Cut', 'Copy', 'Paste', '-',
                 'Undo', 'Redo', '-',
                 'Find', 'Replace', '/',
                 'Format', '-', 'Bold', 'Italic', 'Strike', '-',
                 'NumberedList', 'BulletedList', '-',
                 'Outdent', 'Indent', '-',
                 'SilvaLink', 'SilvaAnchor', 'SilvaImage'],
        required=True)
    skin = schema.Choice(
        title=u"Editor skin",
        description=u"Editor theme",
        source=skin_vocabulary,
        default='kama',
        required=True)


class ICKEditorService(ISilvaLocalService):
    """Service to store editor preferences.
    """
