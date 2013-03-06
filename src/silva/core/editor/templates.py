# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from infrae import rest
from silva.core.interfaces import ISilvaObject
from silva.core.views.interfaces import IVirtualSite
from zope.traversing.browser import absoluteURL

grok.templatedir('templates')


class CKEditorRESTReference(rest.RESTWithTemplate):
    """Template for the reference widget.
    """
    grok.context(ISilvaObject)
    grok.name('silva.core.editor.widget.reference')

    def GET(self):
        self.root_url = IVirtualSite(self.request).get_root_url()
        self.container_url = absoluteURL(
            self.context.get_container(), self.request)
        return self.template.render(self)
