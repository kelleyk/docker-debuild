#!/usr/bin/env bash

set -e

# Container accepts DOCKER_DEBUILD_OPTS variable.

CONTAINER_ID=$(docker run -d --rm \
  -v "${SOURCE_VOL_PATH}":/source:ro \
  -v "${BUILD_VOL_PATH}":/build:rw \
  kelleyk/debuild:utopic)
docker attach "${CONTAINER_ID}"

CONTAINER_EXITCODE="$(docker inspect --format='{{.State.ExitCode}}' "${CONTAINER_ID}")"
exit $CONTAINER_EXITCODE
