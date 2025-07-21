=======================
Developer documentation
=======================


.. toctree::
   :maxdepth: 1
   :caption: Contents:

   code
   docs
   tests
   i18n
   example


The project consists in different repositories, specifically this section focus on the repository
containing the source code and the documentation.

This repository has two protected branches ``main`` and ``dev``, plus any other additional non protected branches.
The logic is that ``dev`` branch is used for the active development, ``main`` for the deployment.
On both branches each commit triggers a `CI <https://en.wikipedia.org/wiki/Continuous_integration>`_ pipeline
on the `Freeport Jenkins server <https://jenkins.freeports.org>`_ this server do some checks on the code (specified in the 
``Jenkinsfile`` on top of the repository). Specifically it:

1. Lint the code
2. Fail if a minimal linting vote is reached
3. Test the code and fail if some test is not passed
4. Fail if a minimal percentage of code is not tested
5. Build the documentation
6. Fail if a minimal percentage of the code is not documented
7. If the commit is tagged as `release version` (using `semantic versioning specification <https://semver.org/>`_) it publishes it to `PyPI <https://pypi.org/project/freeports-analysis/>`_

The difference between the two branches is that the state of the pipeline is only informative on the ``dev`` branch 
(it means that it only shows the failing) but the positive outcome is **imposed a requirement** for the PR on ``main`` branch to be approved and merged.

In particular the development divide between:

- development of tools for helping the contribution process
- development of the code common for the different `pdf reports` 
  (for example the source code related to the options and behaviour of the ``freeports`` command)
- development of the code for parsing the different `pdf report formats`
- development of tests on the code
- writing of the documentation
- internationalization of the code (translation of messages in output of the command)
- internationalization of the documentation (translation of the documentation)

you can consult the specific guide related to the type of contribution that you want to do.
When you feel comfortable with the concepts you can go forward with the workflow :doc:`examples provided <example>`;
this page not only contains video expaining the possible contributions but also how to deploy them.