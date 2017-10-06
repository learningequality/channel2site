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







Provisioning on GCP
-------------------

We'll use the command line tool `docker-machine` for the following two tasks:
  - Provision an instance (a virtual machine rented from GCP) which will
    serve as the docker host
  - Set appropriate environment variables to make `docker` command line tools
    talk to the remote docker host instead of localhost


STEP0: Login (if not logged in already)

    gcloud auth application-default login


STEP1: Create a static IP for the docker host:

    gcloud compute addresses create samplesitehost-address --region us-east1


STEP2: Use `docker-machine`'s [GCE driver](https://docs.docker.com/machine/drivers/gce/)
to setup a docker host called `samplesitehost` in the Google cloud.

    docker-machine create --driver google \
       --google-project kolibri-demo-servers \
       --google-zone us-east1-d \
       --google-machine-type f1-micro \
       --google-machine-image debian-cloud/global/images/debian-9-stretch-v20170717 \
       --google-disk-size 50 \
       --google-username admin \
       --google-tags http-server,https-server \
       --google-address samplesitehost-address \
       samplesitehost


Assuming everything goes to plan, a new instance should be running, with docker
installed on it and the docker daemon listening on port `2375`.

STEP 3: You need to manually edit the inbound firewall rules to allow access to this port.


The security of the connection to the remote docker daemon is established by the
TLS certificates in `~/.docker/machine/machines/samplesitehost/`.
The settings required to configure docker to build and deploy containers on the
remote host `samplesitehost` can be displayed using the command:

    docker-machine env samplesitehost



Using docker on the remote docker host
--------------------------------------

In order to configure docker to build and run containers on `samplesitehost`, we must
inject the appropriate env variables which will tell the local docker command
where it should work:

    eval $(docker-machine env samplesitehost)

After running this, all docker commands will be send to the remote `samplesitehost`.



Start/update/deploy
-------------------

Build a docker image:

    eval $(docker-machine env samplesitehost)
    docker build .  --tag samplesite-docker-img

Start a container from the above image:

    docker run \
      --publish 80:80 \
      --detach \
      --name samplesite \
      samplesite-docker-img


Check if it's running:

    docker ps




Shutting down
-------------

To stop the running container:

    eval $(docker-machine env samplesitehost)
    docker ps                     # to find the running container IDs
    docker stop <container_id>

To destroy the machine:

    docker-machine rm samplesitehost



