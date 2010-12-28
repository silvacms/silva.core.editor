# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from pkg_resources import iter_entry_points
import logging

from five import grok
from infrae import rest
from silva.core import conf as silvaconf
from silva.core.interfaces import ISilvaObject
from silva.core.views.interfaces import IVirtualSite
from silva.core.services.base import SilvaService
from silva.core.editor.interfaces import ICKEditorService, ICKEditorSettings
from zope.component import getUtility
from zope.schema.fieldproperty import FieldProperty
from zeam.form import silva as silvaforms

logger = logging.getLogger('silva.core.editor')


class CKEditorService(SilvaService):
    """Configure the editor service.
    """
    grok.implements(ICKEditorService)
    meta_type = 'Silva CKEditor Service'
    default_service_identifier = 'service_ckeditor'
    silvaconf.icon('service.png')

    manage_options = (
        {'label': 'Editor settings',
         'action': 'manage_settings'},) + SilvaService.manage_options


    toolbars = FieldProperty(ICKEditorSettings['toolbars'])
    skin = FieldProperty(ICKEditorSettings['skin'])

    def get_toolbars_configuration(self):
        """Return toolbar configuration.
        """
        # Use toolbars variable, split list on "/" like CKEditor expect.
        splitted_list = []
        raw_list = list(self.toolbars)
        while "/" in raw_list:
            position = raw_list.index("/")
            if position:
                splitted_list.append(raw_list[:position])
                splitted_list.append("/")
            raw_list = raw_list[position + 1:]
        if raw_list:
            splitted_list.append(raw_list)
        return splitted_list

    def get_extra_paths(self, request=None):
        """Return a list of plugin to enable, with their loading path.
        """
        base = ''
        if request is not None:
            base = IVirtualSite(request).get_root().absolute_url_path()
        extra_paths = {}
        for load_entry in iter_entry_points('silva.core.editor.plugins'):
            entry_paths = load_entry.load()
            if not isinstance(entry_paths, dict):
                logger.error("Invalid plugin settings.")
                continue
            for name, path in entry_paths.iteritems():
                if not path.endswith('/'):
                    path += '/'
                extra_paths[name] = '/'.join((base, path))
        return extra_paths


class CKEditorSettings(silvaforms.ZMIForm):
    """Update the settings.
    """
    grok.name('manage_settings')
    grok.context(ICKEditorService)

    label = u"CKEditor setttings"
    description = u"You can from here modify the WYSIYG editor settings."
    ignoreContent = False
    fields = silvaforms.Fields(ICKEditorSettings)
    actions = silvaforms.Actions(silvaforms.EditAction())


class CKEditorRESTConfiguration(rest.REST):
    grok.context(ISilvaObject)
    grok.name('silva.core.editor.configuration')

    def GET(self):
        service = getUtility(ICKEditorService)
        return self.json_response(
            {'toolbars': service.get_toolbars_configuration(),
             'paths': service.get_extra_paths(self.request),
             'extraPlugins': 'silvaimage,silvalink,silvasave',
             'skin': service.skin})
