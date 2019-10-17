#!/usr/bin/env bash

set -e

# tar up code
echo "Create archive with source code"
tar -czf log-server.tar.gz *

# upload code to server
echo "SCP source code to server"
scp -o StrictHostKeyChecking=no log-server.tar.gz root@aur-precooling.sl.cloud9.ibm.com:/root

# backup frontend and environment files
echo "Backup environment files"
ssh -o StrictHostKeyChecking=no root@aur-precooling.sl.cloud9.ibm.com 'cd /root/log-server && cp .env /root/.tmp/.env-log'

# stop service
echo "Stop service"
ssh -o StrictHostKeyChecking=no root@aur-precooling.sl.cloud9.ibm.com 'systemctl stop log-server.service'

# clean up backend
echo "Clean up existing installation"
ssh -o StrictHostKeyChecking=no root@aur-precooling.sl.cloud9.ibm.com 'rm -rf /root/log-server && mkdir /root/log-server'

# extract backend
echo "Extract new code"
ssh -o StrictHostKeyChecking=no root@aur-precooling.sl.cloud9.ibm.com 'cd /root && tar -xzf log-server.tar.gz -C /root/log-server && rm -f log-server.tar.gz'

# restore backed up files
echo "Restore backed up files"
ssh -o StrictHostKeyChecking=no root@aur-precooling.sl.cloud9.ibm.com 'cd /root && mv /root/.tmp/.env-log /root/log-server/.env'

# start service
echo "Start service"
ssh -o StrictHostKeyChecking=no root@aur-precooling.sl.cloud9.ibm.com 'systemctl start log-server.service'
