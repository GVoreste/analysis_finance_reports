=========================
Documentation development
=========================

The documentation is generated, built and configured using a tool called `Sphinx <https://www.sphinx-doc.org/en/master/>`_
and is located in the ``docs/`` directory of the repository. The actual files where this text is written are written using
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_ and are placed in the ``docs/source``
directory. A part of the documentation is autogenerate by the `autodoc <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_
and `autosummary <https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html>`_ sphinx extensions directly from the source code
(this is why is important to add docstrings to the source code and correctly type hint the different functions).
After each modify of the source you can apply the change compiling the documentation in one of the supported languages with:

.. code-block:: console

    sphinx-build -b html -D language='{LANG CODE}' source  build/{LANG CODE}

where ``{LANG CODE}`` has to be substituted with the `ISO 639 <https://en.wikipedia.org/wiki/ISO_639>`_ code of the language.

To see the result you can open with your favourite browser the file ``docs/build/{LANG CODE}/index.html``.