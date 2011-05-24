# -*- coding: utf-8 -*-
import lxml
import lxml.html
import re

norm_whitespace_re = re.compile(r'[ \t\n]{2,}')

def normalize_space(text):
    if text is not None:
        return re.sub(norm_whitespace_re, ' ', text)
    return u''


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

def html_truncate(max_length, html_data, append=u"…"):
    html_tree = lxml.html.fromstring(html_data)
    html_truncate_node(html_tree, max_length, append=append)
    return lxml.html.tostring(html_tree)


empty_pattern = re.compile(r'^\s*$', re.UNICODE)

def _filter_out_empty_node(node):
    if isinstance(node, basestring):
        if empty_pattern.match(node):
            return False
        return True
    # no children
    if len(node) == 0:
        if empty_pattern.match(node.text):
            return False
    return True

def parse_html_fragments(data):
    """ Parse html fragments and return a tree with one root.

    In case there is more that one fragment in data, it removes every
    empty elements from top level nodes.
    """
    top_level_nodes = lxml.html.fragments_fromstring(data)
    if len(top_level_nodes) == 1:
        return top_level_nodes[0]
    elif len(top_level_nodes) == 0:
        return lxml.html.Element('div')
    else:
        top_level_nodes = filter(_filter_out_empty_node, top_level_nodes)

        if len(top_level_nodes) == 1:
            return top_level_nodes[0]
        elif len(top_level_nodes) == 0:
            return lxml.html.Element('div')
        else:
            new_root = lxml.html.Element('div')
            if isinstance(top_level_nodes[0], basestring):
                new_root.text = top_level_nodes[0]
                del top_level_nodes[0]
            new_root.extend(top_level_nodes)
            return new_root


