.. _install:

============
Installation
============

There are for now 2 installation method:

* using ``pip`` *(Recommended)*
* from source

-------------
Using ``pip``
-------------

Install in a python virtual environment launching

.. code-block:: console

    pip install freeports_analysis

-----------
From source
-----------

.. attention::
    You need to have the python ``build`` package installed.
    You can install it in your virtual environment with ``pip install build``

1. Clone the repository:

.. code-block:: console

    git clone https://github.com/tvp-freeports/analysis_finance_reports.git


2. `cd` into the created directory

.. code-block:: console

    cd analysis_finance_reports

3. build the package

.. code-block:: console

    python -m build .

4. install local package

.. code-block:: console

    pip install .

5. enjoy
