"""
Sphinx-list-items: List versionadded, versionchanged, deprecated, versionremoved items
"""
from docutils import nodes
try:
    from sphinx.addnodes import versionmodified
except ImportError:
    versionmodified = None
from sphinx.util import logging

class PrefixedLogger:
    def __init__(self, logger):
        self.logger = logger
    def debug(self, msg):
        self.logger.debug(f"[sphinx-list-items: versions] {msg}")
    def info(self, msg):
        self.logger.info(f"[sphinx-list-items: versions] {msg}")
    def warning(self, msg):
        self.logger.warning(f"[sphinx-list-items: versions] {msg}")
    def error(self, msg):
        self.logger.error(f"[sphinx-list-items: versions] {msg}")

logger = PrefixedLogger(logging.getLogger(__name__))

def create_versions_list_output(app, env, node, fromdocname, version_types=None, version_filter=None):
    # version_types should be a single string, e.g. 'versionadded'
    vtype = version_types if version_types else 'versionadded'
    logger.info(f"Listing version nodes of type: {vtype} with version filter: {version_filter}")
    blist = nodes.bullet_list()
    found = 0
    import re
    for docname in sorted(env.found_docs):
        dt = env.get_doctree(docname)
        if versionmodified is not None:
            for item in dt.traverse(versionmodified):
                if item.get('type', None) == vtype:
                    version = item.get('version', '')
                    if version_filter and version != version_filter:
                        continue
                    text = item.astext()
                    # Remove the 'X in version {version}:' prefix if present
                    if version:
                        pattern = rf"^(Added|Changed|Deprecated|Removed) in version {re.escape(str(version))}: ?"
                        text = re.sub(pattern, '', text)
                    title = f'{vtype} {version}: {text}' if version else f'{vtype}: {text}'
                    refuri = app.builder.get_relative_uri(fromdocname, docname)
                    ref = nodes.reference('', title, internal=True, refuri=refuri)
                    li = nodes.list_item('', nodes.paragraph('', '', ref))
                    blist += li
                    found += 1
                    logger.debug(f"Found {vtype} in {docname}: version={version}, text={text}")
    logger.debug(f"Total {vtype} found: {found}")
    node.replace_self(blist)

def create_versions_table_output(app, env, node, fromdocname, vtype, columns=None, version_filter=None):
    logger.debug(f"Creating table for {vtype} with columns: {columns} and version filter: {version_filter}")
    if columns is None:
        columns = ['docname', 'version', 'text', 'type']
    table = nodes.table()
    tgroup = nodes.tgroup(cols=len(columns))
    table += tgroup
    for _ in columns:
        tgroup += nodes.colspec(colwidth=1)
    thead = nodes.thead()
    tgroup += thead
    header_row = nodes.row()
    thead += header_row
    for col in columns:
        header_entry = nodes.entry()
        display_name = col.replace('-', ' ').title()
        header_entry += nodes.paragraph(text=display_name)
        header_row += header_entry
    tbody = nodes.tbody()
    tgroup += tbody
    row_count = 0
    import re
    for docname in sorted(env.found_docs):
        dt = env.get_doctree(docname)
        if versionmodified is not None:
            for item in dt.traverse(versionmodified):
                if item.get('type', None) == vtype:
                    version = item.get('version', '')
                    if version_filter and version != version_filter:
                        continue
                    text = item.astext()
                    # Remove the 'X in version {version}:' prefix if present
                    if version:
                        pattern = rf"^(Added|Changed|Deprecated|Removed) in version {re.escape(str(version))}: ?"
                        text = re.sub(pattern, '', text)
                    type_val = item.get('type', '')
                    row = nodes.row()
                    for col in columns:
                        entry = nodes.entry()
                        if col == 'docname':
                            entry += nodes.paragraph(text=docname)
                        elif col == 'version':
                            entry += nodes.paragraph(text=version)
                        elif col == 'text':
                            entry += nodes.paragraph(text=text)
                        elif col == 'type':
                            entry += nodes.paragraph(text=type_val)
                        else:
                            entry += nodes.paragraph(text=str(item.get(col, '')))
                        row += entry
                    tbody += row
                    row_count += 1
                    logger.debug(f"Table row for {vtype} in {docname}: version={version}, text={text}")
    logger.debug(f"Total {vtype} table rows: {row_count}")
    node.replace_self(table)
