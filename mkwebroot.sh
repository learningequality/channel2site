#!/usr/bin/env bash
set -e

export WEBROOTDIR=webroot

if [ -d $WEBROOTDIR ]; then
  rm -rf $WEBROOTDIR
fi

wget --recursive \
  --convert-links \
  --page-requisites \
  --no-host-directories \
  --directory-prefix=$WEBROOTDIR \
   http://localhost:8000

scripts/deindexify.py $WEBROOTDIR

