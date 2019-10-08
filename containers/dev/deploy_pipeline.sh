#!/bin/bash

# Setup colors and text formatting
red=`tput setaf 1`
green=`tput setaf 2`
cyan=`tput setaf 6`
yellow=`tput setaf 3`
bold=`tput bold`
reset=`tput sgr0`

PROJECT_PATH=`pwd`

address_to_app() {
  echo "$1" | sed 's/dev: //' | sed 's/http[^\/]*\/\///' | sed 's/\.herokuapp.com.*//'
}
HEROKU_PROD_APP_NAME=$(address_to_app `cat addresses.yml | grep -e ^prod: | sed 's/prod: //'`)
if [ $HEROKU_PROD_ADDRESS ];
then
  HEROKU_PROD_APP_NAME=$(address_to_app $HEROKU_PROD_ADDRESS)
fi

check_status() {
  if [ $? != 0 ];
  then
    echo
    echo "${bold}${red}Build failed${reset}"
    echo
    exit 1
  else
    echo "${bold}${green}OK${reset}"
  fi
}

title() {
    echo
    echo "${bold}${cyan}=================== $1 ===================${reset}"
}

# From https://github.com/travis-ci/travis-ci/issues/4704 to fix an issue 
# where Travis errors out if too much information goes on stdout and some
# npm package is blocking stdout.
python -c 'import os,sys,fcntl; flags = fcntl.fcntl(sys.stdout, fcntl.F_GETFL); fcntl.fcntl(sys.stdout, fcntl.F_SETFL, flags&~os.O_NONBLOCK);'


###########################################################################
title "Run lint and local tests"
./build.sh prod
check_status

###########################################################################
title "Deploy to test server"
./build.sh deploy test skip-tests skip-build
check_status

title "Delay for test server to restart"
sleep 5s
check_status

# Run Deploy Tests here
title "Run tests on test server"
pytest tests/remote/test tests/remote/common --server test
check_status

###########################################################################
CURRENT_VERSION=`heroku releases -a "$HEROKU_PROD_APP_NAME" | sed -n '1p' | sed 's/^.*: //'`

title "Deploy to prod server - current: $CURRENT_VERSION"
./build.sh deploy prod skip-tests skip-build
check_status

title "Delay for prod server to restart"
sleep 5s
check_status

# Run Prod Tests here and Rollback if fail
title "Run tests on prod server"
pytest tests/remote/prod tests/remote/common --server prod
if [ $? != 0 ];
then
    heroku rollback $CURRENT_VERSION
    NEW_VERSION=`heroku releases -a "$HEROKU_PROD_APP_NAME" | sed -n '1p' | sed 's/^.*: //'`
    echo "${red}${bold}Production deployment failed${reset}"
    title "Rolling back to previous version"
    if [ "$NEW_VERSION" = "$CURRENT_VERSION" ];
    then
        echo "${green}${bold}OK - Rolled back to $CURRENT_VERSION${reset}"
        echo
    else
        echo "${red}${bold}FAIL - Rollback to $CURRENT_VERSION failed${reset}"
        echo
    fi
    exit 1
fi

