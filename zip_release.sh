#!/bin/bash

echo "VERSION = '$1'.split('/')[-1]" > package/python2/byplay/version.py
echo "VERSION = '$1'.split('/')[-1]" > package/python3/byplay/version.py

cd package
zip -r ../package.zip *.pyp python2/**/*.py python3/**/*.py