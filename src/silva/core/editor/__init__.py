# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf

silvaconf.extension_name("silva.core.editor")
silvaconf.extension_title(u"Silva CORE Editor")
silvaconf.extension_system()

PLUGINS = {
    'silvareference': '++resource++silva.core.editor/plugins/silvareference',
    'silvalink': '++resource++silva.core.editor/plugins/silvalink',
    'silvaimage': '++resource++silva.core.editor/plugins/silvaimage',
    'silvaanchor': '++resource++silva.core.editor/plugins/silvaanchor',
    'silvasave': '++resource++silva.core.editor/plugins/silvasave'
    }
