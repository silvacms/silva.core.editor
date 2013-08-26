# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
import lxml.html

from ..utils import html_truncate_characters, html_truncate_words
from ..utils import html_extract_text, html_sanitize
from ..utils import DEFAULT_PER_TAG_WHITELISTS
from ..utils import DEFAULT_HTML_ATTR_WHITELIST
from ..interfaces import PerTagAllowedAttributes

from Products.Silva.testing import tests


ELLIPSIS = u"…"


def html_truncate_test_characters(max_length, html_data, append=ELLIPSIS):
    # Helper for test purposes
    html_tree = lxml.html.fromstring(html_data)
    html_truncate_characters(html_tree, max_length, append=append)
    return lxml.html.tostring(html_tree)


def html_truncate_test_words(max_length, html_data, append=ELLIPSIS):
    # Helper for test purposes
    html_tree = lxml.html.fromstring(html_data)
    html_truncate_words(html_tree, max_length, append=append)
    return lxml.html.tostring(html_tree)


class TestTruncate(unittest.TestCase):

    def test_html_truncate(self):
        html = """<p>some text<a href="#somelink">link</a> and some<span> tail<div></div></span>asdf</p>"""

        self.assertEquals(
            """<p>some text<a href="#somelink">link</a> and&#8230;</p>""",
            html_truncate_test_characters(17, html))

        self.assertEquals(
            """<p>some text<a href="#somelink">link</a> and some<span> t&#8230;</span></p>""",
            html_truncate_test_characters(24, html))

        self.assertEquals(
            """<p>some text<a href="#somelink">link</a> and some<span> tail<div></div></span>a&#8230;</p>""",
            html_truncate_test_characters(28, html))

        self.assertEquals(
            """<p>&#8230;</p>""",
            html_truncate_test_characters(0, html))

        self.assertEquals(
            """<p>some text<img src="#somewhere"> an&#8230;</p>""",
            html_truncate_test_characters(12,
                """<p>some text<img src="#somewhere" /> and some tail</p>"""))

    def test_html_truncate_words(self):
        html = """<p>some text<a href="#somelink">link</a> and                some<span> tail<div></div></span>asdf</p>"""
        spaced_html = """<p>              </p>"""
        empty_html = """<p></p>"""

        self.assertEquals(
            """<p>some text &#8230;</p>""",
            html_truncate_test_words(2, html))

        self.assertEquals(
            """<p>some text<a href="#somelink">link &#8230;</a></p>""",
            html_truncate_test_words(3, html))

        self.assertEquals(
            """<p>some text<a href="#somelink">link</a> and &#8230;</p>""",
            html_truncate_test_words(4, html))

        self.assertEquals(
            """<p>some text<a href="#somelink">link</a> and                some<span> tail &#8230;</span></p>""",
            html_truncate_test_words(6, html))

        self.assertEquals(
            """<p>&#8230;</p>""",
            html_truncate_test_words(0, html))

        self.assertEquals(
            """<p>&#8230;</p>""",
            html_truncate_test_words(0, spaced_html))

        self.assertEquals(
            """<p>&#8230;</p>""",
            html_truncate_test_words(0, empty_html))

    def test_html_truncate_spaces_does_not_count(self):
        html = """<p>some     text<a href="#somelink">link</a>
        \t\n\t\n  and some
        	<span> tail<div></div></span>as      df</p>"""

        self.assertEquals(
            '<p>some     text<a href="#somelink">link</a> and&#8230;</p>',
            html_truncate_test_characters(17, html))

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


class TestSanitize(unittest.TestCase):
    allowed_html_tags = set([PerTagAllowedAttributes('a'),
                             PerTagAllowedAttributes('div')])

    HTML_CHUNCK = u"""
                    <div>
                        <script>
                        function displayDate()
                        {
                        document.getElementById("demo").innerHTML=Date();
                        }
                        </script>
                        <style type="text/css">
                            p {
                                font-size: 1.1em;
                                color: dark;
                            }
                        </style>
                        <!-- this is a comment -->
                        <p AttriBute="self" data-timestamp="42">
                            Hélas! mon ami, l'époque est triste, et mes contes, je vous en préviens,
                            <video width="320" height="240" controls="controls">
                              <source src="movie.mp4" type="video/mp4" />
                              <source src="movie.ogg" type="video/ogg" />
                              Your browser does not support the video tag.
                            </video>
                            ne seront pas gais. Seulement, vous permettrez que, lassé de ce que je vois se passer tous les jours
                            dans le monde réel, j'aille chercher mes récits dans le monde imaginaire. Hélas! j'ai bien peur que tous
                            les esprits un peu élevés, un peu poétiques, un peu rêveurs, n'en soient à cette heure où en est le mien, c'est-à-dire
                            à la recherche de l'idéal, le seul, refuge que Dieu nous laisse contre la réalité.
                            <a href="http://www.gutenberg.org/files/15208/15208-h/15208-h.htm" custom-attrib="attrib">source</a>
                            <object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" width="550" height="400" id="movie_name" align="middle">
                            <param name="movie" value="movie_name.swf"/>
                            <!--[if !IE]>-->
                            <object type="application/x-shockwave-flash" data="movie_name.swf" width="550" height="400">
                                <param name="movie" value="movie_name.swf"/>
                            <!--<![endif]-->
                                <a href="http://www.adobe.com/go/getflash">
                                    <img src="http://www.adobe.com/images/shared/download_buttons/get_flash_player.gif" alt="Get Adobe Flash player"/>
                                </a>
                            <!--[if !IE]>-->
                            </object>
                            <!--<![endif]-->
                            </object>
                        </p>
                        <ul>
                            <li>French</li>
                            <li>English</li>
                            <li>Netherlands</li>
                        </ul>
                    </div>
                    """

    def test_sanitize_chunk(self):
        sanitized = html_sanitize(
            self.HTML_CHUNCK, DEFAULT_PER_TAG_WHITELISTS, DEFAULT_HTML_ATTR_WHITELIST)
        expected = """
                    <div>
                        <p data-timestamp="42">
                            H&#233;las! mon ami, l'&#233;poque est triste, et mes contes, je vous en pr&#233;viens,
                            
                            ne seront pas gais. Seulement, vous permettrez que, lass&#233; de ce que je vois se passer tous les jours
                            dans le monde r&#233;el, j'aille chercher mes r&#233;cits dans le monde imaginaire. H&#233;las! j'ai bien peur que tous
                            les esprits un peu &#233;lev&#233;s, un peu po&#233;tiques, un peu r&#234;veurs, n'en soient &#224; cette heure o&#249; en est le mien, c'est-&#224;-dire
                            &#224; la recherche de l'id&#233;al, le seul, refuge que Dieu nous laisse contre la r&#233;alit&#233;.

                        <a href="http://www.gutenberg.org/files/15208/15208-h/15208-h.htm">source</a>
                            </p>
                        <ul><li>French</li>
                            <li>English</li>
                            <li>Netherlands</li>
                        </ul>
                    </div>
                    """
        tests.assertXMLEqual(expected, sanitized)

    def test_sanitize_attributes(self):
        html = """
                <div>
                    <a href="http://infrae.com/" REL="media" CapitalizedNotAllowed="val">text</a>
                </div>
                """
        sanitized = html_sanitize(html, self.allowed_html_tags, ['href', 'rel'])
        expected = """
                    <div>
                        <a href="http://infrae.com/" rel="media">text</a>
                    </div>
                    """
        tests.assertXMLEqual(expected, sanitized)

    def test_sanitize_tags(self):
        html = """
                <div>
                    <A href="http://infrae.com/">text<FORM><input type="submit" value="button" /></FORM> after</A>
                </div>
                """
        allowed_html_tags = set([PerTagAllowedAttributes('a'),
                                 PerTagAllowedAttributes('div'),
                                 PerTagAllowedAttributes('input')])

        sanitized = html_sanitize(html, allowed_html_tags, ['href'])
        expected = """
                    <div>
                        <a href="http://infrae.com/">text after</a>
                    </div>
                    """
        tests.assertXMLEqual(expected, sanitized)

    def test_sanitize_css(self):
        html = """
                <div>
                    <a href="http://infrae.com/" style="text-decoration: underline; font-size: 20px; display:block">link</a>
                </div>
                """
        sanitized = html_sanitize(html, self.allowed_html_tags, ['href'], ['text-decoration', 'display'])
        expected = """
                    <div>
                        <a href="http://infrae.com/" style="text-decoration: underline;display: block;">link</a>
                    </div>
                    """
        tests.assertXMLEqual(expected, sanitized)

    def test_sanitize_css_with_error(self):
        html = """
                <div>
                    <a href="http://infrae.com/" style="text-decoration: underline; invalid\asdchunck">link</a>
                </div>
                """
        sanitized = html_sanitize(html, self.allowed_html_tags, ['href'], ['text-decoration'])
        expected = """
                    <div>
                        <a href="http://infrae.com/" style="text-decoration: underline;">link</a>
                    </div>
                    """
        tests.assertXMLEqual(expected, sanitized)

    def test_sanitize_css_with_error_first(self):
        html = """
                <div>
                    <a href="http://infrae.com/" style="invalid\asdchunck;text-decoration: underline;">link</a>
                </div>
                """
        sanitized = html_sanitize(html, self.allowed_html_tags, ['href'], ['text-decoration'])
        expected = """
                    <div>
                        <a href="http://infrae.com/" style="text-decoration: underline;">link</a>
                    </div>
                    """
        tests.assertXMLEqual(expected, sanitized)
        
    def test_sanitize_per_tag_css_properties(self):
        html = """
                <div style="color: red; background-color: blue; text-decoration: underline;">
                    <a href="http://infrae.com/" style="color: red; background-color: blue; text-decoration: underline;">link</a>
                </div>
                """
        allowed_html_tags = set([PerTagAllowedAttributes('a', css_properties=set(['color'])),
                                 PerTagAllowedAttributes('div', css_properties=set(['background-color']))])

        sanitized = html_sanitize(html, allowed_html_tags, ['href'], ['text-decoration'])
        expected = """
                    <div style="background-color: blue;text-decoration: underline;">
                        <a href="http://infrae.com/" style="color: red;text-decoration: underline;">link</a>
                    </div>
                    """
        tests.assertXMLEqual(expected, sanitized)

    def test_sanitize_per_tag_html_attributes(self):
        html = """
                <div id="mydiv" class="myclass" title="mytitle" dir="rtl">
                    <span id="mydiv" class="myclass" title="mytitle" dir="rtl">this is inside the span</span>
                </div>
                """
        allowed_html_tags = set([PerTagAllowedAttributes('div', set(['class', 'id'])),
                                 PerTagAllowedAttributes('span', set(['title']))])

        sanitized = html_sanitize(html, allowed_html_tags, ['dir'])
        expected = """
                    <div id="mydiv" class="myclass" dir="rtl">
                        <span title="mytitle" dir="rtl">this is inside the span</span>
                    </div>
                    """
        tests.assertXMLEqual(expected, sanitized)

    def test_sanitize_no_attributes_no_properties_allowed(self):
        html = """
                <div id="mydiv" class="myclass" title="mytitle" dir="rtl">
                    <span id="mydiv" class="myclass" title="mytitle" dir="rtl">this is inside the span</span>
                    <p>This is inside the p</p>
                </div>
                """
        allowed_html_tags = set([PerTagAllowedAttributes('div'),
                                 PerTagAllowedAttributes('span')])
        sanitized = html_sanitize(html, allowed_html_tags, [])
        expected = """
                    <div>
                        <span>this is inside the span</span>
                    </div>
                    """
        tests.assertXMLEqual(expected, sanitized)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTruncate))
    suite.addTest(unittest.makeSuite(TestSanitize))
    return suite
