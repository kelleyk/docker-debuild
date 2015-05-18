#!/usr/bin/env bash
#
# Usage: e.g.
#   ./run.sh my-package vivid [options...]
#
# Container accepts DOCKER_DEBUILD_OPTS variable; this is where your optional extra options go.

set -e


TARGET_PKG="$1"
shift
TARGET_SUITE="$1"
shift

IMAGE_TAG=ubuntu-"${TARGET_SUITE}"

SOURCE_VOL_PATH="${SOURCE_VOL_PATH-$PWD/source}"
BUILD_VOL_PATH="${BUILD_VOL_PATH-$PWD/build}"

CONTAINER_ID=$(docker run -d \
  -v "${SOURCE_VOL_PATH}":/source:ro \
  -v "${BUILD_VOL_PATH}":/build/buildd:rw \
  -e "DOCKER_DEBUILD_OPTS=$@" \
  kelleyk/debuild:"${IMAGE_TAG}" \
  /start.sh "${TARGET_PKG}" "${TARGET_SUITE}" "$@")
docker attach "${CONTAINER_ID}"
# docker rm "${CONTAINER_ID}"

echo -e "\n************\ncontainer is ${CONTAINER_ID}\n******************\n"

CONTAINER_EXITCODE="$(docker inspect --format='{{.State.ExitCode}}' "${CONTAINER_ID}")"
exit $CONTAINER_EXITCODE
