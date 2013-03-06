# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zope import interface


class ITransformerFactory(interface.Interface):
    """Create a transformer to transform some text for a content.
    """

    def __init__(context, request):
        """Adapt a content and a request.
        """

    def __call__(name, text, data, interface):
        """Return a transformer bound to those data.
        """

class ITransformer(interface.Interface):
    """Transformer.
    """

    def restrict(xpath):
        """Restrict imput lxml trees to the matching xpath.
        """

    def visit(function):
        """Visit each input lxml trees, apply a function on it.
        """

    def __call__():
        """Generate transformed lxml trees (and return thoses).
        """

    def truncate():
        """Truncate the trees.
        """

    def __unicode__():
        """Return transformed HTML.
        """


class ITransformationFilter(interface.Interface):
    """Transformation filter.
    """

    def __init__(context, request):
        """Adapt a content and a request.
        """

    def prepare(name, text):
        """Prepare the process of transformation of the text object
        called name.
        """

    def __call__(tree):
        """Transform the given LXML tree.
        """

    def finalize():
        """Finialize the transformation process.
        """

    def truncate(name, text):
        """Truncate the text. The filter will remove any external data
        associated to the named text (references, code sources).
        """


class IDisplayFilter(ITransformationFilter):
    """Filter to display text to the user.
    """


class IEditorFilter(ITransformationFilter):
    """Filter to edit text with the editor.
    """


class IInputEditorFilter(IEditorFilter):
    """Filter to send text to the editor.
    """


class ISaveEditorFilter(IEditorFilter):
    """Filter text from the editor to be saved.
    """


class ISilvaXMLFilter(ITransformationFilter):
    """ Filter for silva xml import/export
    """


class ISilvaXMLExportFilter(ISilvaXMLFilter):
    """ silva xml export filter
    """


class ISilvaXMLImportFilter(ISilvaXMLFilter):
    """ silva xml import filter
    """

