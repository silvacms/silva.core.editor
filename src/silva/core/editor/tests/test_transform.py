# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from silva.core.editor.text import Text
from silva.core.editor.transform.interfaces import ITransformer
from zope.component import getMultiAdapter
from zope.interface.verify import verifyObject
from zope.publisher.browser import TestRequest

from silva.core.editor.testing import FunctionalLayer


class TransformTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', 'Document')

        version = self.root.document.get_editable()
        version.test = Text('test')

    def test_implementation(self):
        version = self.root.document.get_editable()
        request = TestRequest()
        transformer = getMultiAdapter((version, request), ITransformer)
        self.assertTrue(verifyObject(ITransformer, transformer))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TransformTestCase))
    return suite
