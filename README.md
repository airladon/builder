# builder


sudu ufw apply 5023
sudu ufw apply 5020
git clone https://github.com/airladon/builder builder
cd builder
git checkout temp


export LOCAL_PRODUCTION=DISABLE_SECURITY
docker network create --driver bridge isolated_nw
./start_env.sh prod
./start_nginx.sh
