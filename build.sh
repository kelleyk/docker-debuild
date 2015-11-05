#!/usr/bin/env bash

set -e

#SUITES="vivid utopic trusty precise"
SUITES=wily

for SUITE in ${SUITES}; do

  IMAGE_TAG=ubuntu-"${SUITE}"
  FROM_IMAGE=ubuntu:"${SUITE}"

  apt-config-tool image/apt-config.yaml image/apt-config.sh
  sed -e "s/FROM_IMAGE/$FROM_IMAGE/g" image/Dockerfile.in > image/Dockerfile

  # echo -e "\n****"
  # cat image/apt-config.sh
  # echo -e "****\n"

  docker build -t kelleyk/debuild:"${IMAGE_TAG}" "$@" image/
  
done
