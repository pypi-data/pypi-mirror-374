.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


DeepDiff 8.6.1 documentation!
=============================

*******
Modules
*******

The DeepDiff library includes the following modules:

- **DeepDiff** For Deep Difference of 2 objects. :doc:`/diff`

    It return the deep Difference of python objects. It can also be used to take the distance between objects. :doc:`/deep_distance`

- **DeepSearch** Search for objects within other objects. :doc:`/dsearch`

- **DeepHash** Hash any object based on their content even if they are not "hashable" in Python's eyes.  :doc:`/deephash`

- **Delta** Delta of objects that can be applied to other objects. Imagine git commits but for structured data.  :doc:`/delta`

- **Extract** For extracting a path from an object  :doc:`/extract`

- **Commandline** Most of the above functionality is also available via the commandline module  :doc:`/commandline`

***********
What Is New
***********

DeepDiff 8-6-1
--------------

    - Patched security vulnerability in the Delta class which was vulnerable to class pollution via its constructor, and when combined with a gadget available in DeltaDiff itself, it could lead to Denial of Service and Remote Code Execution (via insecure Pickle deserialization).


DeepDiff 8-6-0
--------------

   - Added Colored View thanks to @mauvilsa
   - Added support for applying deltas to NamedTuple thanks to @paulsc
   - Fixed test_delta.py with Python 3.14 thanks to @Romain-Geissler-1A
   - Added python property serialization to json
   - Added ip address serialization
   - Switched to UV from pip
   - Added Claude.md
   - Added uuid hashing thanks to @akshat62
   - Added ``ignore_uuid_types`` flag to DeepDiff to avoid type reports
     when comparing UUID and string.
   - Added comprehensive type hints across the codebase (multiple commits
     for better type safety)
   - Added support for memoryview serialization
   - Added support for bytes serialization (non-UTF8 compatible)
   - Fixed bug where group_by with numbers would leak type info into group
     path reports
   - Fixed bug in ``_get_clean_to_keys_mapping without`` explicit
     significant digits
   - Added support for python dict key serialization
   - Enhanced support for IP address serialization with safe module imports
   - Added development tooling improvements (pyright config, .envrc
     example)
   - Updated documentation and development instructions


DeepDiff 8-5-0
--------------

    - Updating deprecated pydantic calls
    - Switching to pyproject.toml
    - Fix for moving nested tables when using iterable_compare_func.  by 
    - Fix recursion depth limit when hashing numpy.datetime64
    - Moving from legacy setuptools use to pyproject.toml


DeepDiff 8-4-2
--------------

    - fixes the type hints for the base
    - fixes summarize so if json dumps fails, we can still get a repr of the results
    - adds ipaddress support


*********
Tutorials
*********

Tutorials can be found on `Zepworks blog <https://zepworks.com/tags/deepdiff/>`_
                                                                                                                                                                                                          

************
Installation
************

Install from PyPi::

    pip install deepdiff

If you want to use DeepDiff from commandline::

    pip install "deepdiff[cli]"

If you want to improve the performance of DeepDiff with certain processes such as json serialization::

    pip install "deepdiff[optimize]"

Read about DeepDiff optimizations at :ref:`optimizations_label`

Importing
~~~~~~~~~

.. code:: python

    >>> from deepdiff import DeepDiff  # For Deep Difference of 2 objects
    >>> from deepdiff import grep, DeepSearch  # For finding if item exists in an object
    >>> from deepdiff import DeepHash  # For hashing objects based on their contents
    >>> from deepdiff import Delta  # For creating delta of objects that can be applied later to other objects.
    >>> from deepdiff import extract  # For extracting a path from an object


.. note:: if you want to use DeepDiff via commandline, make sure to run:: 
    pip install "deepdiff[cli]"

Then you can access the commands via:

- DeepDiff

.. code:: bash

    $ deep diff --help

- Delta

.. code:: bash

    $ deep patch --help

- grep

.. code:: bash

    $ deep grep --help
- extract

.. code:: bash

    $ deep extract --help


Supported data types
~~~~~~~~~~~~~~~~~~~~

int, string, unicode, dictionary, list, tuple, set, frozenset, OrderedDict, NamedTuple, Numpy, custom objects and more!


References
==========

.. toctree::
   :maxdepth: 4

   diff
   dsearch
   deephash
   delta
   extract
   colored_view
   commandline
   changelog
   authors
   faq
   support


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
