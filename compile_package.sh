#!/bin/zsh

function clear_and_copy() {
    rm -rf $1/
    mkdir -p $1/
    cp -r byplay $1/byplay/
}

dir_name="package/python2"
clear_and_copy $dir_name
3to2 --no-diffs -w -n $dir_name/byplay

find ./$dir_name/byplay -type f -exec sed -i '' 's#from typing .*##' {} \;

clear_and_copy "package/python3"

cp byplay/plugin_template.pyp package/