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
    print(f"Modified version: {v}")

    v.release[1] = 64
    v.release.micro = 4
    print(f"Further modified version: {v}")

    # The output:
        # Initial version: 1
        # Initial version formatted: 1.0.0
        # Modified version: 2.5.3
        # Further modified version: 2.64.4
    # Formatting is necessary because release automatically drops the tailing zeros
    # The parsing is in general very tolerant and self correcting.

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