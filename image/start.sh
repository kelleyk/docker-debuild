#!/usr/bin/env bash

if [ "$(ls -A /build)" ]; then
    >&2 echo "E: Build volume is not empty; boldly refusing to clear it out myself."
    >&2 echo "E: Empty it or give me a different volume to work in."
    exit -1
fi

if ! [ "$(ls -A /source)" ]; then
    >&2 echo "E: Source volume is empty; what were you expecting me to do?"
    exit -1
fi

cp -a /source/* /build

apt-get update

for i; do (
	set -e
	cd $i
	mk-build-deps --install --remove --tool "apt-get --no-install-recommends --yes"
	eval "debuild $DOCKER_DEBUILD_OPTS -us -uc --lintian-opts --allow-root"
)
done
