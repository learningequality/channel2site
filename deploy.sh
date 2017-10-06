#!/usr/bin/env bash
set -e

if [ ! -d webroot ]; then
  ./mkwebroot.sh
fi

# setup docker machien ENV variables
eval $(docker-machine env samplesitehost)

# build docker image
docker build . --tag samplesite-docker-img

# start container
docker run \
  --publish 80:80 \
  --detach \
  --name samplesite \
  samplesite-docker-img

# running?
docker ps