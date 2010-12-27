# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf

silvaconf.extension_name("silva.core.editor")
silvaconf.extension_title(u"Silva CORE Editor")
silvaconf.extension_system()

PLUGINS = {
    'silvalink': '++resource++silva.core.editor/plugins/silvalink',
    'silvasave': '++resource++silva.core.editor/plugins/silvasave'}
