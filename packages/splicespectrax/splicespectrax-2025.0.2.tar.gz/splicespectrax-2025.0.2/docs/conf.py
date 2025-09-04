# Configuration file for the Sphinx documentation builder.

import os
import sys

# -- Path setup --------------------------------------------------------------

# Add the src/ directory to sys.path for autodoc to find 'spectra'
sys.path.insert(0, os.path.abspath('../spectra'))

# -- Project information -----------------------------------------------------

project = 'SPECTRA'
copyright = '2025, Kairavee Thakkar'
author = 'Kairavee Thakkar'
release = '0.1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.autosummary',
    'myst_parser',  # enable Markdown support; remove if not using Markdown
]

# Generate autosummary pages automatically
autosummary_generate = True

# Templates path
templates_path = ['_templates']

# Patterns to ignore when looking for source files
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Enable TODOs in the documentation
todo_include_todos = True

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Napoleon settings for NumPy-style docstrings ----------------------------

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# -- If using Markdown with myst_parser --------------------------------------

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- Autodoc options ---------------------------------------------------------

autodoc_member_order = 'bysource'
autodoc_inherit_docstrings = True
