

import mimetypes
import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.template.loader import get_template

from content.models import  ChannelMetadata, ContentNode, File, LocalFile
from statiksite.helpers import build_path_lookup



def render(request, requestpath):
    """
    Load the markdown file `requestpath`.md or `requestpath/index.md` if folder.
    Apply `process_webcopy_html` transformations to prepends `/webcopy` to links.
    """
    # if len(requestpath) == 0:   # handle / correctly
    #     requestpath = '/'
    if requestpath.endswith('/'):
        requestpath = requestpath.rstrip('/')
    default_channel = ChannelMetadata.objects.all()[0]
    lookup = build_path_lookup(default_channel)
    # print('requestpath=', '<' + requestpath + '>')

    resource_type, resource_id = lookup.get(requestpath, (None, None))
    if resource_id is None:
        return HttpResponseNotFound('<h1>404: Resource not found</h1>')

    if resource_type == 'TopicNode':
        return render_topic_node(request, resource_id)
    elif resource_type == 'ContentNode':
        return render_content_node(request, resource_id)
    elif resource_type == 'File':
        return serve_file(request, resource_id)


def render_topic_node(request, node_id):
    node = ContentNode.objects.get(id=node_id)
    template = get_template('statiksite/topic_node.html')
    context =  {
        'head_title': node.title,
        'meta_description': node.description,
        'node': node,
        'node_dict': node.__dict__,
    }
    return HttpResponse(template.render(context, request))


def render_content_node(request, node_id):
    node = ContentNode.objects.get(id=node_id)
    template = get_template('statiksite/content_node.html')
    context =  {
        'head_title': node.title,
        'meta_description': node.description,
        'node': node,
        'node_dict': node.__dict__,
    }
    return HttpResponse(template.render(context, request))


def serve_file(request, file_id):
    importcontent_dir, _ = os.path.split(settings.CONTENT_STORAGE_DIR)
    f = File.objects.get(id=file_id)
    storage_url = f.get_storage_url()
    sub_path_list = storage_url.split('/')[2:]
    sub_path = '/'.join(sub_path_list)
    file_path = os.path.join(importcontent_dir, sub_path)
    # print('serving', file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    file_to_serve = open(file_path, 'rb')
    response = HttpResponse(content=file_to_serve)
    response['Content-Type'] = mime_type
    # response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % 'whatever'
    return response
