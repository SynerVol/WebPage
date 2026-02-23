#!/bin/bash


curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
. ~/.bashrc
nvm install 22
nvm use 22
node -v
rm -rf node_modules
npm install --legacy-peer-deps
#npm install socket.io-client --legacy-peer-deps
echo 'run "npm run dev -- --host" to launch'

