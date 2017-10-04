# channel2site
Generate a static website from a Kolibri channel


Install
-------
Create a virtualenv, and `pip install -r requirements.txt` into it.



Prerequisites
-------------
Find the channel ID (a long hash-like



Usage
-----
To create a static site from a Kolibr Studio channel, run the following steps:

1. Prepare Local DB:

        fakolibri/manage.py migrate


2. Import content from Studio Server into local DB

        fakolibri/main.py  --channel f916c07c979c50cfab48cfe1e8d7ec2d


3. Start Django server

        fakolibri/manage.py migrate


4. Scrape content

        wget --recursive \
          --convert-links \
          --page-requisites \
          --no-host-directories \
          --directory-prefix=webroot \
           http://localhost:8000

5. Upload the contents of `webroot` to your web server.



