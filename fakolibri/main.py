#!/usr/bin/env python
"""
Utility function for downloading content from Kolibri Studio server.
"""
import argparse
import os
import django
import shutil

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fakolibri.settings")
django.setup()



from django.db.models import Sum
from django.template.loader import get_template

from content.models import  ChannelMetadata, ContentNode, File, LocalFile
from content.utils import annotation, paths
from content.utils.channel_import import import_channel_from_local_db
from content.utils.downloader import download_channel_db_file, download_content_files
from content.utils.paths import get_content_database_folder_path, get_content_storage_folder_path



def import_content(channel_id):
    """
    Download all the files for channel_id.
    """
    files_to_download = LocalFile.objects.filter(files__contentnode__channel_id=channel_id, available=False)
    total_bytes_to_transfer = files_to_download.aggregate(Sum('file_size'))['file_size__sum'] or 0
    size_in_MB = total_bytes_to_transfer/1024/1024
    print('Downloading ' + str(size_in_MB) + 'MB of files for channel_id=' + channel_id)
    # download_content_files(files_to_download)


def importchannel(args):
    """
    Import content metadata and files for channel_id in `args['channel']`.
    """
    channel_id = args['channel']

    # 1. download db file
    download_channel_db_file(channel_id)

    # 2. import db file into local db
    import_channel_from_local_db(channel_id)

    # 3. import content
    import_content(channel_id)




def clean():
    # delete local files
    databases_path = get_content_database_folder_path()
    storage_path = get_content_storage_folder_path()
    shutil.rmtree(databases_path)
    shutil.rmtree(storage_path)

    # delete objects from local db
    ChannelMetadata.objects.all().delete()
    ContentNode.objects.all().delete()
    File.objects.all().delete()
    LocalFile.objects.all().delete()


def render_node(node, indent):
    print(indent, node.title, '('+node.kind+')')
    for child in node.children.all():
        render_node(child, indent+'   ')



if __name__=="__main__":
    parser = argparse.ArgumentParser(prog='fakolibri', description=__doc__)
    parser.add_argument("--channel", required=True, help="The channel_id to be downloaded.")
    parser.add_argument("--clean", action="store_true",
                        help="Delete downloaded files in importconant and clear DB tables.")
    args = parser.parse_args()
    args = args.__dict__

    if args['clean']:
        clean()

    importchannel(args)

    # show dat channel
    channel_id = args['channel']
    ch = ChannelMetadata.objects.get(id=channel_id)
    ch_props = ch.__dict__
    del ch_props['thumbnail']
    del ch_props['_state']
    print('CHANNEL:', ch_props)

    # show dem contents
    content_nodes = ContentNode.objects.filter(channel_id=channel_id)
    print("Total ContentNode objects: " + str(len(content_nodes)) + '\n')
    root = content_nodes.filter(level=0)[0]
    render_node(root, '   ')
    print('\n')
