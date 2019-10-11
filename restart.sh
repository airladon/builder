./terminate.sh

./start_env.sh prod

cp containers/Dockerfile_nginx Dockerfile
docker build -t nginx-local .
rm Dockerfile


if [ -z "$DOCKER_RESTART" ];
then
  DOCKER_RESTART=no
fi

docker run --restart $DOCKER_RESTART --name nginx-server -p 80:80 -d --net=isolated_nw nginx-local
