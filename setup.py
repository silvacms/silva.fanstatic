# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '1.1.1'

tests_require = [
    'infrae.wsgi [test]',
    'infrae.testbrowser',
    ]

setup(name='silva.fanstatic',
      version=version,
      description="Integration of fanstatic in Silva CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Zope Public License",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope2",
          ],
      keywords='zope2 fanstatic silva',
      author='Sylvain Viollon',
      author_email='info@infrae.com',
      url='http://hg.infrae.com/silva.fanstatic',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['silva'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'fanstatic > 0.11',
          'five.grok',
          'martian',
          'silva.core.conf',
          'silva.core.views',
          'zope.component',
          'zope.interface',
          'zope.publisher',
          'zope.traversing',
          'zope.testing',
          ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
