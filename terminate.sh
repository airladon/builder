BUILDER_RUNNING=`docker ps | grep builder-prod`
NGINX_RUNNING=`docker ps | grep nginx-server`

if [ "$BUILDER_RUNNING" ];
then
  echo Stopping builder-prod
  docker stop builder-prod
fi
if [ "$NGINX_RUNNING" ];
then
  echo Stopping nginx-server
  docker stop nginx-server
fi

BUILDER_EXISTS=`docker ps -a | grep builder-prod`
NGINX_EXISTS=`docker ps -a | grep nginx-server`

if [ "$BUILDER_RUNNING" ];
then
  echo Removing builder-prod
  docker rm builder-prod
fi
if [ "$NGINX_RUNNING" ];
then
  echo Removing nginx-server
  docker rm nginx-server
fi
