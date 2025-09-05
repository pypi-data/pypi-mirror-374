"""
sphinx-list-items: Sphinx extension to list figures in documents
"""


from docutils import nodes
from .utils import get_section_info, get_caption, get_image_file

def create_figure_list_output(app, env, node, fromdocname):
    """Create bulleted list output for figures"""
    blist = nodes.bullet_list()
    for docname in sorted(env.found_docs):
        dt = env.get_doctree(docname)
        for fig in dt.traverse(nodes.figure):
            if not fig.get('ids'):
                continue
            figid = fig['ids'][0]
            caption = get_caption(fig)
            title = caption
            if getattr(env.config, 'numfig', False):
                nums = (env.toc_fignumbers.get(docname, {}).get('figure', {}).get(figid))
                if nums:
                    num = '.'.join(str(n) for n in nums)
                    fmt = env.config.numfig_format.get('figure', 'Figure %s')
                    title = f"{fmt % num}: {caption}"
            refuri = app.builder.get_relative_uri(fromdocname, docname) + '#' + figid
            ref = nodes.reference('', title, internal=True, refuri=refuri)
            li = nodes.list_item('', nodes.paragraph('', '', ref))
            blist += li
    node.replace_self(blist)

def create_figure_table_output(app, env, node, fromdocname, columns):
    """Create table output for figures with specified columns"""
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
    figure_data = []
    for docname in sorted(env.found_docs):
        dt = env.get_doctree(docname)
        for fig in dt.traverse(nodes.figure):
            if not fig.get('ids'):
                continue
            figid = fig['ids'][0]
            caption = get_caption(fig)
            figure_num = ''
            if getattr(env.config, 'numfig', False):
                nums = (env.toc_fignumbers.get(docname, {}).get('figure', {}).get(figid))
                if nums:
                    figure_num = '.'.join(str(n) for n in nums)
            section_id, section_name, section_number = get_section_info(fig, env, docname)
            image_file = get_image_file(fig)
            figure_data.append({
                'section': section_id,
                'section-name': section_name,
                'id': figure_num,
                'anchor': figid,
                'caption': caption,
                'file': image_file,
                'docname': docname,
                'refuri': app.builder.get_relative_uri(fromdocname, docname) + '#' + figid
            })
    figure_data.sort(key=lambda x: (x['id'] if x['id'] else x['docname'], x['anchor']))
    for fig_data in figure_data:
        row = nodes.row()
        tbody += row
        for col in columns:
            entry = nodes.entry()
            if col.lower() == 'anchor':
                ref = nodes.reference('', fig_data['anchor'], internal=True, refuri=fig_data['refuri'])
                entry += nodes.paragraph('', '', ref)
            else:
                text = fig_data.get(col.lower(), '')
                entry += nodes.paragraph(text=text)
            row += entry
    node.replace_self(table)
