#!/bin/bash
sed -i 's|localhost|'"${DBHOST}"'|g' app.js

export NODE_ENV=production
export NVM_HOME=${IROOT}/nvm
# Used to avoid nvm's return 2 error.
# Sourcing this functions if 0 is returned.
source $NVM_HOME/nvm.sh || 0
nvm install iojs-v1.8.1
nvm use iojs-v1.8.1

# update npm before app init
npm install -g npm

# run app
npm install
iojs app &