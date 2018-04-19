#!/usr/bin/env bash
set -euf -o pipefail

if test -n "${KK_DEBUG_APT_KEYS+x}"; then
    echo "----------------------------------------"
    echo "- apt-key list"
    echo "----------------------------------------"
    apt-key list
    echo "----------------------------------------"
fi

/build-package.sh "$@"
