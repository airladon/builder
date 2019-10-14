#!/bin/bash

# Setup colors and text formatting
red=`tput setaf 1`
green=`tput setaf 2`
cyan=`tput setaf 6`
yellow=`tput setaf 3`
bold=`tput bold`
reset=`tput sgr0`

# Default values of variables
DOCKERFILE='Dockerfile_prod'
HOST_PORT=5000
CMD=''
PROJECT_PATH=`pwd`
FAIL=0

LOCAL_PROJECT_PATH=`pwd`
if [ $HOST_PATH ];
then
  PROJECT_PATH=$HOST_PATH
else
  PROJECT_PATH=`pwd`
fi

stop_dev_server() {
  SERVER_RUNNING=`docker ps --format {{.Names}} \
                | grep builder-dev-server`
  if [ $SERVER_RUNNING ];
    then
    echo Dev server container is running - stopping...
    docker stop builder-dev-server
  fi
}

# Check environment variables
# $1: Deploy variable - can be "deploy" or "no_deploy"
# $2: ENV name
check_env_exists() {
  if [ -z ${!1} ];
  then
    echo "${bold}${yellow}Warning: $1 environment variable not set. $2${reset}"
  fi
}

# Check current build status and exit if in failure state
check_status() {
  if [ $FAIL != 0 ];
    then
    echo "${bold}${red}Build failed at${bold}${cyan}" $1 "${reset}"
    exit 1    
  fi
}

echo
echo "${bold}${cyan}============ Checking Environment Variables ============${reset}"
# check_env_exists MAIL_SERVER "Emails will not be sent by app."
# check_status "Checking environment variables"
# echo "Environment variable checking complete"


if [ $1 ];
then
  DOCKERFILE=Dockerfile_$1
fi

if [ $1 = "prod" ];
then
  HOST_PORT=5020
  CONTAINER_PORT=4000
  stop_dev_server
fi

if [ $1 = "stage" ];
then
  HOST_PORT=5021
  CONTAINER_PORT=5000
fi

if [ $1 = "dev" ];
then
  HOST_PORT=5022
  CONTAINER_PORT=5000
fi

if [ $1 = 'dev-server' ];
then
  HOST_PORT=5023
  CONTAINER_PORT=5000
  DOCKERFILE="Dockerfile_dev"
  CMD=/opt/app/dev-server.sh
fi

if [ $1 = 'deploy_pipeline' ];
then
  HOST_PORT=5024
  CONTAINER_PORT=5000
  CMD="/opt/app/deploy_pipeline.sh"
  DOCKERFILE="Dockerfile_dev"
fi

echo
echo "${bold}${cyan}================= Building container ===================${reset}"
cp containers/$DOCKERFILE DockerfileTemp
# set user id of new user in production container to the same user id of the 
# user calling the container so permissions of files work out ok
DOCKER_GROUP_ID=`grep -e '^docker:' /etc/group | sed 's/[^:]*:[^:]*:\([0-9]*\).*/\1/'`
if [ -z "$DOCKER_GROUP_ID" ];
then
  DOCKER_GROUP_ID=`ls -n /var/run/docker.sock | sed "s/[^ ]* *[^ ]* *\([^ ]*\).*/\1/"`
fi
HOST_USER_GROUP_ID=`id -g`
HOST_USER_ID=`id -u`

sed "s/HOST_USER_ID/${HOST_USER_ID}/;s/HOST_USER_GROUP_ID/${HOST_USER_GROUP_ID}/;s/DOCKER_GROUP_ID/${DOCKER_GROUP_ID}/" < DockerfileTemp > Dockerfile 
rm DockerfileTemp

docker build -t builder-$1 .
rm Dockerfile

echo
echo "${bold}${cyan}================= Starting container ===================${reset}"

if [ -z "$DOCKER_RESTART" ];
then
  DOCKER_RESTART=no
fi

if [[ $1 = 'prod' && $2 = 'debug' ]];
then
  docker run -it --rm \
    --name builder-$1 \
    --net=isolated_nw \
    --env PORT=$CONTAINER_PORT \
    --env-file=$LOCAL_PROJECT_PATH/containers/env.txt \
    -v $PROJECT_PATH/logs:/opt/app/logs \
    -v $PROJECT_PATH/repo:/opt/app/repo \
    -v $PROJECT_PATH/tools:/opt/app/tools \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -e HOST_PATH=$PROJECT_PATH/repo/clone \
    builder-$1 bash
  # -p $HOST_PORT:$CONTAINER_PORT \

elif [ $1 = 'prod' ];
  then
    docker run -it \
    --name builder-$1 \
    --net=isolated_nw \
    --env PORT=$CONTAINER_PORT \
    --env-file=$LOCAL_PROJECT_PATH/containers/env.txt \
    -v $PROJECT_PATH/logs:/opt/app/logs \
    -v $PROJECT_PATH/repo:/opt/app/repo \
    -v $PROJECT_PATH/tools:/opt/app/tools \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -e HOST_PATH=$PROJECT_PATH/repo/clone \
    --restart $DOCKER_RESTART \
    -d \
    builder-$1
else
  # docker volume create browser-tests
  # docker run 
  docker run -it --rm \
    -v $PROJECT_PATH/containers:/opt/app/containers \
    -v $PROJECT_PATH/containers/dev/build.sh:/opt/app/build.sh \
    -v $PROJECT_PATH/containers/dev/deploy_pipeline.sh:/opt/app/deploy_pipeline.sh \
    -v $PROJECT_PATH/containers/dev/dev-server.sh:/opt/app/dev-server.sh \
    -v $PROJECT_PATH/containers/dev/addresses.yml:/opt/app/addresses.yml \
    -v $PROJECT_PATH/containers/dev/pytest.ini:/opt/app/pytest.ini \
    -v $PROJECT_PATH/tests:/opt/app/tests \
    -v $PROJECT_PATH/repo:/opt/app/repo \
    -v $PROJECT_PATH/tools:/opt/app/tools \
    -v $PROJECT_PATH/app:/opt/app/app \
    -v $PROJECT_PATH/.flake8:/opt/app/.flake8 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --env-file=$LOCAL_PROJECT_PATH/containers/env.txt \
    -e HOST_PATH=$PROJECT_PATH \
    --name builder-$1 \
    -p $HOST_PORT:$CONTAINER_PORT \
    builder-$1 $CMD
fi
