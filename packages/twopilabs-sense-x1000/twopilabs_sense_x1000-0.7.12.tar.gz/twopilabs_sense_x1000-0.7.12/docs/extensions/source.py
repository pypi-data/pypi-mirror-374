# Role for linking source code to Gitlab
# Borrowed from original cpython docs
# https://github.com/python/cpython/blob/main/Doc/tools/extensions/pyspecific.py

from sphinx.errors import SphinxError
from sphinx.util.nodes import split_explicit_title
from docutils import nodes, utils
import os

source_uri = None

def config_inited(app, config):
    if not isinstance(config.source_uri, str):
        raise SphinxError("`source_uri` is missing from conf.py")

    global source_uri
    source_uri = config.source_uri

def source_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    has_t, title, target = split_explicit_title(text)
    title = utils.unescape(title)
    target = utils.unescape(target)
    refnode = nodes.reference(title, title, refuri=f'{source_uri}/{target}')
    return [refnode], []

def setup(app):
    app.add_role('source', source_role)
    app.add_config_value('source_uri', None, '')
    app.connect('config-inited', config_inited)

