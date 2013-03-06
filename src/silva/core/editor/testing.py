# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from Products.Silva.testing import SilvaLayer
import silva.core.editor

from silva.core.references.interfaces import IReferenceService
from silva.core.references.reference import get_content_id
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

import uuid
import transaction


class SilvaEditorLayer(SilvaLayer):
    default_packages = SilvaLayer.default_packages + [
        'silva.core.editor',
        ]

    def _install_application(self, app):
        super(SilvaEditorLayer, self)._install_application(app)
        factory = app.root.manage_addProduct['silva.core.editor']
        factory.manage_addCKEditorService('service_ckeditor')
        transaction.commit()


FunctionalLayer = SilvaEditorLayer(silva.core.editor)


def save_editor_text(text, html, **kwargs):
    """Helper used to save text with references in tests.
    """
    context = kwargs.get('content')
    if context is not None:
        formating = {}
        service = getUtility(IReferenceService)
        for key in kwargs:
            if '_' in key:
                if key.endswith('_content'):
                    content = kwargs[key]
                    name = kwargs.get(key[:-7] + "name", u'document link')
                    tag = unicode(uuid.uuid1())
                    reference = service.new_reference(context, name=name)
                    reference.add_tag(tag)
                    reference.set_target_id(get_content_id(content))
                    formating[key[:-8]] = tag
            elif key != 'content':
                formating[key] = kwargs[key]
        html = html.format(**formating)
    else:
        html = html.format(**kwargs)
    text.save_raw_text(html)
    if context is not None:
        notify(ObjectModifiedEvent(context))
