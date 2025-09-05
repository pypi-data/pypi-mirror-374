"""
Common utilities for sphinx-list-items
"""
from docutils import nodes

def get_section_info(fig, env, docname):
    section_id = ''
    section_name = ''
    section_number = ''
    current = fig
    while current:
        current = current.parent
        if current is None:
            break
        if isinstance(current, nodes.section) and current.get('ids'):
            section_anchor = current['ids'][0]
            title_node = current.next_node(nodes.title)
            if title_node:
                section_name = title_node.astext()
            section_number = ''
            if hasattr(env, 'toc_secnumbers') and docname in env.toc_secnumbers:
                secnums = env.toc_secnumbers[docname]
                anchor_key = '#' + section_anchor
                if anchor_key in secnums:
                    nums = secnums[anchor_key]
                    if nums:
                        section_number = '.'.join(str(n) for n in nums)
            if not section_number and section_name:
                import re
                match = re.match(r'^(\d+(?:\.\d+)*)', section_name.strip())
                if match:
                    section_number = match.group(1)
            section_id = section_number if section_number else section_anchor
            break
    return section_id, section_name, section_number

def get_caption(node):
    cap = node.next_node(nodes.caption)
    return cap.astext() if cap else '(no caption)'

def get_image_file(node):
    img = node.next_node(nodes.image)
    if img and 'uri' in img:
        return img['uri'].split('/')[-1]
    return ''
