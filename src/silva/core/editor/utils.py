# -*- coding: utf-8 -*-
import lxml
import lxml.html
import re

norm_whitespace_re = re.compile(r'[ \t\n][ \t\n]+')

def normalize_space(text):
    return re.sub(norm_whitespace_re, ' ', text)


def html_truncate_node(el, remaining_length, append=u""):
    text = normalize_space(el.text)
    if el.text and len(text) >= remaining_length:
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
    if el.tail and len(tail) >= remaining_length:
        el.tail = tail[0:remaining_length] + append
        return 0

    remaining_length -= len(tail)

    return remaining_length

def html_truncate(max_length, html_data, append=u"…"):
    html_tree = lxml.html.fromstring(html_data)
    html_truncate_node(html_tree, max_length, append=append)
    return lxml.html.tostring(html_tree)
