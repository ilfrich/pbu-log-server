#!/bin/bash

set -e

########################
# VARIABLE DECLARATION #
########################

start_date=$(date)

REMOTE="$DEPLOY_SERVER"
SCP_OPTIONS="-rp -o StrictHostKeyChecking=no"
BASE_DIR=/home/$DEPLOY_USER/pbu-log-server
echo "Deploying to $REMOTE"
RSYNC_EXCLUDE="--exclude=.git --exclude=.idea --exclude=__pycache__ --exclude=_data --exclude=_logs --exclude=_temp --exclude=_output --exclude=*.ipynb --exclude=.pytest_cache --exclude=tests"

APP_DIR="$REMOTE:$BASE_DIR"
STATIC_DIR="$APP_DIR/static"
APP_DIR="$APP_DIR/"  # append trailing /

FOLDERS="api"
for folder in $FOLDERS; do
    echo "- Synchronizing PBU Log Server folder: $folder"
    rsync -avL $RSYNC_EXCLUDE -e "ssh" $folder $APP_DIR
done

# copying single files
scp $SCP_OPTIONS *.py $APP_DIR
# devops
scp $SCP_OPTIONS requirements.txt $APP_DIR
scp $SCP_OPTIONS Makefile $APP_DIR
# frontend
scp $SCP_OPTIONS templates $APP_DIR
# scp $SCP_OPTIONS static/images/* $STATIC_DIR/images/
scp $SCP_OPTIONS static/index.js $STATIC_DIR

# update dependencies
echo "- Updating PBU Log Server External Dependencies"
ssh $REMOTE "cd $BASE_DIR && pip3.11 install -r requirements.txt"

# restart service and print out date
echo "- Restarting PBU Log Server Service"
ssh $REMOTE "sudo systemctl restart $DEPLOY_APP"

# print start and end date
echo $start_date
date
