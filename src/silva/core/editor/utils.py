# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import lxml
import lxml.html
import re
from tinycss import CSS21Parser

norm_whitespace_re = re.compile(r'[ \t\n]{2,}')

def normalize_space(text, strip=False):
    if text is not None:
        if strip:
            text = text.strip()
        return re.sub(norm_whitespace_re, ' ', text)
    return u''

IMG_TAG = 'img'
ALT_ATTRIBUTE = 'alt'
TITLE_ATTRIBUTE = 'title'

def html_extract_text(element, data=None):
    if data is None:
        data = []
    tag = element.tag.lower()

    def add(text):
        normalized = normalize_space(text, True)
        if normalized:
            data.append(normalized)

    add(element.text)
    if tag == IMG_TAG:
        add(element.attrib.get(ALT_ATTRIBUTE))
    add(element.attrib.get(TITLE_ATTRIBUTE))

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


STYLE_ATTRIBUTE = 'style'
UTF8 = 'utf-8'
_CSS_RULE_FORMAT = "%s: %s;"
_DATA_ATTRIBUTE = 'data-'

def html_sanitize_node(el, allowed_tags_set, allowed_attributes_set,
        allowed_css_style_attributes_set=None):
    attribute_names = set(el.attrib.iterkeys())

    # CSS sanitizing
    if allowed_css_style_attributes_set is not None and \
        STYLE_ATTRIBUTE in attribute_names:
        style = el.attrib[STYLE_ATTRIBUTE]
        attribute_names.remove(STYLE_ATTRIBUTE)
        rules, errors = CSS21Parser().parse_style_attr(style)
        if not rules and errors:
            del el.attrib[STYLE_ATTRIBUTE]
        else:
            style_buffer = bytearray()
            for rule in rules:
                if rule.name in allowed_css_style_attributes_set:
                    style_buffer += _CSS_RULE_FORMAT % (
                        rule.name.encode(UTF8),
                        rule.value.as_css().encode(UTF8))
            el.attrib[STYLE_ATTRIBUTE] = str(style_buffer)

    # HTML attributes sanitizing
    for attribute_name in attribute_names - allowed_attributes_set:
        # We authorize data- attributes.
        if not attribute_name.startswith(_DATA_ATTRIBUTE):
            del el.attrib[attribute_name]

    # HTML tags sanitizing
    for child in el.iterchildren():
        if child.tag in allowed_tags_set:
            html_sanitize_node(child, allowed_tags_set, allowed_attributes_set,
                allowed_css_style_attributes_set)
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
    "dd",
    "del",
    "details",
    "div",
    "dl",
    "dt",
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
    "legend",
    "li",
    "map",
    "mark",
    "meter",
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
    "align",
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

css_attributes_whitelist = set([
    'margin-left',
    'width',
    'height',
])

####### All the code below is only used in tests ####################

def html_sanitize(html_data, allowed_tags, allowed_attributes, allowed_css_style_attributes=None):
    html_tree = lxml.html.fromstring(html_data)
    if allowed_css_style_attributes is not None:
        allowed_css_style_attributes = set(allowed_css_style_attributes)
    html_sanitize_node(html_tree, set(allowed_tags), set(allowed_attributes),
        allowed_css_style_attributes)
    return lxml.html.tostring(html_tree)

ELLIPSIS = u"…"

def html_truncate(max_length, html_data, append=ELLIPSIS):
    html_tree = lxml.html.fromstring(html_data)
    html_truncate_node(html_tree, max_length, append=append)
    return lxml.html.tostring(html_tree)
