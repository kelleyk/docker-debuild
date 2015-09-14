#!/usr/bin/env bash

set -e

# if [ "$(ls -A /build/buildd)" ]; then
#     >&2 echo "E: Build volume is not empty; boldly refusing to clear it out myself."
#     >&2 echo "E: Empty it or give me a different volume to work in."
#     exit -1
# fi

if ! [ "$(ls -A /build/buildd)" ]; then
    >&2 echo "E: Source volume is empty; what were you expecting me to do?"
    exit -1
fi

# XXX: Check that these aren't empty
TARGET_PKG="$1"
shift
TARGET_SUITE="$1"
shift

if test -n "${APT_PROXY_URL}"; then
    >&2 echo "I: Using apt proxy at ${APT_PROXY_URL}"
    echo "Acquire::http:Proxy \"${APT_PROXY_URL}\";" > /etc/apt/apt.conf.d/30proxy
else
    >&2 echo "W: Not using an apt proxy!"
fi

# cp -a /source/* /build/buildd

if ! test -d /build/buildd/"${TARGET_PKG}"; then
    >&2 echo "E: No source directory named \"${TARGET_PKG}\"."
    exit -1
fi
 
cd /build/buildd/"${TARGET_PKG}"

echo -e "\n************\nrunning apt-get update...\n************\n"
apt-get update

echo -e "\n************\nrunning mk-build-deps...\n************\n"
# This *should* create a package, --install it, and then --remove it; but it doesn't seem to do either.  (See similar situation reported here: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=753657)
mk-build-deps --install --remove --tool "apt-get --no-install-recommends --yes"
# Workaround:  (We make sure to remove the package, because otherwise git-buildpackage complains about the repo being unclean.)
BUILD_DEPS_PKG="$(find . -maxdepth 1 -iname '*build-deps_*.deb')"
if test -n "${BUILD_DEPS_PKG}"; then
    dpkg -i "${BUILD_DEPS_PKG}"
    rm "${BUILD_DEPS_PKG}"
fi

# eval "debuild $DOCKER_DEBUILD_OPTS -us -uc --lintian-opts --allow-root"
echo -e "\n************\nrunning debuild... \n************\n"

debuild "$@"

# --allow-root
# TODO: Do we need to ask for lintian?

########################
##
########################

