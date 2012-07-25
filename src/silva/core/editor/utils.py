# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import lxml
import lxml.html
import re

norm_whitespace_re = re.compile(r'[ \t\n]{2,}')

def normalize_space(text, strip=False):
    if text is not None:
        if strip:
            text = text.strip()
        return re.sub(norm_whitespace_re, ' ', text)
    return u''


def html_extract_text(element, data=None):
    if data is None:
        data = []
    tag = element.tag.lower()

    def add(text):
        normalized = normalize_space(text, True)
        if normalized:
            data.append(normalized)

    add(element.text)
    if tag == 'img':
        add(element.attrib.get('alt'))
    add(element.attrib.get('title'))

    for child in element.iterchildren():
        html_extract_text(child, data)

    add(element.tail)

    return data


def html_truncate_node(el, remaining_length, append=u"…"):
    text = normalize_space(el.text)
    if text and len(text) >= remaining_length:
        el.text = text[0:remaining_length] + append
        el.tail = None
        for child in el.iterchildren():
            el.remove(child)
        return 0

    remaining_length -= len(text)

    for child in el.iterchildren():
        if remaining_length <= 0:
            el.remove(child)
        remaining_length = html_truncate_node(
            child, remaining_length, append=append)
        if remaining_length == 0:
            el.tail = None

    if remaining_length <= 0:
        return 0

    tail = normalize_space(el.tail)
    if tail and len(tail) >= remaining_length:
        el.tail = tail[0:remaining_length] + append
        return 0

    remaining_length -= len(tail)

    return remaining_length


####### All the code below this comment is not used ####################

def html_truncate(max_length, html_data, append=u"…"):
    html_tree = lxml.html.fromstring(html_data)
    html_truncate_node(html_tree, max_length, append=append)
    return lxml.html.tostring(html_tree)




