#!/bin/bash

set -eu -o pipefail

function release_ip_lists() {
    dirname=$1
    pushd $dirname
    git init
    git config --local user.email "github-action@users.noreply.github.com"
    git config --local user.name "GitHub Action"
    git remote add origin https://github-action:$GITHUB_TOKEN@github.com/Detavern/bgpip-tools.git
    git branch -M $dirname
    git add .
    git commit -m "update ip lists at $(date +%Y-%m-%d)"
    git push -f origin $dirname
    popd
}

release_ip_lists ip-lists
release_ip_lists ip-lists-nightly
