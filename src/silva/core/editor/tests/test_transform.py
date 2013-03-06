# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.editor.text import Text
from silva.core.editor.transform.interfaces import ITransformer
from silva.core.editor.transform.interfaces import ITransformerFactory
from silva.core.editor.transform.interfaces import IDisplayFilter
from zope.component import getMultiAdapter
from zope.interface.verify import verifyObject

from Products.Silva.testing import TestRequest
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
        factory = getMultiAdapter((version, request), ITransformerFactory)
        self.assertTrue(verifyObject(ITransformerFactory, factory))
        transformer = factory('test', version.test, '<p/>', IDisplayFilter)
        self.assertTrue(verifyObject(ITransformer, transformer))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TransformTestCase))
    return suite
