#!/usr/bin/env bash

set -e

########################
## Wait for signal from process
########################

# resume() {
#     kill "$PID"
# }

# trap resume SIGUSR1
# while true; do
#     sleep 1 &
#     PID="$!"
#     wait "$PID" 2>/dev/null || break
# done
# trap - SIGUSR1

########################
##
########################

# # @KK: In 14.04 and earlier, unshare does not have --user yet.  We would need to backport the
# # 'unshare' utility (or all of util-linux); or, probably more effectively, go for a pure-python
# # implementation (and then include Python in our build image).

# # XXX: Failing error codes do not seem to be passed back by 'unshare'.
# sudo -u '#1000' unshare --user --map-root-user /build-package.sh "$@"

/build-package.sh "$@"
