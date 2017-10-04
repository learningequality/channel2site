#!/usr/bin/env bash
set -e

if [ -d webroot ]; then
  rm -rf webroot
fi

wget --recursive \
  --convert-links \
  --page-requisites \
  --no-host-directories \
  --directory-prefix=webroot \
   http://localhost:8000

