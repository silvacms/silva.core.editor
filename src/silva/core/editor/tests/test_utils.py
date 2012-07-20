# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
import lxml.html

from silva.core.editor.utils import html_truncate
from silva.core.editor.utils import html_extract_text
from silva.core.editor.utils import parse_html_fragments


class TestStrip(unittest.TestCase):

    def test_html_truncate(self):
        html = """<p>some text<a href="#somelink">link</a> and some<span> tail<div></div></span>asdf</p>"""

        self.assertEquals(
            """<p>some text<a href="#somelink">link</a> and&#8230;</p>""",
            html_truncate(17, html))

        self.assertEquals(
            """<p>some text<a href="#somelink">link</a> and some<span> t&#8230;</span></p>""",
            html_truncate(24, html))

        self.assertEquals(
            """<p>some text<a href="#somelink">link</a> and some<span> tail<div></div></span>a&#8230;</p>""",
            html_truncate(28, html))

        self.assertEquals(
            """<p>&#8230;</p>""",
            html_truncate(0, html))

        self.assertEquals(
            """<p>some text<img src="#somewhere"> an&#8230;</p>""",
            html_truncate(12,
                """<p>some text<img src="#somewhere" /> and some tail</p>"""))

    def test_html_extract_text(self):
        chunk = """
<p>This is some text and <img alt="an image appears" src="#" />
and then there
<a href="#">is a link</a> then it is over.</p>
"""
        tree = parse_html_fragments(chunk)

        text = """This is some text and  an image appears 
and then there
is a link then it is over.
"""
        self.assertEquals(unicode(html_extract_text(tree)), text)

    def test_spaces_does_not_count(self):
        html = """<p>some     text<a href="#somelink">link</a>
        \t\n\t\n  and some
        	<span> tail<div></div></span>as      df</p>"""

        self.assertEquals(
            '<p>some     text<a href="#somelink">link</a> and&#8230;</p>',
            html_truncate(17, html))


class TestParseHtml(unittest.TestCase):

    def test_parse_one_top_level_node(self):
        data = """<div>
    <p>some text</p>
    <img src="#"/><span class="some">span text</span>
</div>"""
        tree = parse_html_fragments(data)
        self.assertEquals(data,
            lxml.html.tostring(tree, method="xml", pretty_print=True).strip())

    def test_parse_multiple_roots(self):
        data = """<h1>Some text title</h1>
<p>&nbsp;</p>
<p>some text</p>
<p>some text</p>
<p>some text</p>
<p>&nbsp;</p>
"""
        tree = parse_html_fragments(data)
        self.assertEquals("""<div><h1>Some text title</h1>
<p>&#160;</p>
<p>some text</p>
<p>some text</p>
<p>some text</p>
</div>""", lxml.html.tostring(tree, method="xml", pretty_print=True).strip())

    def test_parse_trailing_empty_elements(self):
        data = """<div>
    <h1>Some text title</h1>
    <p>&nbsp;</p>
    <p>some text</p>
    <p>some text</p>
    <p>some text</p>
    <p>&nbsp;</p>
</div>
<p>
    &nbsp;</p>
"""
        tree = parse_html_fragments(data)
        self.assertEquals("""<div>
    <h1>Some text title</h1>
    <p>&#160;</p>
    <p>some text</p>
    <p>some text</p>
    <p>some text</p>
    <p>&#160;</p>
</div>""", lxml.html.tostring(tree, method="xml", pretty_print=True).strip())

    def test_parse_trailing_image_node(self):
        data = """<div>
    <h1>Some text title</h1>
    <p>&nbsp;</p>
    <p>some text</p>
    <p>some text</p>
    <p>some text</p>
    <p>&nbsp;</p>
</div>
<p>
    &nbsp;</p>
<img src="#" />"""

        tree = parse_html_fragments(data)
        self.assertEquals("""<div><div>
    <h1>Some text title</h1>
    <p>&#160;</p>
    <p>some text</p>
    <p>some text</p>
    <p>some text</p>
    <p>&#160;</p>
</div>
<p>
    &#160;</p>
<img src="#"/></div>""",
            lxml.html.tostring(tree, method="xml", pretty_print=True).strip())

    def test_parse_trailing_text(self):
        data = """blah <div>
    <h1>Some text title</h1>
    <p>&nbsp;</p>
    <p>some text</p>
    <p>some text</p>
    <p>some text</p>
    <p>&nbsp;</p>
</div>
blah blah blah"""

        tree = parse_html_fragments(data)
        self.assertEquals("""<div>blah <div>
    <h1>Some text title</h1>
    <p>&#160;</p>
    <p>some text</p>
    <p>some text</p>
    <p>some text</p>
    <p>&#160;</p>
</div>
blah blah blah</div>""",
            lxml.html.tostring(tree, method="xml", pretty_print=True).strip())

    def test_parse_comment(self):
        data = """
        <!-- some comment -->
"""
        tree = parse_html_fragments(data)
        self.assertEquals("""<!-- some comment -->""",
            lxml.html.tostring(tree, method="xml", pretty_print=True).strip())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestStrip))
    suite.addTest(unittest.makeSuite(TestParseHtml))
    return suite


