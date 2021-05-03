#!/bin/bash

set -e
set -x

# # WOOPS, this need changing to miniconda !!!!

# echo "Installing a fresh version of maxiconda."
# MAXICONDA_URL="https://github.com/conda-forge/maxiconda/releases/download/4.8.3-1"
# MAXICONDA_FILE="maxiconda-4.8.3-1-MacOSX-x86_64.sh"
# curl -L -O "${MAXICONDA_URL}/${MAXICONDA_FILE}"
# bash $MAXICONDA_FILE -b

# echo "Configuring conda."
# source ~/maxiconda/bin/activate root

# export CONSTRUCT_ROOT=$PWD
# mkdir -p build


if [ "$TARGET_ARCH" == "$(uname -m)" ] && [ "$TARGET_OS" == "$(uname)"]
then
  printf "Building the maxiconda metapackage for $TARGET_OS/$TARGET_ARCH\\n"

else
  printf "On $(uname)/$(uname -m), can not build maxiconda for $TARGET_OS/$TARGET_ARCH\\n"
  exit 1
fi
