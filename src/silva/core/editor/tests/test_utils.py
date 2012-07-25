# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
import lxml.html

from silva.core.editor.utils import html_truncate
from silva.core.editor.utils import html_extract_text


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

    def test_html_truncate_spaces_does_not_count(self):
        html = """<p>some     text<a href="#somelink">link</a>
        \t\n\t\n  and some
        	<span> tail<div></div></span>as      df</p>"""

        self.assertEquals(
            '<p>some     text<a href="#somelink">link</a> and&#8230;</p>',
            html_truncate(17, html))

    def test_html_extract_text(self):
        chunk = """
<p>This is some text and <img alt="an image appears" src="#" />
and then there
<a href="#" title="Link title">is a link</a> then it is over.</p>
"""
        tree = lxml.html.fromstring(chunk)

        self.assertItemsEqual(
            html_extract_text(tree),
            ['This is some text and', 'an image appears', 'and then there',
             'is a link', 'Link title', 'then it is over.'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestStrip))
    return suite


