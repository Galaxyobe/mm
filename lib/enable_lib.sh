#!/bin/bash

# Add lib to python2.7 lib,than's python PATH can load it.

cat <<EOF | sudo tee /usr/local/lib/python2.7/dist-packages/org.pth
$PWD
EOF