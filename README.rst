====
v440
====

Overview
--------

Mutable version objects in accordance with PEP440.

Installation
------------

To install ``v440``, you can use ``pip``. Open your terminal and run:

.. code-block:: bash

    pip install v440

Example
-------

A Code Example:

.. code-block:: python

    from v440 import Version

    # Formatting is necessary because release automatically drops the tailing zeros
    # The parsing is in general very tolerant and self correcting.
    # release, pre, and local behave like lists

    print("EXAMPLE #1")
    v = Version("v1.0.0")
    print("Initial version:", v)
    print("Initial version formatted:", v.format("3"))
    print("----------------")

    print("EXAMPLE #2")
    v.release = "2.5.3"
    print("Modified version:", v)
    v.release[1] = 64
    v.release.micro = 4
    print("Further modified version:", v)
    print("----------------")

    print("EXAMPLE #3")
    v1 = "1.6.3"
    v2 = Version("1.6.4")
    print("v1", v1)
    print("v2", v2)
    print("v1 == v2 gives", v1 == v2)
    print("v1 != v2 gives", v1 != v2)
    print("v1 >= v2 gives", v1 >= v2)
    print("v1 <= v2 gives", v1 <= v2)
    print("v1 > v2 gives", v1 > v2)
    print("v1 < v2 gives", v1 < v2)
    print("----------------")

    print("EXAMPLE #4")
    v = Version("2.5.3.9")
    print("before sorting:", v)
    v.release.sort()
    print("after sorting:", v)
    print("----------------")

    print("EXAMPLE #5")
    v = Version("2.0.0-alpha.1")
    print("Pre-release version:", v)
    v.pre = "beta.2"
    print("Modified pre-release version:", v)
    v.pre[1] = 4
    print("Further modified pre-release version:", v)
    v.pre.phase = "PrEvIeW"
    print("Even further modified pre-release version:", v)
    print("----------------")

    print("EXAMPLE #6")
    v = Version("1.2.3")
    v.post = "post1"
    v.local = "local.7.dev"
    print("Post-release version:", v)
    print("Formatted version with post and local:", v.format('-1'))
    v.post = "post.2"
    print("Modified:", v)
    del v.post
    print("Modified:", v)
    v.post = "post", 3
    v.local.sort()
    print("After sorting local:", v)
    v.local.append(8)
    print("Modified:", v)
    v.local = "3.test.19"
    print("Modified:", v)
    print("----------------")

    print("EXAMPLE #7")
    v = Version("5.0.0")
    print("Original version:", v)
    del v.data
    print("After reset:", v)
    v.base = "4!5.0.1"
    print("Before error:", v)
    try:
        v.base = "9!x"
    except Exception as e:
        print("Error:", e)
    print("After error:", v)
    print("----------------")

    print("EXAMPLE #8")
    v = Version("1.2.3.4.5.6.7.8.9.10")
    v.release.bump(index=7, amount=5)
    print("Bumping:", v)
    print("----------------")

The Output:

.. code-block:: text

    EXAMPLE #1
    Initial version: 1
    Initial version formatted: 1.0.0
    ----------------
    EXAMPLE #2
    Modified version: 2.5.3
    Further modified version: 2.64.4
    ----------------
    EXAMPLE #3
    v1 1.6.3
    v2 1.6.4
    v1 == v2 gives False
    v1 != v2 gives True
    v1 >= v2 gives False
    v1 <= v2 gives True
    v1 > v2 gives False
    v1 < v2 gives True
    ----------------
    EXAMPLE #4
    before sorting: 2.5.3.9
    after sorting: 2.3.5.9
    ----------------
    EXAMPLE #5
    Pre-release version: 2a1
    Modified pre-release version: 2b2
    Further modified pre-release version: 2b4
    Even further modified pre-release version: 2rc4
    ----------------
    EXAMPLE #6
    Post-release version: 1.2.3.post1+local.7.dev
    Formatted version with post and local: 1.2.post1+local.7.dev
    Modified: 1.2.3.post2+local.7.dev
    Modified: 1.2.3+local.7.dev
    After sorting local: 1.2.3.post3+dev.local.7
    Modified: 1.2.3.post3+dev.local.7.8
    Modified: 1.2.3.post3+3.test.19
    ----------------
    EXAMPLE #7
    Original version: 5
    After reset: 0
    Before error: 4!5.0.1
    Error: 'x' is not a valid numeral segment
    After error: 4!5.0.1
    ----------------
    EXAMPLE #8
    Bumping: 1.2.3.4.5.6.7.13
    ----------------

License
-------

This project is licensed under the MIT License.

Links
-----

* `Documentation <https://pypi.org/project/v440>`_
* `Download <https://pypi.org/project/v440/#files>`_
* `Source <https://github.com/johannes-programming/v440>`_

Credits
-------

* Author: Johannes
* Email: `johannes-programming@mailfence.com <mailto:johannes-programming@mailfence.com>`_

Thank you for using ``v440``!