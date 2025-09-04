# Configuration file for the Sphinx documentation app.

# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


import sys

import deapi


# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.append("../")

# Project information
project = "deapi"

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "_static/de_api_icon.svg"

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.

# html_favicon = "_static/logo.ico"


master_doc = "index"

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "sphinxcontrib.bibtex",
    "sphinx_design",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.githubpages",
    "sphinx.ext.graphviz",
    "sphinx.ext.mathjax",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.linkcode",
    "sphinx_codeautolink",
    "sphinx_gallery.gen_gallery",
    "sphinx_copybutton",
    "nbsphinx",
]

# Create links to references within deapi's documentation to these packages.
intersphinx_mapping = {
    "dask": ("https://docs.dask.org/en/stable", None),
    "diffpy.structure": ("https://www.diffpy.org/diffpy.structure", None),
    "diffsims": ("https://diffsims.readthedocs.io/en/stable", None),
    "hyperspy": ("https://hyperspy.org/hyperspy-doc/current", None),
    "h5py": ("https://docs.h5py.org/en/stable", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "orix": ("https://orix.readthedocs.io/en/stable", None),
    "python": ("https://docs.python.org/3", None),
    "scipy": ("https://docs.scipy.org/doc/scipy", None),
    "skimage": ("https://scikit-image.org/docs/stable", None),
    "sklearn": ("https://scikit-learn.org/stable", None),
    "rosettasciio": ("https://hyperspy.org/rosettasciio/", None),
}


_version = deapi.__version__
version_match = "dev" if "dev" in _version else ".".join(_version.split(".")[:2])


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files. This image also affects
# html_static_path and html_extra_path.

# The theme to use for HTML and HTML Help pages.  See the documentation for a
# list of builtin themes.
html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "github_url": "https://github.com/directelectron/deapi",
    "header_links_before_dropdown": 7,
    "navigation_with_keys": True,
    "show_toc_level": 2,
    "use_edit_page_button": True,
    "navbar_start": ["navbar-logo"],
}

html_context = {
    "github_user": "deapi",
    "github_repo": "deapi",
    "github_version": "main",
    "doc_path": "doc",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files, so
# a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

# Syntax highlighting
pygments_style = "friendly"

napoleon_google_docstring = False
napoleon_use_param = False
napoleon_use_ivar = True
nitpicky = True

# Figure references
numfig = True

# nbsphinx configuration
# Taken from nbsphinx' own nbsphinx configuration file, with slight
# modification to point nbviewer and Binder to the GitHub master links
# when the documentation is launched from a deapi version with
# "dev" in the version.
if "dev" in version:
    release_version = "master"
else:
    release_version = "v" + version
# https://nbsphinx.readthedocs.io/en/0.8.0/never-execute.html
nbsphinx_execute = "never"  # auto, always, never
nbsphinx_kernel_name = "python3"
nbsphinx_allow_errors = True
exclude_patterns = ["_build", "**.ipynb_checkpoints", "examples/*/*.ipynb"]

# sphinxcontrib-bibtex configuration
bibtex_bibfiles = ["bibliography.bib"]


# -- Sphinx-Gallery---------------
# https://sphinx-gallery.github.io
sphinx_gallery_conf = {
    "backreferences_dir": "reference/generated",
    "doc_module": ("deapi",),
    "examples_dirs": "../examples",  # path to your example scripts
    "gallery_dirs": "examples",  # path to where to save gallery generated output
    "filename_pattern": "^((?!sgskip).)*$",  # pattern to define which will be executed
    "ignore_pattern": "_sgskip.py",  # pattern to define which will not be executed
    "reference_url": {"deapi": None},
    "show_memory": True,
}

autodoc_default_options = {
    "show-inheritance": True,
}

graphviz_output_format = "svg"


# sphinx.ext.autodoc
# ------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
autosummary_ignore_module_all = False
autosummary_imported_members = True
autodoc_typehints_format = "short"
autodoc_default_options = {
    "show-inheritance": True,
}

autosummary_generate = True


# This is the expected signature of the handler for this event, cf doc
def autodoc_skip_member(app, what, name, obj, skip, options):
    # Basic approach; you might want a regex instead
    return False


# Automatically called by sphinx at startup
def setup(app):
    # Connect the autodoc-skip-member event from apidoc to the callback
    app.connect("autodoc-skip-member", autodoc_skip_member)
