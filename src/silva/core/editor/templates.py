# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from infrae import rest
from silva.core.interfaces import ISilvaObject
from silva.core.views.interfaces import IVirtualSite
from zope.traversing.browser import absoluteURL


class CKEditorRESTReference(rest.REST):
    """Template for the reference widget.
    """
    grok.context(ISilvaObject)
    grok.name('silva.core.editor.widget.reference')

    template = grok.PageTemplate(filename='templates/ckeditorrestreference.pt')

    def default_namespace(self):
        return {'rest': self,
                'context': self.context,
                'request': self.request}

    def namespace(self):
        return {}

    def GET(self):
        self.root_url = IVirtualSite(self.request).get_root_url()
        self.container_url = absoluteURL(
            self.context.get_container(), self.request)
        return self.template.render(self)
