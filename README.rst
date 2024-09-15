====
v440
====

Overview
--------

mutable version objects in accordance with PEP440

Installation
------------

To install ``v440``, you can use ``pip``. Open your terminal and run:

.. code-block:: bash

    pip install v440

Example
-------

.. code-block:: python

    from v440 import Version

    v = Version("v1.0.0")
    print("Initial version:", v)
    print("Initial version formatted:", v.format("3"))

    v.release = "2.5.3"
    print("Modified version:", v)

    v.release[1] = 64
    v.release.micro = 4
    print("Further modified version:", v)

    v1 = Version("1.6.3")
    v2 = Version("1.6.4")
    print("v1 == v2 gives", v1 == v2)
    print("v1 != v2 gives", v1 != v2)
    print("v1 >= v2 gives", v1 >= v2)
    print("v1 <= v2 gives", v1 <= v2)
    print("v1 > v2 gives", v1 > v2)
    print("v1 < v2 gives", v1 < v2)

    v = Version("2.5.3.9")
    print("before sorting:", v)
    v.release.sort()
    print("after sorting:", v)

    v = Version("2.0.0-alpha.1")
    print("Pre-release version:", v)
    v.pre = "beta.2"
    print("Modified pre-release version:", v)
    v.pre[1] = 4
    print("Further modified pre-release version:", v)
    v.pre.phase = "BeTa"
    print("Even further modified pre-release version:", v)

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

    v = Version("5.0.0")
    print("Original version:", v)
    del v.data
    print("After reset:", v)

    v.base = "4!5.0.1"
    print(v)
    try:
        v.base = "!!!"
    except Exception as e:
        print(e)
    print(v)

    # The output:
        # Initial version: 1
        # Initial version formatted: 1.0.0
        # Modified version: 2.5.3
        # Further modified version: 2.64.4
        # v1 == v2 gives False
        # v1 != v2 gives True
        # v1 >= v2 gives False
        # v1 <= v2 gives True
        # v1 > v2 gives False
        # v1 < v2 gives True
        # before sorting: 2.5.3.9
        # after sorting: 2.3.5.9
        # Pre-release version: 2a1
        # Modified pre-release version: 2b2
        # Further modified pre-release version: 2b4
        # Even further modified pre-release version: 2b4
        # Post-release version: 1.2.3.post1+local.7.dev
        # Formatted version with post and local: 1.2.post1+local.7.dev
        # Modified: 1.2.3.post2+local.7.dev
        # Modified: 1.2.3+local.7.dev
        # After sorting local: 1.2.3.post3+dev.local.7
        # Modified: 1.2.3.post3+dev.local.7.8
        # Modified: 1.2.3.post3+3.test.19
        # Original version: 5
        # After reset: 0
        # 4!5.0.1
        # '!!!' is an invalid value for 'base'
        # 4!5.0.1
    # Formatting is necessary because release automatically drops the tailing zeros
    # The parsing is in general very tolerant and self correcting.
    # release, pre, and local behave like lists


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
* Email: johannes-programming@mailfence.com

Thank you for using ``v440``!