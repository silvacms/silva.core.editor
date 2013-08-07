# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core import conf as silvaconf

silvaconf.extension_name("silva.core.editor")
silvaconf.extension_title(u"Silva Core Editor")
silvaconf.extension_system()


class CKEditorExtension(object):
    base = '++static++/silva.core.editor'
    plugins = {
        'silvautils': 'plugins/silvautils',
        'silvalink': 'plugins/silvalink',
        'silvaimage': 'plugins/silvaimage',
        'silvaanchor': 'plugins/silvaanchor',
        'silvasave': 'plugins/silvasave',
        'silvaformat': 'plugins/silvaformat',
        'silvatablestyles': 'plugins/silvatablestyles',
        'silvadialog': 'plugins/silvadialog',
        }
    skins = {
        'silva': {'title': 'Silva default', 'path': 'skins/silva'}
        }

extension = CKEditorExtension()
