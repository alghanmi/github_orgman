#!/bin/sh

##
## Git Repo Update
##   Keep a set of git repos up to date including all branches
##

LAST_PWD=$PWD
USAGE_MESSAGE="Keep a set of git repos up to date. Usage:\n$0 REPOS_DIR LOG_DIR"

if [ $# -eq 0 ]; then
    echo -e $USAGE_MESSAGE
    exit 0
fi

if [ $# -ne 2 ]; then
    echo -e $USAGE_MESSAGE
    exit 1
fi

if [ ! -d $1 ]; then
    echo "$1 is not a valid directory. Please provide a valid directory"
    exit 1
fi

if [ ! -d $2 ]; then
    echo "$2 is not a valid directory. Please provide a valid directory for logs"
    exit 1
fi

#Log File
_LOG_TIME="$(date +%Y-%m-%d_%H%M)"
_LOG_FILE_NAME="$2/repo-update_${_LOG_TIME}.log"
touch $_LOG_FILE_NAME
_LOG_FILE="$(readlink -e $_LOG_FILE_NAME)"


#Load SSH Keys
eval $(ssh-agent) >> $_LOG_FILE 2>&1
ssh-add >> $_LOG_FILE 2>&1

#Find the list of repos and script absolute paths
_REPOS_HOME=$(readlink -e $1)
_REPOS=$(find $_REPOS_HOME -mindepth 1 -maxdepth 1 -type d)

#Apply script on all paths
for _REPO in $_REPOS
do
    cd $_REPO
    echo "Working on $_REPO" >> $_LOG_FILE
    git remote update  >> $_LOG_FILE 2>&1
    git pull --all --quiet  >> $_LOG_FILE 2>&1
done


# Return back to original directory
cd $LAST_PWD

## confirmation log
echo "$_LOG_TIME All repositories in: $_REPOS_HOME were successfully updated" >> $2/confirmation.log

