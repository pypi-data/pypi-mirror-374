# -*- coding: utf-8 -*-
"""
sphinx_nb_execution_patterns
~~~~~~~~~~~~~~~~~~~~

A Sphinx extension to execute Jupyter NoteBooks based on include and exclude patterns instead of only exclude patterns.

"""

import os
import fnmatch

from typing import Any, Dict
from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)

def setup(app: Sphinx) -> Dict[str, Any]:

    app.add_config_value('nb_execution_includepatterns', [], 'env')
    app.add_config_value('nb_execution_patterns_method', 'only_include', 'env')

    app.connect('config-inited', process_execute_config)

    return {
        "version": "builtin",
        "parallel_read_safe": False,
        "parallel_write_safe": False,
    }

def process_execute_config(app: Sphinx, config: Any):

    # get settings
    nb_execution_excludepatterns = getattr(config, 'nb_execution_excludepatterns', [])
    nb_execution_includepatterns = getattr(config, 'nb_execution_includepatterns', [])
    nb_execution_patterns_method = getattr(config, 'nb_execution_patterns_method', 'only_include')

    # process settings
    if nb_execution_excludepatterns == [] and nb_execution_includepatterns == []:
        # if both include and exclude patterns are not set, just do nothing
        return
    elif nb_execution_excludepatterns != [] and nb_execution_includepatterns == []:
        # only exclude patterns are set, so keep everything as is.
        return
    elif nb_execution_excludepatterns == [] and nb_execution_includepatterns != []:
        # only include patterns are set, so generate exclude patterns and clear include patterns
        nb_execution_excludepatterns = convert_includes_to_excludes(app,config,nb_execution_includepatterns)
        nb_execution_includepatterns = []
        setattr(config, 'nb_execution_excludepatterns', nb_execution_excludepatterns)
        setattr(config, 'nb_execution_includepatterns', nb_execution_includepatterns)
        return
    else:
        # both include and exclude patterns are set
        # consider which method has been set by the user
        if nb_execution_patterns_method == 'only_include':
            # ignore exclude patterns and only use include patterns
            nb_execution_excludepatterns = convert_includes_to_excludes(app,config,nb_execution_includepatterns)
            nb_execution_includepatterns = []
            setattr(config, 'nb_execution_excludepatterns', nb_execution_excludepatterns)
            setattr(config, 'nb_execution_includepatterns', nb_execution_includepatterns)
            return
        elif nb_execution_patterns_method == 'only_exclude':
            # ignore include patterns and only use exclude patterns
            nb_execution_includepatterns = []
            setattr(config, 'nb_execution_includepatterns', nb_execution_includepatterns)
            return
        elif nb_execution_patterns_method == 'exclude_include':
            # first exclude all files matching the exclude patterns, then include files matching the include patterns
            nb_execution_excludepatterns = convert_exclude_include_to_exclude(app,config,nb_execution_excludepatterns,nb_execution_includepatterns)
            nb_execution_includepatterns = []
            setattr(config, 'nb_execution_excludepatterns', nb_execution_excludepatterns)
            setattr(config, 'nb_execution_includepatterns', nb_execution_includepatterns)
        elif nb_execution_patterns_method == 'include_exclude':
            # first include all files matching the include patterns, then exclude files matching the exclude patterns
            nb_execution_excludepatterns = convert_include_exclude_to_exclude(app,config,nb_execution_excludepatterns,nb_execution_includepatterns)
            nb_execution_includepatterns = []
            setattr(config, 'nb_execution_excludepatterns', nb_execution_excludepatterns)
            setattr(config, 'nb_execution_includepatterns', nb_execution_includepatterns)
            return
        else:
            logger.warning(f"Both nb_execution_excludepatterns and nb_execution_includepatterns are non-empty and the selected method {nb_execution_patterns_method} is not implemented yet. Defaulting to include patterns only.")
            nb_execution_excludepatterns = convert_includes_to_excludes(app,config,nb_execution_includepatterns)
            nb_execution_includepatterns = []
            setattr(config, 'nb_execution_excludepatterns', nb_execution_excludepatterns)
            setattr(config, 'nb_execution_includepatterns', nb_execution_includepatterns)
            return


def convert_includes_to_excludes(app: Sphinx, config: Any, include_patterns: list):

    # get all .ipynb files in the source directory
    nb_execution_excludepatterns = list_ipynb_files(app.confdir)
    # remove .ipynb files that match any of the include patterns
    matchings = set()
    for include in include_patterns:
        matching = fnmatch.filter(nb_execution_excludepatterns, include)
        matchings.update(matching)
    nb_execution_excludepatterns.difference_update(matchings)

    return list(nb_execution_excludepatterns)

def list_ipynb_files(confdir):
    ipynb_files = []
    for dirpath, dirnames, filenames in os.walk(confdir):
        rel_dir = os.path.relpath(dirpath, confdir)
        if rel_dir == '_build' or rel_dir.startswith('_build' + os.sep):
            dirnames[:] = []
            continue
        for fname in filenames:
            if fname.endswith('.ipynb'):
                rel_path = fname if rel_dir == '.' else os.path.join(rel_dir, fname)
                rel_path = rel_path.replace(os.sep, '/')
                ipynb_files.append(rel_path)
    return set(sorted(ipynb_files))

def convert_exclude_include_to_exclude(app: Sphinx, config: Any, exclude_patterns: list, include_patterns: list):

    # get all .ipynb files in the source directory
    ipynb_files = list_ipynb_files(app.confdir)

    # include .ipynb files that match any of the exclude patterns
    nb_execution_excludepatterns = set()
    for exclude in exclude_patterns:
        matching = fnmatch.filter(ipynb_files, exclude)
        nb_execution_excludepatterns.update(matching)

    # now exclude .ipynb files that match any of the include patterns
    matchings = set()
    for include in include_patterns:
        matching = fnmatch.filter(ipynb_files, include)
        matchings.update(matching)
    nb_execution_excludepatterns.difference_update(matchings)

    return list(nb_execution_excludepatterns)

def convert_include_exclude_to_exclude(app: Sphinx, config: Any, exclude_patterns: list, include_patterns: list):

    # get all .ipynb files in the source directory
    nb_execution_excludepatterns = list_ipynb_files(app.confdir)

    # now exclude .ipynb files that match any of the include patterns
    matchings = set()
    for include in include_patterns:
        matching = fnmatch.filter(nb_execution_excludepatterns, include)
        matchings.update(matching)
    nb_execution_excludepatterns.difference_update(matchings)

    # now include .ipynb files that match any of the exclude patterns
    nb_execution_excludepatterns.update(exclude_patterns)

    return list(nb_execution_excludepatterns)