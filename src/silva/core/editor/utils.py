# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import lxml
import lxml.html
import re
from itertools import imap

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


def html_sanitize_node(el, allowed_tags_set, allowed_attributes_set):
    attribute_names = set(el.attrib.iterkeys())
    for attribute_name in attribute_names - allowed_attributes_set:
        del el.attrib[attribute_name]

    for child in el.iterchildren():
        if child.tag in allowed_tags_set:
            html_sanitize_node(child, allowed_tags_set, allowed_attributes_set)
        else:
            el.remove(child)
            if child.tail:
                el.text += child.tail


html_tags_whitelist = set([
    "a",
    "abbr",
    "acronym",
    "address",
    "area",
    "article",
    "aside",
    "base",
    "bdo",
    "blink",
    "blockquote",
    "body",
    "br",
    "button",
    "caption",
    "col",
    "colgroup",
    "comment",
    "datalist",
    "dd",
    "del",
    "details",
    "div",
    "dl",
    "dt",
    "fieldset",
    "figure",
    "b",
    "big",
    "i",
    "small",
    "footer",
    "head",
    "header",
    "hgroup",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "img",
    "ins",
    "label",
    "layer",
    "legend",
    "li",
    "map",
    "mark",
    "marquee",
    "meter",
    "multicol",
    "nav",
    "nobr",
    "ol",
    "option",
    "p",
    "cite",
    "code",
    "dfn",
    "em",
    "kbd",
    "samp",
    "strong",
    "pre",
    "q",
    "ruby",
    "rp",
    "rt",
    "section",
    "spacer",
    "span",
    "sub",
    "sup",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "time",
    "title",
    "tr",
    "ul",
    "wbr",
])

html_attributes_whitelist = set([
    "accesskey",
    "alt",
    "border",
    "cite",
    "class",
    "colspan",
    "coords",
    "crossorigin",
    "datetime",
    "dir",
    "for",
    "headers",
    "height",
    "hidden",
    "high",
    "href",
    "hreflang",
    "id",
    "ismap",
    "low",
    "media",
    "min",
    "name",
    "open",
    "rel",
    "reversed",
    "rowspan",
    "spellcheck",
    "scope",
    "src",
    "tabindex",
    "target",
    "title",
    "translate",
    "type",
    "usemap",
    "value",
    "width",
])

####### All the code below is only used in tests ####################

def html_sanitize(html_data, allowed_tags_set, allowed_attributes_set):
    html_tree = lxml.html.fromstring(html_data)
    html_sanitize_node(html_tree, set(allowed_tags_set), set(allowed_attributes_set))
    return lxml.html.tostring(html_tree)

def html_truncate(max_length, html_data, append=u"…"):
    html_tree = lxml.html.fromstring(html_data)
    html_truncate_node(html_tree, max_length, append=append)
    return lxml.html.tostring(html_tree)
