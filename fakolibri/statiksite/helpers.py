from django.core.cache import caches


def get_slug(node):
    """
    Return short URL-able sting to use as identifier for current Node or File.
    """
    return node.title.replace(' ', '_')


def get_path_for_node(node):
    """
    Returns the requestpath for accessing this node,
    e.g. 'topic_1/subtopic_2/content_item/ for ContentNode
      or 'topic_1/subtopic_2/  for TopicNode
    """
    current = node
    path_rtl = []
    while current.parent is not None:
        path_rtl.append(get_slug(current))
        current = current.parent
    slugs = reversed(path_rtl)

    path = '/'.join(slugs)
    if path == '/':
        return path
    else:
        return path + '/'


def get_path_for_file(file):
    """
    Returns the requestpath for serving this file
    e.g. 'topic_1/subtopic_2/content_item/content_item.pdf
    """
    node = file.contentnode
    pathdir = get_path_for_node(node)
    filename = file.get_download_filename()
    return pathdir + filename


def build_path_lookup(channel):
    """
    Returns a requestpath --> ContentNode || File lookup dictonary.
    e.g. 'topic_1/subtopic_2/content_item/ --> ('ContentNode', node_id)
      or 'topic_1/subtopic_2/content_item/content_item_Document.pdf --> ('File', file_id)
    """
    cache = caches['default']
    lookup = cache.get('lookup')
    if lookup is not None:
        return lookup

    lookup = {}
    def process_node(node):
        node_path = get_path_for_node(node)
        if node.kind == 'topic':
            lookup[node_path] = ('TopicNode', node.id)
        else:
            lookup[node_path] = ('ContentNode', node.id)
        # process files
        for node_file in node.files.all():
            file_path = get_path_for_file(node_file)
            lookup[file_path] = ('File', node_file.id)
        # recurse on children
        for child_node in node.children.all():
            process_node(child_node)

    process_node(channel.root)

    cache.set('lookup', lookup, 3000)
    return lookup
