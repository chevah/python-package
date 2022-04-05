#!/bin/bash

# Create a virtualenv in order to ensure that we do all of our testing
# with the oldest supported version of Python (3.6) and that that
# version of Python actually works.  We also install the 'codecov'
# utility in the virtualenv; it will be used by travis-after-success.

set -ex
rm -rf build/
mkdir build/

if command -V python3.6; then
    python3.6 -m venv build/venv
else
    python3 -m venv build/venv
fi

. build/venv/bin/activate

python --version
python -c 'import sys, pprint; pprint.pprint(sys.path)'
python -m pip install --upgrade pip wheel
python -m pip install codecov
