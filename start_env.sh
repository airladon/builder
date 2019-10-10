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
  HOST_PORT=5002
  CONTAINER_PORT=5000
  CMD="/opt/app/deploy_pipeline.sh"
  DOCKERFILE="Dockerfile_dev"
fi

echo
echo "${bold}${cyan}================= Building container ===================${reset}"
cp containers/$DOCKERFILE Dockerfile

GUNICORN_PORT=4000
docker build -t builder-$1 .
rm Dockerfile

echo
echo "${bold}${cyan}================= Starting container ===================${reset}"
if [ $1 = 'prod' ];
then
  docker run -it --rm \
    --name builder-$1 \
    -p $HOST_PORT:$CONTAINER_PORT \
    --net=isolated_nw \
    --env PORT=$CONTAINER_PORT \
    --env-file=$PROJECT_PATH/containers/env.txt \
    builder-$1
else
  # docker volume create browser-tests
  # docker run 
  docker run -it --rm \
    -v $PROJECT_PATH/containers:/opt/app/containers \
    -v $PROJECT_PATH/.git:/opt/app/.git \
    -v $PROJECT_PATH/containers/dev/build.sh:/opt/app/build.sh \
    -v $PROJECT_PATH/containers/dev/deploy_pipeline.sh:/opt/app/deploy_pipeline.sh \
    -v $PROJECT_PATH/containers/dev/dev-server.sh:/opt/app/dev-server.sh \
    -v $PROJECT_PATH/containers/dev/addresses.yml:/opt/app/addresses.yml \
    -v $PROJECT_PATH/containers/dev/pytest.ini:/opt/app/pytest.ini \
    -v $PROJECT_PATH/tests:/opt/app/tests \
    -v $PROJECT_PATH/repo:/opt/app/repo \
    -v $PROJECT_PATH/app:/opt/app/app \
    -v $PROJECT_PATH/.flake8:/opt/app/.flake8 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --env-file=$PROJECT_PATH/containers/env.txt \
    -e HOST_PATH=$PROJECT_PATH/repo/clone \
    --name builder-$1 \
    -p $HOST_PORT:$CONTAINER_PORT \
    builder-$1 $CMD
fi
