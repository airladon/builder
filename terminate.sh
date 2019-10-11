BUILDER_RUNNING=`docker ps | grep builder-prod`
NGINX_RUNNING=`docker ps | grep nginx-server`

if [ "$BUILDER_RUNNING" ];
then
  docker stop builder-prod
fi
if [ "$NGINX_RUNNING" ];
then
  docker stop builder-prod
fi

BUILDER_EXISTS=`docker ps -a | grep builder-prod`
NGINX_EXISTS=`docker ps -a | grep nginx-server`

if [ "$BUILDER_RUNNING" ];
then
  docker rm builder-prod
fi
if [ "$NGINX_RUNNING" ];
then
  docker rm builder-prod
fi
