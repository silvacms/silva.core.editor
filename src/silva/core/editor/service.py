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

FORMAT_IDENTIFIER_BASE = 'format%0004d'


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
    formats = FieldProperty(ICKEditorSettings['formats'])
    contents_css = FieldProperty(ICKEditorSettings['contents_css'])
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

    def get_custom_extensions(self, request=None):
        """Return the custom extensions, and the base URL to their
        resource folder.
        """
        base = ''
        if request is not None:
            base = IVirtualSite(request).get_root().absolute_url_path()
            if base.endswith('/'):
                # If base is only '/', we will end up with two '/',
                # creating an invalid URL for CKEditor resource
                # manager.
                base = base[:-1]
        for load_entry in iter_entry_points('silva.core.editor.extension'):
            extension = load_entry.load()
            extension_base = base
            if hasattr(extension, 'base'):
                extension_base = '/'.join((base, extension.base))
            yield extension, extension_base

    def get_custom_plugins(self, request=None):
        """Return a list of plugin to enable, with their loading path.
        """
        extra_plugins = {}
        for extension, base in self.get_custom_extensions(request):
            if hasattr(extension, 'plugins'):
                for name, path in extension.plugins.iteritems():
                    if not path.endswith('/'):
                        path += '/'
                    extra_plugins[name] = '/'.join((base, path))
        return extra_plugins

    def get_formats(self):
        count = 0
        order = []
        result = {'order': order}
        for format in self.formats:
            attributes_result = {}
            format_result = {
                'name': format.name,
                'element': format.element}
            for attribute in format.attributes:
                attributes_result[attribute.name] = attribute.value
            if attributes_result:
                format_result['attributes'] = attributes_result
            format_identifier = FORMAT_IDENTIFIER_BASE % count
            result[format_identifier] =  format_result
            order.append(format_identifier)
            count += 1
        return result


class CKEditorSettings(silvaforms.ZMIForm):
    """Update the settings.
    """
    grok.name('manage_settings')
    grok.context(ICKEditorService)

    label = u"CKEditor settings"
    description = u"You can from here modify the WYSIYG editor settings."
    ignoreContent = False
    fields = silvaforms.Fields(ICKEditorSettings)
    actions = silvaforms.Actions(silvaforms.EditAction())


class CKEditorRESTConfiguration(rest.REST):
    grok.context(ISilvaObject)
    grok.name('silva.core.editor.configuration')

    def GET(self):
        service = getUtility(ICKEditorService)
        plugins_path = service.get_custom_plugins(self.request)
        return self.json_response(
            {'toolbars': service.get_toolbars_configuration(),
             'paths': plugins_path,
             'contents_css': service.contents_css,
             'formats': service.get_formats(),
             'plugins': ','.join(plugins_path.keys()),
             'skin': service.skin})
