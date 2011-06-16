# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from setuptools import setup, find_packages
import os

version = '1.0dev'

tests_require = [
    'infrae.testing',
    ]


setup(name='silva.core.editor',
      version=version,
      description="Support for the WYSIWYG editor CKEditor for Silva",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
              "Framework :: Zope2",
              "License :: OSI Approved :: BSD License",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              ],
      keywords='silva core editor wysiwyg ckeditor',
      author='Infrae',
      author_email='info@infrae.com',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva', 'silva.core'],
      url='http://infrae.com/products/silva',
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'fanstatic',
        'five.grok',
        'infrae.rest',
        'js.ckeditor',
        'lxml',
        'setuptools',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.references',
        'silva.core.views',
        'silva.ui',
        'zope.component',
        'zope.interface',
        'zope.schema',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      entry_points="""
      [silva.core.editor.extension]
      core = silva.core.editor:extension
      [silva.ui.resources]
      editor = silva.core.editor.interfaces:ICKEditorSilvaUIResources
      """,
      )
