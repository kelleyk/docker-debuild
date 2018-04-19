#!/usr/bin/env bash
set -euf -o pipefail

declare -a SUITES
if test $# -eq 0; then
    SUITES=("zesty" "yakkety" "xenial" "wily" "trusty")
else
    SUITES=("$@")
fi

for SUITE in "${SUITES[@]}"; do
    echo "*** updating base image: ${SUITE}"

    IMAGE_TAG_NAME="kelleyk/debuild"
    IMAGE_TAG_VERSION=ubuntu-"${SUITE}"
    FROM_IMAGE=ubuntu:"${SUITE}"

    docker pull "${FROM_IMAGE}"
    
    apt-config-tool image/apt-config.yaml image/apt-config.sh
    sed -e "s/FROM_IMAGE/$FROM_IMAGE/g" image/Dockerfile.in > image/Dockerfile

    echo "*** building image: ${SUITE}"
    docker build -t "${IMAGE_TAG_NAME}":"${IMAGE_TAG_VERSION}" image/
done
