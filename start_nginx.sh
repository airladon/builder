cp containers/Dockerfile_nginx Dockerfile
docker build -t nginx-local .
rm Dockerfile
docker run --name nginx-server -p 80:80 -v /etc/nginx/conf -d nginx-local