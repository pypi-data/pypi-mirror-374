#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""
This module contains PyAMS content themes package
"""
import os
from setuptools import setup, find_namespace_packages


DOCS = os.path.join(os.path.dirname(__file__),
                    'docs')

README = os.path.join(DOCS, 'README.rst')
HISTORY = os.path.join(DOCS, 'HISTORY.rst')

version = '2.1.1'
long_description = open(README).read() + '\n\n' + open(HISTORY).read()

tests_require = [
    'pyramid_zcml',
    'zope.exceptions'
]

setup(name='pyams_content_themes',
      version=version,
      description="PyAMS sample themes",
      long_description=long_description,
      classifiers=[
          "License :: OSI Approved :: Zope Public License",
          "Development Status :: 4 - Beta",
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='Pyramid PyAMS',
      author='Thierry Florac',
      author_email='tflorac@ulthar.net',
      url='https://pyams.readthedocs.io',
      license='ZPL',
      packages=find_namespace_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=[],
      package_data={
          'pyams_content_themes.static': [
              '*.rst', '*.txt', '*.pt', '*.pot', '*.po', '*.mo',
              '*.png', '*.gif', '*.jpeg', '*.jpg', '*.svg',
              '*.ttf', '*.eot', '*.woff', '*.woff2',
              '*.scss', '*.css', '*.js', '*.map']
      },
      include_package_data=True,
      zip_safe=False,
      python_requires='>=3.7',
      # uncomment this to be able to run tests with setup.py
      test_suite="pyams_content_themes.tests.test_utilsdocs.test_suite",
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'fanstatic',
          "importlib_resources; python_version < '3.9'",
          'pyams_content >= 2.7.0',
          'pyams_form',
          'pyams_layer',
          'pyams_portal',
          'pyams_skin',
          'pyams_template',
          'pyramid >= 2.0.0'
      ],
      entry_points={
          'fanstatic.libraries': [
              'pyams = pyams_content_themes:library'
          ]
      })


