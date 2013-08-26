# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import lxml
import lxml.html
import re
from tinycss import CSS21Parser
from .interfaces import PerTagAllowedAttributes

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
    """Extract the text of an lxml tree and return it inside a list.
    """
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


def downgrade_title_nodes(element):
    """Downgrade title nodes (h2 -> h3, h3 -> h4, h4 -> h5, h5-> h6).
    """
    for (expr, tag) in [('//h5', 'h6'), ('//h4', 'h5'),
                        ('//h3', 'h4'), ('//h2', 'h3'),
                        ('//h1', 'h2')]:
        for node in element.xpath(expr):
            node.tag = tag


def html_truncate_characters(el, remaining_length, append=u"…"):
    """Truncate the content of the lxml node ``el`` to contains not
    more than ``remaining_length`` characters. ``append`` is added at
    the end of the last node is truncation happened.
    """
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
        remaining_length = html_truncate_characters(
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


WORD_PATTERN = re.compile(r'\s*[^\s]+\s*')
RE_TRAIL_SPC = re.compile(r'\s*$')


def html_truncate_words(el, remaining_words, append=u"…"):
    """Truncate the content of the lxml node ``el`` to contain no
    more than ``remaining_words`` words. ``append`` is appended to
    the end of the final truncated node, if any.
    """
    found_words = re.findall(WORD_PATTERN, el.text or u'')

    if len(found_words) >= remaining_words:
        el.text = ''.join(found_words[:remaining_words])
        if len(el.text):
            el.text = re.sub(RE_TRAIL_SPC, ' ', el.text)
        el.text += append
        el.tail = None
        for child in el.iterchildren():
            el.remove(child)
        return 0

    remaining_words -= len(found_words)

    for child in el.iterchildren():
        if not remaining_words:
            el.remove(child)
        remaining_words = html_truncate_words(
            child, remaining_words, append=append)
        if not remaining_words:
            el.tail = None

    if not remaining_words:
        return 0

    found_words = re.findall(WORD_PATTERN, el.tail or u'')

    if len(found_words) >= remaining_words:
        el.tail = ''.join(found_words[:remaining_words])
        if len(el.tail):
            el.tail = re.sub(RE_TRAIL_SPC, ' ', el.tail)
        el.tail += append
        return 0

    return remaining_words - len(found_words)


STYLE_ATTRIBUTE = 'style'
UTF8 = 'utf-8'
_CSS_RULE_FORMAT = "%s: %s;"
_DATA_ATTRIBUTE = 'data-'


def html_sanitize_node(el,
                       per_tag_allowed_attr,
                       allowed_attributes_set,
                       allowed_css_style_attributes_set=None):

    allowed_tags = {}
    for allowed_tag in per_tag_allowed_attr:
        allowed_tags[allowed_tag.html_tag] = (
            set(allowed_tag.html_attributes),
            set(allowed_tag.css_properties))

    def recursive_html_sanitize_node(el):
        attribute_names = set(el.attrib.iterkeys())

        extra_allowed_html_attr_for_el = set()
        extra_allowed_css_proper_for_el = set()
        if el.tag in allowed_tags:
            extra_allowed_html_attr_for_el = allowed_tags[el.tag][0]
            extra_allowed_css_proper_for_el = allowed_tags[el.tag][1]

        # CSS sanitizing
        if ((allowed_css_style_attributes_set is not None
             or extra_allowed_css_proper_for_el)
                and STYLE_ATTRIBUTE in attribute_names):
            style = el.attrib[STYLE_ATTRIBUTE]
            attribute_names.remove(STYLE_ATTRIBUTE)
            rules, errors = CSS21Parser().parse_style_attr(style)
            if not rules and errors:
                del el.attrib[STYLE_ATTRIBUTE]
            else:
                style_buffer = bytearray()
                for rule in rules:
                    if (rule.name in allowed_css_style_attributes_set
                            or rule.name in extra_allowed_css_proper_for_el):
                        style_buffer += _CSS_RULE_FORMAT % (
                            rule.name.encode(UTF8),
                            rule.value.as_css().encode(UTF8))
                el.attrib[STYLE_ATTRIBUTE] = str(style_buffer)

        # HTML attributes sanitizing
        for attribute_name in (
                attribute_names - (allowed_attributes_set |
                                   extra_allowed_html_attr_for_el)):
            # We authorize data- attributes.
            if not attribute_name.startswith(_DATA_ATTRIBUTE):
                del el.attrib[attribute_name]

        # HTML tags sanitizing
        for child in el.iterchildren():
            if not isinstance(child, lxml.html.HtmlElement):
                el.remove(child)
                continue
            if (child.tag in allowed_tags):
                recursive_html_sanitize_node(child)
            else:
                el.remove(child)
                if child.tail:
                    if el.text is not None:
                        el.text += child.tail
                    else:
                        el.text = child.tail

    recursive_html_sanitize_node(el)


URL_SCHEMES_BLACKLIST = set([
    'javascript'])

URL_SCHEMES_WHITELIST = set([
    'http', 'https', 'ftp', 'ftps', 'ssh', 'news', 'mailto',
    'tel', 'webcal', 'itms', 'broken',
    ])

DEFAULT_PER_TAG_WHITELISTS = set([
    PerTagAllowedAttributes('a', set(['name', 'target', 'href'])),
    PerTagAllowedAttributes('br'),
    PerTagAllowedAttributes('abbr'),
    PerTagAllowedAttributes('acronym'),
    PerTagAllowedAttributes('blockquote'),
    PerTagAllowedAttributes('caption'),
    PerTagAllowedAttributes('div'),
    PerTagAllowedAttributes('h1'),
    PerTagAllowedAttributes('h2'),
    PerTagAllowedAttributes('h3'),
    PerTagAllowedAttributes('h4'),
    PerTagAllowedAttributes('h5'),
    PerTagAllowedAttributes('h6'),
    PerTagAllowedAttributes('dl'),
    PerTagAllowedAttributes('dt'),
    PerTagAllowedAttributes('dd'),
    PerTagAllowedAttributes('pre'),
    PerTagAllowedAttributes('img', set(['alt', 'src'])),
    PerTagAllowedAttributes('li'),
    PerTagAllowedAttributes('ol', set(['start', 'type']),
                            set(['list-style-type'])),
    PerTagAllowedAttributes('p'),
    PerTagAllowedAttributes('em'),
    PerTagAllowedAttributes('strong'),
    PerTagAllowedAttributes('i'),
    PerTagAllowedAttributes('b'),
    PerTagAllowedAttributes('strike'),
    PerTagAllowedAttributes('span'),
    PerTagAllowedAttributes('sub'),
    PerTagAllowedAttributes('sup'),
    PerTagAllowedAttributes('table', set(['summary', 'dir', 'cols']),
                            set(['width', 'height'])),
    PerTagAllowedAttributes('tbody'),
    PerTagAllowedAttributes('td', set(['colspan', 'rowspan', 'scope']),
                            set(['text-align', 'vertical-align',
                                 'white-space', 'width', 'height'])),
    PerTagAllowedAttributes('th', set(['colspan', 'rowspan', 'scope']),
                            set(['text-align', 'vertical-align',
                                 'white-space', 'width', 'height'])),
    PerTagAllowedAttributes('thead'),
    PerTagAllowedAttributes('tr'),
    PerTagAllowedAttributes('ul', set(['type']), set(['list-style-type']))
    ])


DEFAULT_HTML_ATTR_WHITELIST = set([
    "id",
    "class",
    "title"
])

DEFAULT_CSS_PROP_WHITELIST = set([
    'margin',
    'margin-left',
    'margin-right'
])


####### All the code below is only used in tests ####################

def html_sanitize(html_data, per_tag_allowed_attr,
                  global_allowed_html_attr, global_allowed_css_prop=None):
    html_tree = lxml.html.fromstring(html_data)
    if global_allowed_css_prop is not None:
        global_allowed_css_prop = set(global_allowed_css_prop)

    html_sanitize_node(html_tree,
                       set(per_tag_allowed_attr),
                       set(global_allowed_html_attr),
                       global_allowed_css_prop)

    return lxml.html.tostring(html_tree)
