#!/bin/bash
export MY_VENV=${MY_VENV:="venv"}

if [ "`uname`" = "Darwin" ] ; then
	export DYLD_LIBRARY_PATH=${DYLD_LIBRARY_PATH}:/opt/homebrew/lib:${MY_VENV}/lib
fi

if [ ! -d ${MY_VENV} ] ; then echo "DIR  ${MY_VENV} missing"; exit 1; fi

source ${MY_VENV}/bin/activate

export PYTHONPATH="./src"
