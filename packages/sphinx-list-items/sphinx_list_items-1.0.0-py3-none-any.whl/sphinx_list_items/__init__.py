#!/usr/bin/env python3
# coding: utf-8
'''
A Sphinx extension to list items (figures, tables, etc.) in your documentation.

Project Source: https://github.com/JoKneeMo/sphinx-list-items

Copyright 2025 - JoKneeMo

Licensed under GNU General Public License version 3 (GPLv3).
'''

__author__ =    'JoKneeMo <https://github.com/JoKneeMo>'
__email__ =     '421625+JoKneeMo@users.noreply.github.com'
__copyright__ = '2025 - JoKneeMo'
__license__ =   'GPL-3.0-only'
__version__ =   '1.0.0'

from docutils import nodes
from docutils.parsers.rst import Directive
from .utils import get_section_info, get_caption, get_image_file
from .figures import create_figure_table_output, create_figure_list_output
from .tables import create_table_list_output, create_table_table_output
from .versions import create_versions_list_output, create_versions_table_output

class ListItemsNode(nodes.General, nodes.Element):
    pass

class ListItemsDirective(Directive):
    """
    Sphinx directive to list items (figures, tables, versions, etc.).

    Options:
        :list:   Output as a bulleted list (default)
        :table:  Output as a table (optionally specify columns)
        :version: Only show entries for the specified version (for versionadded, versionchanged, etc.)
    """
    has_content = False
    required_arguments = 1  # e.g., 'figures' or 'tables'
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'list': lambda x: True,
        'table': lambda x: [col.strip() for col in x.split(',') if col.strip()] if x else [],
        'version': str,
    }
    def run(self):
        list_type = self.arguments[0].strip().lower()
        node = ListItemsNode('')
        node['options'] = self.options
        node['list_type'] = list_type
        return [node]

def process_list_items_nodes(app, doctree, fromdocname):
    env = app.builder.env
    for node in list(doctree.traverse(ListItemsNode)):
        options = node.get('options', {})
        list_type = node.get('list_type', '')
        if list_type == 'figures':
            if 'table' in options:
                columns = options['table'] if options['table'] else ['section', 'id', 'anchor', 'caption', 'file']
                create_figure_table_output(app, env, node, fromdocname, columns)
            else:
                create_figure_list_output(app, env, node, fromdocname)
        elif list_type in ('versionadded', 'versionchanged', 'deprecated', 'versionremoved'):
            version_filter = options['version'] if 'version' in options else None
            if 'table' in options:
                columns = options['table'] if options['table'] else ['docname', 'version', 'text', 'type']
                create_versions_table_output(app, env, node, fromdocname, list_type, columns, version_filter)
            else:
                create_versions_list_output(app, env, node, fromdocname, list_type, version_filter)
        elif list_type == 'tables':
            if 'table' in options:
                columns = options['table'] if options['table'] else ['section', 'id', 'anchor', 'caption']
                create_table_table_output(app, env, node, fromdocname, columns)
            else:
                create_table_list_output(app, env, node, fromdocname)

def setup(app):
    app.add_node(ListItemsNode)
    app.add_directive('list-items', ListItemsDirective)
    app.connect('doctree-resolved', process_list_items_nodes)
    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True
    }
