# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
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

    if not isinstance(element, lxml.html.HtmlElement):
        return data

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
        if not isinstance(element, lxml.html.HtmlElement):
            continue
        html_extract_text(child, data)

    add(element.tail)

    return data


def html_truncate_node(el, remaining_length, append=u"…",
        truncate_words=False):

    if truncate_words:
        return html_truncate_node_words(el, remaining_length, append=append);

    text = normalize_space(el.text)
    if text and len(text) >= remaining_length:
        el.text = text[:remaining_length] + append
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
        el.tail = tail[:remaining_length] + append
        return 0

    remaining_length -= len(tail)

    return remaining_length

def html_truncate_node_words(el, remaining_words, append=u"…"):
    word_pattern = re.compile(r'\s*[^\s]+\s*')
    re_append    = re.compile(r'\s*$')

    norm_text    = normalize_space(el.text)
    found_words  = re.findall(word_pattern, norm_text)

    if len(found_words) >= remaining_words:
        el.text = ''.join(found_words[:remaining_words])
        el.text = re.sub(re_append, append, el.text)
        el.tail = None
        for child in el.iterchildren():
            el.remove(child);
        return 0

    remaining_words -= len(found_words)

    for child in el.iterchildren():
        if not remaining_words:
            el.remove(child)
        remaining_words = html_truncate_node_words(
            child, remaining_words, append=append)
        if not remaining_words:
            el.tail = None

    if not remaining_words:
        return 0

    norm_tail    = normalize_space(el.tail)
    found_words  = re.findall(word_pattern, norm_tail)

    if len(found_words) >= remaining_words:
        el.tail = ''.join(found_words[:remaining_words])
        el.tail = re.sub(re_append, append, el.tail)
        return 0

    return remaining_words - len(found_words)

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
        if not isinstance(child, lxml.html.HtmlElement):
            el.remove(child)
            continue
        if child.tag in allowed_tags_set:
            html_sanitize_node(child, allowed_tags_set, allowed_attributes_set,
                allowed_css_style_attributes_set)
        else:
            el.remove(child)
            if child.tail:
                if el.text is not None:
                    el.text += child.tail
                else:
                    el.text = child.tail

URL_SCHEMES_WHITELIST = set([
        'http', 'https', 'ftp', 'ftps', 'ssh', 'news', 'mailto',
        'tel', 'webcal', 'itms'
        ])

HTML_TAGS_WHITELIST = set([
    "a",
    "abbr",
    "acronym",
    "address",
    "area",
    "article",
    "aside",
    "blockquote",
    "br",
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
    "b",
    "i",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "img",
    "ins",
    "label",
    "legend",
    "li",
    "map",
    "mark",
    "nobr",
    "ol",
    "p",
    "cite",
    "code",
    "em",
    "strong",
    "strike",
    "pre",
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
    "tr",
    "ul",
    "wbr",
])

HTML_ATTRIBUTES_WHITELIST = set([
    "accesskey",
    "alt",
    "cite",
    "class",
    "colspan",
    "coords",
    "crossorigin",
    "datetime",
    "for",
    "href",
    "hreflang",
    "id",
    "ismap",
    "media",
    "min",
    "name",
    "rowspan",
    "src",
    "tabindex",
    "target",
    "title",
    "translate",
    "type",
    "usemap",
    "value",
])

CSS_ATTRIBUTES_WHITELIST = set([
    'clear',
    'list-style-type',
    'margin',
    'margin-left',
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

def html_truncate(max_length, html_data, append=ELLIPSIS, truncate_words=False):
    html_tree = lxml.html.fromstring(html_data)
    html_truncate_node(html_tree, max_length, append=append,
            truncate_words=truncate_words)
    return lxml.html.tostring(html_tree)

def html_truncate_words(max_length, html_data, append=ELLIPSIS):
    return html_truncate(max_length, html_data, append=append, truncate_words=True)
