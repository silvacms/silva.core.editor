# -*- coding: utf-8 -*-
# Copyright (c) 2011-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
import lxml.html

from silva.core.editor.utils import html_truncate
from silva.core.editor.utils import html_extract_text
from silva.core.editor.utils import html_sanitize, html_tags_whitelist, html_attributes_whitelist

from Products.Silva.testing import tests


class TestTruncate(unittest.TestCase):

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


class TestSanitize(unittest.TestCase):

    HTML_CHUNCK = u"""
<div>
    <script>
    function displayDate()
    {
    document.getElementById("demo").innerHTML=Date();
    }
    </script>
    <p AttriBute="self">
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
        sanitized = html_sanitize(self.HTML_CHUNCK, html_tags_whitelist, html_attributes_whitelist)
        expected = """
<div>
    <p>
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
        sanitized = html_sanitize(html, ['a', 'div'], ['href', 'rel'])
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
        sanitized = html_sanitize(html, ['a', 'div', 'input'], ['href'])
        expected = """
<div>
    <a href="http://infrae.com/">text after</a>
</div>
"""
        tests.assertXMLEqual(expected, sanitized)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTruncate))
    suite.addTest(unittest.makeSuite(TestSanitize))
    return suite


