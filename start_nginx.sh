cp containers/Dockerfile_nginx Dockerfile
docker build -t nginx-local .
rm Dockerfile
docker run --rm --name nginx-server -p 80:80 -d nginx-local