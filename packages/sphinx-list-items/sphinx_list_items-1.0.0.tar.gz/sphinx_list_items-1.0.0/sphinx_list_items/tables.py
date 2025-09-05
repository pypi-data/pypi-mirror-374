"""
sphinx-list-items: Sphinx extension to list tables in documents
"""
from docutils import nodes
from .utils import get_section_info, get_caption

def create_table_list_output(app, env, node, fromdocname):
    blist = nodes.bullet_list()
    for docname in sorted(env.found_docs):
        dt = env.get_doctree(docname)
        for tbl in dt.traverse(nodes.table):
            if not tbl.get('ids'):
                continue
            tblid = tbl['ids'][0]
            caption = get_caption(tbl)
            title = caption
            refuri = app.builder.get_relative_uri(fromdocname, docname) + '#' + tblid
            ref = nodes.reference('', title, internal=True, refuri=refuri)
            li = nodes.list_item('', nodes.paragraph('', '', ref))
            blist += li
    node.replace_self(blist)

def create_table_table_output(app, env, node, fromdocname, columns):
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
    table_data = []
    for docname in sorted(env.found_docs):
        dt = env.get_doctree(docname)
        for tbl in dt.traverse(nodes.table):
            if not tbl.get('ids'):
                continue
            tblid = tbl['ids'][0]
            caption = get_caption(tbl)
            table_num = ''
            if getattr(env.config, 'numfig', False):
                nums = (env.toc_fignumbers.get(docname, {}).get('table', {}).get(tblid))
                if nums:
                    table_num = '.'.join(str(n) for n in nums)
            section_id, section_name, section_number = get_section_info(tbl, env, docname)
            table_data.append({
                'section': section_id,
                'section-name': section_name,
                'id': table_num,
                'anchor': tblid,
                'caption': caption,
                'docname': docname,
                'refuri': app.builder.get_relative_uri(fromdocname, docname) + '#' + tblid
            })
    table_data.sort(key=lambda x: (x['id'] if x['id'] else x['docname'], x['anchor']))
    for tbl_data in table_data:
        row = nodes.row()
        tbody += row
        for col in columns:
            entry = nodes.entry()
            if col.lower() == 'anchor':
                ref = nodes.reference('', tbl_data['anchor'], internal=True, refuri=tbl_data['refuri'])
                entry += nodes.paragraph('', '', ref)
            else:
                text = tbl_data.get(col.lower(), '')
                entry += nodes.paragraph(text=text)
            row += entry
    node.replace_self(table)
