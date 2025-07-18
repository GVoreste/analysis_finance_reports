# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
from pathlib import Path

sys.path.insert(0, str(Path("../../", "src").resolve()))
from freeports_analysis import *

project = "freeports_analysis"
copyright = "2025, Oreste Sciacqualegni"
author = "Oreste Sciacqualegni"
release = "0.0.3"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

locale_dirs = ["locales/"]
language = "en"
gettext_compact = False

extensions = [
    "sphinx_rtd_theme",
    # 'sphinx.ext.i18n',
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
]

napoleon_numpy_docstring = True

autosummary_generate = True


pygments_style = "sphinx"
templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
# html_static_path = ["_static"]
