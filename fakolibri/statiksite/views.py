

import mimetypes
import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.template.loader import get_template

from content.models import  ChannelMetadata, ContentNode, File, LocalFile
from statiksite.helpers import build_path_lookup, get_path_for_node, get_path_for_file


MAIN_FILE_EXTNSIONS = ['mp4', 'mp3', 'pdf']


def render(request, requestpath):
    """
    Load the markdown file `requestpath`.md or `requestpath/index.md` if folder.
    Apply `process_webcopy_html` transformations to prepends `/webcopy` to links.
    """
    if len(requestpath) == 0:   # handle / correctly
        requestpath = '/'
    default_channel = ChannelMetadata.objects.all()[0]
    lookup = build_path_lookup(default_channel)
    print('requestpath=', '<' + requestpath + '>')

    resource_type, resource_id = lookup.get(requestpath, (None, None))
    if resource_id is None:
        return HttpResponseNotFound('<h1>404: Resource not found</h1>')

    if requestpath == '/':
        return render_channel(request, default_channel, resource_id)
    elif resource_type == 'TopicNode':
        return render_topic_node(request, resource_id)
    elif resource_type == 'ContentNode':
        return render_content_node(request, resource_id)
    elif resource_type == 'File':
        return serve_file(request, resource_id)


def render_channel(request, channel, root_node_id):
    root_node = ContentNode.objects.get(id=root_node_id)
    node_children = []
    for child_node in root_node.children.all():
        path = '/' + get_path_for_node(child_node)
        node_children.append( (path, child_node) )

    template = get_template('statiksite/channel_node.html')
    context =  {
        'head_title': channel.name,
        'meta_description': channel.description,
        'node': root_node,
        'node_children': node_children,
        'channel': channel,
    }
    return HttpResponse(template.render(context, request))

def render_topic_node(request, node_id):
    node = ContentNode.objects.get(id=node_id)

    node_children = []
    for child_node in node.children.all():
        path = '/' + get_path_for_node(child_node)
        node_children.append( (path, child_node) )

    template = get_template('statiksite/topic_node.html')
    context =  {
        'head_title': node.title,
        'meta_description': node.description,
        'node': node,
        'node_children': node_children,
    }
    return HttpResponse(template.render(context, request))


def render_content_node(request, node_id):
    node = ContentNode.objects.get(id=node_id)


    main_path = None
    thumb_path = None
    subtitles_path_tuples = []  # (lang_code, path)
    node_files = []
    for file_obj in node.files.all():
        path = '/' + get_path_for_file(file_obj)
        node_files.append( (path, file_obj) )
        #
        ext = path[-3:]
        if file_obj.thumbnail:              # thumbnail for file
            thumb_path = path
        elif ext in MAIN_FILE_EXTNSIONS:    # main media file
            main_path = path
        elif ext == 'vtt':
            subtitles_path_tuples.append( (file_obj.lang.lang_code, path) )
        else:
            print('UNRECOGNIZED PATH TYPE', path)

    if node.kind == 'video':
        template = get_template('statiksite/video_node.html')
    elif node.kind == 'audio':
        template = get_template('statiksite/audio_node.html')
    elif node.kind == 'document':
        template = get_template('statiksite/document_node.html')
    else:
        template = get_template('statiksite/content_node.html')

    context =  {
        'head_title': node.title,
        'meta_description': node.description,
        'node': node,
        'node_dict': node.__dict__,
        'node_files': node_files,
        'subtitles_path_tuples': subtitles_path_tuples,
        'thumb_path': thumb_path,
        'main_path': main_path,
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
