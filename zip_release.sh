#!/bin/bash

echo "VERSION = '$1'.split('/')[-1]" > package/python2/byplay/version.py
echo "VERSION = '$1'.split('/')[-1]" > package/python3/byplay/version.py
zip -r package.zip package/*.pyp package/python2/**/*.py package/python3/**/*.py