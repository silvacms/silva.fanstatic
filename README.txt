===============
silva.fanstatic
===============

This package provides an integration of `fanstatic`_ into Silva
3.0. In order to know how to use it, please refer to the `Silva
developer documentation`_.

Custom injector
===============

This package provides a custom fanstatic injector called rules. It
can be used like this inside the Paster configuration::

  injector = rules
  rules =
     if there is <!-- Here goes Fanstatic top CSS -->
     replace with all css resources

     if there is <!-- Here goes Fanstatic top JS -->
     replace with all js top resources

     if there is <!-- Here goes Fanstatic bottom JS -->
     replace with all js bottom resources

     otherwise
     insert before </head>

The rules let you look for specific markup in the generated HTML and
will insert the resources around them, if present.


Additional API
==============

This package provides additional objects ``ExternalResources`` and
``Snippet`` in order to include external URLs as resources and
inline snippets too.


Code repository
===============

You can find the code of this extension in Git:
https://github.com/silvacms/silva.fanstatic.


.. _fanstatic: http://www.fanstatic.org
.. _Silva developer documentation: http://docs.silvacms.org/latest/
