# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import lxml
from five import grok


def transform(name, raw_text, text, version, request, category):
    transformers = grok.queryOrderedSubscribers(
        (version, request), category)
    tree = lxml.html.fromstring(unicode(raw_text, 'utf-8'))
    for transformer in transformers:
        transformer.prepare(name, text)
    for transformer in transformers:
        transformer(tree)
    for transformer in transformers:
        transformer.finalize()
    return lxml.html.tostring(tree)


def render(attribute_name, version, request, category):
    text = getattr(version, attribute_name)
    return transform(attribute_name, str(text), text, version, request, category)
