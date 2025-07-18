=================
How to contribute
=================

The general workflow to contribute is:

1. *forking the repository*
2. making your edits to the code
3. *submitting a pull request*

Before doing so you need to setup your local repository

*************************
Setting up the local repo
*************************

First thing clone locally your *forked repository*

.. code-block:: console

    git clone <url-forked-repo>

then enter your local copy and initialize the repository launching from within the root folder of your repository

.. code-block:: console

    contrib/init.sh

this script does:

* install the `githooks <https://git-scm.com/docs/githooks>`_ of the project
* create a python `virtual environment <https://docs.python.org/3/library/venv.html>`_
* install the required packages for developing the project

**********
Contribute
**********

Before making any contribution activate your developing virtual environment located in ``venv/freeports-dev``.
If you want to create other virtual environment, please do that in the *gitignored* ``venv/`` directory.
To activate the virtual environment launch:

.. code-block:: console

    source venv/freeports-dev/bin/activate

in other to *deactivate* it, just launch the ``deactivate`` command.

**********
Guidelines
**********

* comment your code
* add the `docstings <https://peps.python.org/pep-0257/>`_ in order to autogenerate the documentation
* `type hint <https://peps.python.org/pep-0484/>`_ your code
* write `tests <https://docs.pytest.org/en/stable/>`_ for your code
* add meaningful commit messages (add the issue id if it refears to one)
* `lint <https://www.pylint.org/>`_ your code

***************************
Contribution to the website
***************************

It is possible to contribute to the `official website <https://www.freeports.org>`_ of the project
from the specific `GitHub repository <https://github.com/GVoreste/analysis_finance_reports_website>`_. 


*********
Resources
*********
* `How to Contribute to Open Source <https://opensource.guide/how-to-contribute/>`_
* `Using Pull Requests <https://help.github.com/articles/about-pull-requests/>`_
* `GitHub Help <https://help.github.com>`_