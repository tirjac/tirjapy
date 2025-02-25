#!/bin/bash

export SRCDIR=$(dirname $(cd ${0%/*} 2>>/dev/null ; echo `pwd`/${0##*/}))
. ${SRCDIR}/00_script_config.sh

# main
mkdir build
bash scripts/02_run_python.sh -m build
