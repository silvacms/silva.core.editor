# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import lxml
import lxml.html
import re

norm_whitespace_re = re.compile(r'[ \t\n]{2,}')

def normalize_space(text):
    if text is not None:
        return re.sub(norm_whitespace_re, ' ', text)
    return u''


def html_extract_text(element, buffer=None, charset='utf-8'):
    if buffer is None:
        buffer = bytearray()

    if element.text:
        buffer.extend(element.text.encode(charset))

    if element.tag.lower() == 'img':
        alt = element.attrib.get('alt')
        if alt:
            buffer.append(' ')
            buffer.extend(alt.encode(charset))
            buffer.append(' ')

    for child in element.iterchildren():
        html_extract_text(child, buffer)

    if element.tail:
        buffer.extend(element.tail.encode(charset))

    return buffer


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


empty_pattern = re.compile(r'^\s*$', re.UNICODE)


def create_node_if_string(string_or_node, tag='div'):
    if isinstance(string_or_node, basestring):
        node = lxml.html.Element(tag)
        node.text = string_or_node
        return node
    return string_or_node


def parse_html_fragments(data, clear_tags=['p', 'span', 'br']):
    """ Parse html fragments and return a tree with one root.

    In case there is more that one fragment in data, it removes every
    empty elements from top level nodes.
    """
    top_level_nodes = lxml.html.fragments_fromstring(data)
    if len(top_level_nodes) == 1:
        return create_node_if_string(top_level_nodes[0])
    elif len(top_level_nodes) == 0:
        return lxml.html.Element('div')
    else:
        for node in reversed(top_level_nodes):
            if isinstance(node, basestring):
                if empty_pattern.match(node):
                    top_level_nodes.pop()
                    continue
            # no children
            if len(node) == 0 and node.tag.lower() in clear_tags:
                if node.text is None or empty_pattern.match(node.text):
                    top_level_nodes.pop()
                    continue
            break

        if len(top_level_nodes) == 1:
            return create_node_if_string(top_level_nodes[0])
        elif len(top_level_nodes) == 0:
            return lxml.html.Element('div')
        else:
            new_root = lxml.html.Element('div')
            if isinstance(top_level_nodes[0], basestring):
                new_root.text = top_level_nodes[0]
                del top_level_nodes[0]
            new_root.extend(top_level_nodes)
            return new_root


