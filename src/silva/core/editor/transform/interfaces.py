# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import interface


class ITransformationFilter(interface.Interface):
    """Transformation filter.
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


class IOutputEditorFilter(IEditorFilter):
    """Filter to retrieve text from the editor.
    """
