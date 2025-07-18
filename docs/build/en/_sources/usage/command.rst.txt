=================
Command reference
=================

The command can be used launching 

.. code-block:: console

    freeports

from the command line. To get a contextual help use the option ``--help`` shortened to ``-h``

.. code-block:: console

    freeports -h

the options can be specified in different ways that overwrite each other. The same option can be specified in 3 different ways:

1. **configuration file**
2. **environment variables**
3. **command line options**

option not specified default to values specified in the :ref:`conf_parse submodule <freeports\_analysis.conf\_parse>`. 
Those are overwritten by the options specified in the **configuration file**, then the result is overwritten by the **environment variables**,
**command line options** and finally if when in :ref:`BATCH MODE <batch_mode>` by the *job contextual options*.
The option available to be overwritten and how are documented in the respective reference page:

.. toctree::
   :maxdepth: 1
   :caption: Reference config pages:

   config/cmd_args.rst
   config/env_variables.rst
   config/config_file.rst 

After specified the options are overwritten as described in :ref:`the section about validation <conf_validation>`.
Each method of overwriting also has a specific validation mechanism documented in the respective page and applied before
the validation of resulting configuration.
Each way of specify option set one of the program option described in this page.
The options here documented have an effecton the behaviour of the ``freeports`` call.

-----------
The options
-----------

+------------------------+-------------------------+----------------------------------------------------------+----------------------------+
| Option                 | Type                    | Description                                              | Default                    |
+========================+=========================+==========================================================+============================+
| ``VERBOSITY``          | ``int``                 | Describe how much the program verbosity                  | 2                          |
+------------------------+-------------------------+----------------------------------------------------------+----------------------------+
| ``BATCH``              | ``Path``                | If set to path of batch file, it triggers ``BATCH MODE`` |                            |
+------------------------+-------------------------+----------------------------------------------------------+----------------------------+
| ``N_WORKERS``          | ``int``                 | Number of parallel processes in ``BATCH MODE``           | ``os.process_cpu_count()`` |
+------------------------+-------------------------+----------------------------------------------------------+----------------------------+
| ``OUT_CSV``            | ``Path``                | File where to output ``csv`` files                       | ``/dev/stdout``            |
+------------------------+-------------------------+----------------------------------------------------------+----------------------------+
| ``SAVE_PDF``           | ``bool``                | If set and ``URL`` is specified, it save the input pdf   | ``True``                   |
+------------------------+-------------------------+----------------------------------------------------------+----------------------------+
| ``URL``                | ``str``                 | Url of the pdf to take in input                          |                            |
+------------------------+-------------------------+----------------------------------------------------------+----------------------------+
| ``PDF``                | ``Path``                | Path to local pdf                                        |                            |
+------------------------+-------------------------+----------------------------------------------------------+----------------------------+
| ``FORMAT``             | :py:class:`PdfFormats`  | Format to parse the pdf document                         |                            |
+------------------------+-------------------------+----------------------------------------------------------+----------------------------+
| ``CONFIG_FILE``        | ``Path``                | Custom config file location                              | Calculated dynamically     |
+------------------------+-------------------------+----------------------------------------------------------+----------------------------+
| ``SEPARATE_OUT_FILES`` | ``bool``                | In ``BATCH_MODE`` do not merge the results of the batch  | ``False``                  |
+------------------------+-------------------------+----------------------------------------------------------+----------------------------+
| ``PREFIX_OUT``         | ``str``                 | In ``BATCH_MODE`` define an id for the different outputs |                            |
+------------------------+-------------------------+----------------------------------------------------------+----------------------------+ 

"""""""""""""
``VERBOSITY``
"""""""""""""

This values goes from 0 to 5, 0 indicate min verbosity called ``CRITICAL VERBOSITY`` and 4 indicate the max verbosity also called ``DEBUG VERBOSITY``, 5 is the ``NOSET VERBOSITY``.
The meaning of the others levels are the ones used by the python `logging package <https://docs.python.org/3/library/logging.html>`_:

+-----------+----------------------------------------------------------------------------+
| freeports | `logging <https://docs.python.org/3/library/logging.html#logging-levels>`_ |
+===========+============================================================================+
| 0         | ``loggign.CRITICAL``                                                       |
+-----------+----------------------------------------------------------------------------+
| 1         | ``logging.ERROR``                                                          |
+-----------+----------------------------------------------------------------------------+
| 2         | ``loggign.WARNING``                                                        |
+-----------+----------------------------------------------------------------------------+
| 3         | ``loggign.INFO``                                                           |
+-----------+----------------------------------------------------------------------------+
| 4         | ``logging.DEBUG``                                                          |
+-----------+----------------------------------------------------------------------------+
| 5         | ``logging.NOSET``                                                          |
+-----------+----------------------------------------------------------------------------+

"""""""""""""""""""""""""""""""""
``URL``, ``PDF`` and ``SAVE_PDF``
"""""""""""""""""""""""""""""""""

One between ``URL`` or ``PDF`` has to be specified, directly or by consequently to 
*job contextual options* overwriting.
If ``URL`` is specified the program use the pdf resource corresponding to the url,
if ``PDF`` is specified it load a pdf file from local filesystem. If both are specified
it tries to load from local storage, then fallback to the url.
If both are specified and ``SAVE_PDF`` is ``True``, if the file is not present locally, it download it
and save on disk with name indicate by ``PDF`` option.

"""""""""""
``OUT_CSV``
"""""""""""

When not in ``BATCH MODE`` it indicate the file where to output the resulting ``csv`` parsed from the pdf document.

.. note::
    
    The ``OUT_CSV`` default on ``Windows`` systems is ``CON``


""""""""""
``FORMAT``
""""""""""

It indicate which algorithm to use to parse the pdf, these algorithms are called the 'formats' of the pdf reports.
It is mandatory to specify this variable if no ``URL`` is provided, if it is provided the format try to be inferred using
a mapping file that map different url regular expressions to a format. The file is called ``format_url_mapping.yaml`` in the source code.

"""""""""""""""
``CONFIG_FILE``
"""""""""""""""

This option indicate the config file loaded to overwrite the default options, this option can only be specified
using an environment variable or using a command line argument, and it is evaluated before any other option.

""""""""""""""
``N_WORKWERS``
""""""""""""""

Integer that rappresent the number of process spawned (if not set default to number of available CPUs).
When in ``BATCH MODE`` it indicate the process to spawn concurrently to achieve parrallelization on the
processing of different files. When not in ``BATCH_MODE`` the program divide the pdf document in different
section of pages and parallelize processing document wise.

.. _conf_validation:

-------------------------------------
Validation of resulting configuration
-------------------------------------

Each way of specify options have his algorithm to validate the user choice, but after those checks 
it is performed a consistency check on the resulting configuration.
Noticebly the most important performed chekcs are:

* In ``BATCH MODE`` ``OUT_CSV`` is the name of an archive or of a directory
* After *job contextual options* overwriting at least one between ``PDF`` or ``URL`` is defined



.. _batch_mode:

--------------
``BATCH MODE``
--------------

This mode permit to process different files all at one in parallel. This mode is caratterized by the ``BATCH``
variable set to a *batch csv file* and the possibility of setting ``SEPARATE_OUT_FILES`` to ``True``
( in this case ``OUT_CSV`` should be a directory name or the name of a ``.tar.gz`` archive to create)
The *batch csv file* is a csv file with some header that indicate the option to overwrite to the 
resulting configuration. These option are called *job contextual options* and each row of the csv file is called a *job*.
The available overwrittables options are:

+----------------+--------------------+
| Header         | Overwritten option |
+================+====================+
| ``url``        | ``URL``            |
+----------------+--------------------+
| ``save pdf``   | ``SAVE_PDF``       |
+----------------+--------------------+
| ``pdf``        | ``PDF``            |
+----------------+--------------------+
| ``format``     | ``FORMAT``         |
+----------------+--------------------+
| ``prefix out`` | *See below*        |
+----------------+--------------------+

the header is case insensitive, so for example *url*, *URL* and *Url* are considered the same header.
the bool matching is done so that cast to ``True`` if csv value is one between (case insensitive) 
*true, on, yes, y, t, 1* to ``False`` if between *false, off, no, n, f, 0*.

""""""""""""""""""""""""""""""
``OUT_CSV`` and ``prefix out``
""""""""""""""""""""""""""""""

When in ``BATCH MODE`` there are two output profiles, the standard one on a single *csv* and 
on separate files (this distinction can be made setting ``SEPARATE_OUT_FILES`` to ``True`` or ``False``).
The ``prefix out`` cell of the batch file set the ``PREFIX_OUT`` option.
When output on same file the usual *csv* add a column (*Format*) to indicate the format used to parse the 
pdf report from which the data come from. To identify precisely the line of the batch file that generate
the data can if is present ``PREFIX_OUT`` it is added a column called *Report identifier* 
with the corresponding value.

.. tip::
    Set ``PREFIX_OUT`` something meaning full that distinguish the input document, like for example
    the date of the publication of the pdf and istitution that created the report


When on different files ``OUT_CSV`` has to be a directory or a ``.tar.gz`` archive. 
The program create if it doesn't exists a directory named as ``OUT_CSV`` if is not an archive
or the name of the archive without ``.tar.gz`` exstension and for each *job*, save an output file
named ``{PREFIX_OUT}-{FORMAT}.csv`` or just ``{FORMAT}.csv`` if absent or empty prefix. 
If ``OUT_CSV`` was specified  as an archive, the directory
is compressed into ``.tar.gz``. If the directory didn't existed and an archive is created, after creation
the directory is deleted from the filesystem.