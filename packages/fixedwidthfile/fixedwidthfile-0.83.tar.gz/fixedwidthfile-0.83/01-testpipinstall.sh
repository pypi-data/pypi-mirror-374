#!/usr/bin/bash

PKGNAME="fixedwidthfile"

# QA
# python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps "$PKGNAME"

# prod
python3 -m pip install --no-deps "$PKGNAME"
