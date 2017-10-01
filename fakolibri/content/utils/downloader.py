import os
import shutil

from ricecooker.utils.caching import CacheForeverHeuristic, FileCache, CacheControlAdapter
from ricecooker.utils.html import download_file

from content.utils import annotation, paths


def download_channel_db_file(channel_id):
    """
    Downloads the database file `{{channel_id}}.sqlite3` from Studio Server.
    """
    url = paths.get_content_database_file_url(channel_id)
    dest = paths.get_content_database_file_path(channel_id)
    destdir, filename = os.path.split(dest)
    print('Download .sqlite3 DB file for channel_id=' + channel_id)
    download_file(url, destdir, filename)


def download_content_files(files_to_download):
    """
    Receive list of File objects and downloads them to local content/storage dir.
    """
    # print(files_to_download)

    downloaded_files = []

    file_checksums_to_annotate = []

    for f in files_to_download:

        filename = f.get_filename()
        dest = paths.get_content_storage_file_path(filename)
        destdir = os.path.dirname(dest)

        # if the file already exists, add its size to our overall progress, and skip
        if os.path.isfile(dest) and os.path.getsize(dest) == f.file_size:
            file_checksums_to_annotate.append(f.id)
            continue

        url = paths.get_content_storage_remote_url(filename)

        # print('downloading...', url, 'to', dest)
        download_file(url, destdir, filename)

        downloaded_files.append(dest)

        file_checksums_to_annotate.append(f.id)

    annotation.set_availability(file_checksums_to_annotate)

