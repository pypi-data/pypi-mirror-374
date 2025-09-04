# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

try:
    from importlib import metadata
except ImportError:
    # Python < 3.8
    import importlib_metadata as metadata

sys.path.insert(0, os.path.abspath('../twopilabs/'))
sys.path.append(os.path.abspath('extensions'))

SOURCE_URI = os.environ['SOURCE_URI'] if 'SOURCE_URI' in os.environ else 'http://invalid.uri'

# -- Project information -----------------------------------------------------

project = '2πSENSE X1000 series device control package'
copyright = '2021, 2pi-Labs GmbH'
author = '2pi-Labs GmbH'
release = metadata.version('twopilabs-sense-x1000')
version = '.'.join(release.split('.')[:2])

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.linkcode',
    'source'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('http://numpy.org/doc/stable/reference', None),
    'scipy': ('http://docs.scipy.org/doc/scipy/reference', None),
    'matplotlib': ('http://matplotlib.sourceforge.net', None),
    'h5py': ('http://docs.h5py.org/en/stable')
}

def linkcode_resolve(domain, info):
    if domain != 'py':
        return None
    if not info['module']:
        return None
    filename = info['module'].replace('.', '/')
    return f'{SOURCE_URI}/twopilabs/{filename}.py'

autosectionlabel_prefix_document = True

source_uri = SOURCE_URI

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static', '_images']

