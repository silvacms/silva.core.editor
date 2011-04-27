# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.testing import SilvaLayer
import silva.core.editor


class SilvaEditorLayer(SilvaLayer):
    default_packages = SilvaLayer.default_packages + [
        'silva.core.editor',
        ]

FunctionalLayer = SilvaEditorLayer(silva.core.editor)
