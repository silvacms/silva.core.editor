# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from pkg_resources import iter_entry_points
import logging
import operator

from five import grok
from zope import schema
from zope.component import getUtility
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import IObjectAddedEvent, ObjectCreatedEvent
from zope.schema.fieldproperty import FieldProperty
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.traversing.browser import absoluteURL

from AccessControl.security import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from OFS.Folder import Folder
from zExceptions import Redirect

from infrae import rest
from silva.core import conf as silvaconf
from silva.core.interfaces import ISilvaObject
from silva.core.services.base import SilvaService, ZMIObject
from silva.core.views.interfaces import IVirtualSite
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zeam.form.ztk.actions import EditAction

from .interfaces import ICKEditorService
from .interfaces import ICKEditorSettings
from .utils import HTML_TAGS_WHITELIST
from .utils import HTML_ATTRIBUTES_WHITELIST
from .utils import CSS_ATTRIBUTES_WHITELIST


logger = logging.getLogger('silva.core.editor')
FORMAT_IDENTIFIER_BASE = 'format%0004d'
TABLE_STYLE_IDENTIFIER_BASE = 'table_style_%0004d'


class CKEditorConfiguration(ZMIObject):
    """ A CKEditor configuration
    """
    security = ClassSecurityInfo()
    silvaconf.factory('manage_addCKEditorConfiguration')
    silvaconf.zmi_addable(False)
    meta_type = 'Silva CKEditor Configuration'

    manage_options = (
        {'label': 'Editor configuration',
         'action': 'manage_configuration'},) + ZMIObject.manage_options

    toolbars = FieldProperty(ICKEditorSettings['toolbars'])
    formats = FieldProperty(ICKEditorSettings['formats'])
    table_styles = FieldProperty(ICKEditorSettings['table_styles'])
    contents_css = FieldProperty(ICKEditorSettings['contents_css'])
    skin = FieldProperty(ICKEditorSettings['skin'])
    disable_colors = FieldProperty(ICKEditorSettings['disable_colors'])
    startup_show_borders = FieldProperty(
        ICKEditorSettings['startup_show_borders'])
    editor_body_class = FieldProperty(ICKEditorSettings['editor_body_class'])

    def __init__(self, id, title=None):
        self.id = id
        self.title = title

    def getId(self):
        return self.id

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
            result[format_identifier] = format_result
            order.append(format_identifier)
            count += 1
        return result

    def get_table_styles(self):
        count = 0
        order = []
        results = {}
        for table_style in self.table_styles:
            table_style_result = {
                'name': table_style.name,
                'html_class': table_style.html_class
            }
            table_style_identifier = TABLE_STYLE_IDENTIFIER_BASE % count
            results[table_style_identifier] = table_style_result
            order.append(table_style_identifier)
            count += 1
        results['order'] = order
        return results


InitializeClass(CKEditorConfiguration)


def manage_addCKEditorConfiguration(self, id, REQUEST=None):
    config = CKEditorConfiguration(id)
    self._setObject(id, config)
    config = self._getOb(id)
    notify(ObjectCreatedEvent(config))
    return config


class CKEditorService(Folder, SilvaService):
    """Configure the editor service.
    """
    grok.implements(ICKEditorService)
    grok.name('service_ckeditor')
    meta_type = 'Silva CKEditor Service'
    silvaconf.icon('service.png')

    manage_options = (
        {'label': 'Editor settings',
         'action': 'manage_settings'},
        {'label': 'HTML Sanitizer configuration',
         'action': 'manage_html_sanitizer'},) + SilvaService.manage_options

    _config_declarations = None
    _allowed_html_tags = None
    _allowed_html_attributes = None
    _allowed_css_attributes = None

    def __init__(self, *args, **kw):
        Folder.__init__(self, *args, **kw)
        SilvaService.__init__(self, *args, **kw)
        self._config_declarations = {}
        self._allowed_html_tags = set(HTML_TAGS_WHITELIST)
        self._allowed_html_attributes = set(HTML_ATTRIBUTES_WHITELIST)
        self._allowed_css_attributes = set(CSS_ATTRIBUTES_WHITELIST)

    def get_configuration(self, name):
        names = [name]
        informations = self._config_declarations.get(name)
        if informations:
            names.extend(informations[1])

        ids = self.objectIds()
        for candidate in names:
            if candidate in ids:
                return self._getOb(candidate)
        return self._getOb('default')

    def get_configuration_declaration(self, name):
        return self._config_declaration.get(name)

    def declare_configuration(self, name, fallbacks=None, title=None):
        self._config_declarations[name] = (title or name, fallbacks or [])
        self._p_changed = True

    def available_configurations(self):
        for name, info in self._config_declarations.iteritems():
            if not hasattr(self, name):
                yield name, info

    def get_custom_extensions(self):
        """Return the custom extensions, and the base URL to their
        resource folder.
        """
        for load_entry in iter_entry_points('silva.core.editor.extension'):
            extension = load_entry.load()
            extension_base = ''
            if hasattr(extension, 'base'):
                extension_base = extension.base
            yield extension, extension_base

    def get_custom_plugins(self):
        """Return a list of plugin to enable, with their loading path.
        """
        extra_plugins = {}
        for extension, base in self.get_custom_extensions():
            if hasattr(extension, 'plugins'):
                for name, path in extension.plugins.iteritems():
                    if not path.endswith('/'):
                        path += '/'
                    extra_plugins[name] = '/'.join((base, path))
        return extra_plugins

    def set_allowed_html_tags(self, tags):
        self._allowed_html_tags = set(tags)

    def set_allowed_html_attributes(self, attributes):
        self._allowed_html_attributes = set(attributes)

    def set_allowed_css_attributes(self, attributes):
        self._allowed_css_attributes = set(attributes)

    def get_allowed_html_tags(self):
        return self._allowed_html_tags

    def get_allowed_html_attributes(self):
        return self._allowed_html_attributes

    def get_allowed_css_attributes(self):
        return self._allowed_css_attributes


InitializeClass(CKEditorService)


@grok.provider(IContextSourceBinder)
def configurations_source(context):
    configurations = list(context.available_configurations())
    configurations.sort(key=operator.itemgetter(0))
    return SimpleVocabulary([
        SimpleTerm(value=name, token=name, title=info[0])
        for name, info in configurations])


class ICKEditorConfigurations(Interface):
    config = schema.Choice(title=u'Configuration',
                           source=configurations_source,
                           required=True)


class CKEditorServiceConfigurationManager(silvaforms.ZMIComposedForm):
    grok.context(ICKEditorService)
    grok.name('manage_settings')

    label = _(u"Manage CKEditor configurations")
    description = _(u"You can from here modify the WYSIYG editor settings.")


class CKEditorServiceAddConfiguration(silvaforms.ZMISubForm):
    grok.context(ICKEditorService)
    grok.view(CKEditorServiceConfigurationManager)
    grok.order(20)

    label = _(u"Add a configuration")
    description = _(u"Add a specific editor configuration "
                    u"for a content type in Silva.")
    ignoreContent = False
    fields = silvaforms.Fields(ICKEditorConfigurations)

    def available(self):
        return bool(self.fields['config'].getChoices(self))

    @silvaforms.action(title=_(u'Add'))
    def add(self):
        data, errors = self.extractData()
        if errors:
            self.status = _(u'There were errors')
            return silvaforms.FAILURE

        name = data['config']
        factory = self.context.manage_addProduct['silva.core.editor']
        factory.manage_addCKEditorConfiguration(name)
        return silvaforms.SUCCESS


class EditConfigurationAction(silvaforms.Action):
    title = _(u'Edit')
    description = _(u'edit the selected configuration')

    def __call__(self, form, config, line):
        raise Redirect(
            absoluteURL(config, form.request) + '/manage_configuration')


class RemoveConfigurationAction(silvaforms.Action):
    title = _(u'Remove')
    description = _(u'remove the selected configuration')

    def __call__(self, form, config, line):
        identifier = config.getId()
        if identifier == 'default':
            raise silvaforms.ActionError(
                _('You cannot remove the default configuration'))
        form.context.manage_delObjects([identifier])
        return silvaforms.SUCCESS


class IConfigurationListItemFields(Interface):
    id = schema.TextLine(title=u'Name')


class CKEditorServiceEditConfigurations(silvaforms.ZMISubTableForm):
    grok.context(ICKEditorService)
    grok.view(CKEditorServiceConfigurationManager)
    grok.order(10)

    ignoreContent = False
    label = _(u"Manage existing configurations")
    description = _(u"Edit or remove editor configuration for the given Silva "
                    u"content types.")
    mode = silvaforms.DISPLAY
    tableFields = silvaforms.Fields(IConfigurationListItemFields)
    tableActions = silvaforms.TableActions(
        EditConfigurationAction(),
        RemoveConfigurationAction())

    def getItems(self):
        return list(self.context.objectValues(
            spec=CKEditorConfiguration.meta_type))


class CKEditorEditConfiguration(silvaforms.ZMIForm):
    """Update the settings.
    """
    grok.name('manage_configuration')
    grok.context(CKEditorConfiguration)

    label = _(u"CKEditor settings")
    description = _(u"You can from here modify the WYSIYG editor settings.")
    ignoreContent = False
    fields = silvaforms.Fields(ICKEditorSettings)
    actions = silvaforms.Actions(silvaforms.EditAction())


class CKEditorRESTConfiguration(rest.REST):
    grok.context(ISilvaObject)
    grok.name('silva.core.editor.configuration')

    def GET(self, name='default'):
        service = getUtility(ICKEditorService)

        url_base = IVirtualSite(self.request).get_root_path()
        if not url_base.endswith('/'):
            url_base = url_base + '/'

        # Insert url_base where ever it is needed.
        plugins_url = {name: url_base + path for name, path in
                       service.get_custom_plugins().items()}

        configuration = service.get_configuration(name)
        skin = configuration.skin
        if ',' in skin:
            skin = skin.replace(',', ',' + url_base)

        return self.json_response(
            {'toolbars': configuration.get_toolbars_configuration(),
             'paths': plugins_url,
             'contents_css': configuration.contents_css,
             'formats': configuration.get_formats(),
             'table_styles': configuration.get_table_styles(),
             'plugins': list(plugins_url.keys()),
             'disable_colors': configuration.disable_colors,
             'startup_show_borders': configuration.startup_show_borders,
             'editor_body_class': configuration.editor_body_class,
             'skin': skin})


@grok.subscribe(ICKEditorService, IObjectAddedEvent)
def add_default_configuration(service, event):
    if service._getOb('default', None) is None:
        factory = service.manage_addProduct['silva.core.editor']
        factory.manage_addCKEditorConfiguration('default')


class ISanitizerConfiguration(Interface):
    _allowed_html_tags = schema.Set(title=u"Allowed HTML tags",
                                    value_type=schema.TextLine())
    _allowed_html_attributes = schema.Set(title=u"Allowed HTML attributes",
                                          value_type=schema.TextLine())
    _allowed_css_attributes = schema.Set(title=u"Allowed CSS attributes",
                                         value_type=schema.TextLine())


class CKEditorServiceHTMLSanitizerConfiguration(silvaforms.ZMIForm):
    grok.context(ICKEditorService)
    grok.name('manage_html_sanitizer')

    ignoreContent = False
    label = _(u"Manage HTML Sanitizer")
    description = _(u"""Manager allowed HTML tags
                    and attributes allowed in editor.""")

    fields = silvaforms.Fields(ISanitizerConfiguration)
    actions = silvaforms.Actions(EditAction(title=_(u"Save changes")))
