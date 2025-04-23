# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../src'))
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'FEMORA (Fast Efficient Meshing for OpenSees-based Resilience Analysis)'
copyright = '2025, Amin Pakzad'
author = 'Amin Pakzad'
release = '0.5.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- autodoc configuration ---------------------------------------------------
# Use custom template for autoclass directive
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'special-members': '__init__',
}

# Mock imports for modules that might not be available during documentation building
autodoc_mock_imports = ['pykdtree']

# Set custom templates
autodoc_class_template = 'autoclasstemplate.rst'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Custom CSS ----------------------------------------------------------
html_css_files = [
    'css/custom.css',
]

# -- Logo configuration -----------------------------------------------------
html_logo = 'images/Simcenter_Femora2.png'
html_theme_options = {
    'logo_only': True,
}
