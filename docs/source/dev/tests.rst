==============
Creating tests
==============

The tests are developed using `pytest <https://docs.pytest.org/en/stable/>`_ and they are located in the ``tests/`` directory.
This guide will forcus on the development of the tests related to the creation of a format. In order to make a test there are three steps:

- create the test file in the ``tests/formats/`` directory. It has to be called ``test_{format name}.py``
- create the dataset to test and with validated results into ``tests/data/{FORMAT NAME}/``
- activate the relevant single page tests in the ``tests/conftest.py`` file


---------
Test file
---------

You can take as reference any test file for the others formats. As you can see usually there are four tests:

- ``PdfFilter`` single page
- ``TextExtract`` single page
- ``Deserialize`` single page
- ``pipeline``

The first three are parametrized tests on a single page of a pdf report that usually behave in the same manner and call an utility
to test in a standardized way. The last one is marked as ``integration_tests`` (because it is slow) and it is not run after each commit
but only in the CI pipeline upon push on ``dev`` or ``main`` remote branches (or by the user launching ``pytest`` command without any option).
This test is run on an entire document and check on the output ``csv``.

.. tip::
    It is not mandatory to test and provide single page tests or pipeline test for all three functions 
    if some of them are not defined or not working.

------------
Test dataset
------------

The dataset to assert the validity of tests and to recreate them consists in different files placed in ``tests/data/{FORMAT NAME}/``.
One document pdf named ``report.pdf`` has to be present to validate the ``PdfFilter`` function and for the integration test.
In order to check the results of the pipeline test has to be present a csv file named ``out.csv``. All the other file are used 
for validating and generating the results of the single page tests for ``PdfFilter``, ``TextExtract`` and ``Deserialize`` functions.
The files are named respectively ``pdf_blks-{page number}.pkl``, ``txt_blks-{page number}.pkl`` and ``financial_data-{page number}.pkl``
and are direct dump of the object generated calling the different functions on a specific ``xml tree`` (page of the document). These files
are `pickle files <https://docs.python.org/3/library/pickle.html>`_ containing respectively a list of ``PdfBlocks``, ``TextBlocks`` and
``FinancialData``. To generate these files is present some utility functions in the ``devtools/make_tests.py`` file.



--------------------------
Activate single page tests
--------------------------

The dataset referring a format can contain a variable number of single page tests to be performed. In not specified no test is performed,
even if the dataset contains the required data. To activate it is necessary to modify the ``tests/conftest.py`` file adding
to the ``single_page_tests`` array a key with the format name in capslock and the list of the pages to test.
