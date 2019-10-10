# builder


sudu ufw apply 5023
sudu ufw apply 5020
git clone https://github.com/airladon/builder builder
cd builder
git checkout temp

./start_ngingx.sh
./start_env.sh prod