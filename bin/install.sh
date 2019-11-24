#!/bin/bash

BINDIR=$(dirname $0)

python3 -c 'import sys; sys.exit(0) if hasattr(sys, "real_prefix") else sys.exit(1)'
INVENV=$?
if [ "$INVENV" = "1" ]; then
    echo "Cannot install. This code requires virtualenv"
    exit 1
fi

pip3 install -r $BINDIR/../etc/requirements.txt 
