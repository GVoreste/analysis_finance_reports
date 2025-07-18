=====================
Config file reference
=====================

By default the config file is searched in the current directory using the following regular expressions:

* ``^\.?(config|conf)[-\._]?freeports\.ya?ml$``
* ``^\.?freeports[-\._]?(config|conf)\.ya?ml$``

.. tip::
    Our preferred way of calling the config file are:

    * config.freeports.yaml
    * freeports.conf.yaml
    * freeports-config.yaml

If not present it fallback conforming to `XDG Base Directory Specification <https://specifications.freedesktop.org/basedir-spec/latest/>`_ (usually to ``~/.config``)
and search for a ``freeports.yaml`` or ``freeports.yml`` file. 
If no configuration is found last attempt is to *system wise* configuration file (``/etc/freeports.yaml`` or ``/etc/freeport.yml``).

.. note::
    
    In ``Windows`` systems the check on `XDG base directories` is substitute with 
    ``%LOCALAPPDATA%`` (fallback to ``~\\AppData\\Local``) or ``%PROGRAMDATA%`` (fallback to ``C:\\ProgramData``).
    The check to system wise configuration is done on ``%SystemRoot%`` (fallback to ``C:\\Windows``).


The map between command line config file variables and options is:

+----------------------+------------------------+-------------------------+
| Environment variable | Corresponding option   | Type                    |
+======================+========================+=========================+
| ``verbosity``        | ``VERBOSITY``          | ``int``                 |
+----------------------+------------------------+-------------------------+
| ``batch_path``       | ``BATCH``              | ``Path``                |
+----------------------+------------------------+-------------------------+
| ``n_workers``        | ``N_WORKERS``          | ``int``                 |
+----------------------+------------------------+-------------------------+
| ``out_path``         | ``OUT_CSV``            | ``Path``                |
+----------------------+------------------------+-------------------------+
| ``save_pdf``         | ``SAVE_PDF``           | ``bool``                |
+----------------------+------------------------+-------------------------+
| ``url``              | ``URL``                | ``str``                 |
+----------------------+------------------------+-------------------------+
| ``pdf``              | ``PDF``                | ``Path``                |
+----------------------+------------------------+-------------------------+
| ``format``           | ``FORMAT``             | :py:class:`PdfFormats`  |
+----------------------+------------------------+-------------------------+
| ``separate_out``     | ``SEPARATE_OUT_FILES`` | ``bool``                |
+----------------------+------------------------+-------------------------+





