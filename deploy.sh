#!/usr/bin/env bash
set -e

if [ ! -d webroot ]; then
  ./mkwebroot.sh
fi

tar -czf static_site_webroot.tgz webroot/
scp static_site_webroot.tgz minireference.com:~/www/minireference/static/tmp/
ssh minireference.com 'cd ~/www/minireference/static/tmp/; rm -rf simplesite; tar -xzf static_site_webroot.tgz; mv webroot simplesite;'
rm static_site_webroot.tgz