# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import interface


class ITransformer(interface.Interface):
    """Transform some text for a content.
    """

    def __init__(context, request):
        """Adapt a content and a request.
        """

    def data(name, text, data, interface):
        """Transform for the named name text object the given data,
        using the filters specified by interface.
        """

    def attribute(name, interface):
        """Transform the attribute named name from the content using
        the filters specified by interface.
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
