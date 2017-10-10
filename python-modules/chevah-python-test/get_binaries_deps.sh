#!/usr/bin/env bash

# Uses 'ldd' or equivalents to list all dependencies for the python binary and
# .so files in the current hierarchy of directories (to be run in 'build/').

set -o nounset
set -o errexit
set -o pipefail

checker="ldd"
os="$(uname)"

if [ "$os" = "Darwin" ]; then
    checker="otool -L"
elif [ "$os" = "SunOS" ]; then
    # In Solaris 10, make sure we find the OpenSSL libs (both 64/32 binaries).
    # We need a trick to avoid "unbound variables" errors with "set -o nounset".
    # https://www.gnu.org/software/bash/manual/bashref.html#Shell-Parameter-Expansion
    export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:+$LD_LIBRARY_PATH:}/usr/sfw/lib/64:/usr/sfw/lib/"
    # By default, Solaris' ldd picks up too many libs, including some very
    # specific libs from /platform on Sparc in Solaris 10.
    checker="ldd -L"
elif [ "$os" = "HP-UX" ]; then
    checker="/usr/ccs/bin/ldd"
elif [ "$os" = "Linux" ]; then
    if [ -f /etc/alpine-release ]; then
        # musl's ldd has issues with some Python modules, so we use lddtree,
        # which is forked from pax-utils and installed by default in Alpine.
        checker="lddtree -l"
    fi
fi

# This portable invocation of find will get a raw list of linked libs
# for the current binaries in the current sub-directory, usually 'build'.
find ./ -type f \( -name "python" -o -name "*.so" \) -exec $checker {} \;
