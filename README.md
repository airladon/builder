# Builder

Basic CI server that assumes project to test has a deploy_pipeline script.

## Arcitecture

Two containers are used to make the build server:
* nginx-server - web server container
* builder-prod - includes gunicorn, flask

The two containers talk to each other over a private network (see `isolated_nw` below).

The ngingx-server has PORT 80 exposed for http traffic.


## Setup Server

### DO Ubuntu server

Here a simple Ubuntu server is created that will host `builder`, and the generated logs files.

#### Create droplet
Include the pulic key from the .ssh directory

#### ssh into droplet as root
```
ssh -i ~/.ssh/<ssh_key_file> root@<DROPLET_IP>
```

#### Create a user account
```
set -x \
&& adduser <USER> -u 7777 \
&& usermod -aG sudo <USER> \
&& rsync --archive --chown=<USER>:<USER> ~/.ssh /home/<USER> \
&& set +x
```

#### Log out and log back in as the user
```
ssh -i ~/.ssh/<ssh_key_file> <USER>@<DROPLET_IP>
```

#### Install Docker and setup a private network for container to container communication
```
set -x \
&& curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - \
&& sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
&& sudo apt-get update \
&& sudo apt-get install -y docker-ce \
&& sudo usermod -aG docker ${USER} \
&& su - ${USER} \
&& set +x

docker network create --driver bridge isolated_nw
sudo chmod +775 /var/run/docker.sock
```

#### Setup Firewall
```
set -x \
&& sudo ufw allow OpenSSH \
&& sudo ufw allow http \
&& sudo ufw allow https \
&& sudo ufw enable \
&& sudo ufw status \
&& set +x
```

#### Add environment variables to \~/.bashrc
```
nano ~/.bashrc
```
export LOCAL_PRODUCTION=DISABLE_SECURITY
export HEROKU_API_KEY=<>
export DOCKER_RESTART=on-failure
export GITHUB_TOKEN=<>
export GITHUB_USERNAME=<>
export HOST_URL=http://`ip addr show | grep -e 'inet.*138.*eth0' | sed 's/inet *//' | sed 's/\/.*//' | sed 's/ *//g'`

```
source ~/.bashrc
```

#### Clone builder repository
```
git clone https://github.com/airladon/builder builder
cd builder
```

#### Start server
./restart.sh

## Debug Options

To enter the builder-prod container while it is running use:
```
docker exec -it builder-prod bash
```

