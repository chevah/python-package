#!/usr/bin/env bash

set -o nounset
set -o errexit
set -o pipefail

checker=ldd
os=$(uname)

# In OS X, there's no ldd.
if [ "$os" = "Darwin" ]; then
    checker="otool -L"
fi

# In Solaris 10, make sure we find the OpenSSL libs (both 64/32 binaries).
if [ "$os" = "SunOS" ]; then
    # We need a trick to avoid "unbound variables" errors with "set -o nounset".
    # https://www.gnu.org/software/bash/manual/bashref.html#Shell-Parameter-Expansion
    export LD_LIBRARY_PATH="${LD_LIBRARY_PATH:+$LD_LIBRARY_PATH:}/usr/sfw/lib/64:/usr/sfw/lib/"
fi

# This portable invocation of find will get a raw list of linked libs
# for the current binaries in the current sub-directory: 'build'.
raw_list=$(find ./ -type f \( -name "python" -o -name "*.so" \) \
            -exec $checker {} \;)

# We exclude any occuring lines listing the examined files as we
# know they start with './' and we select the first fields with awk.
lib_list=$(echo "$raw_list" | grep -v ^\\./ | awk '{print $1}')

# For AIX and OS X, the output includes the full path. More so, some
# AIX 5.x libs from /usr/lib/ have moved to /lib in newer AIX versions.
if [ "$os" = "AIX" ]; then
    >&2 echo -n "Beware that in AIX we cut /lib/ and /usr/lib/ prefixes from the "
    >&2 echo    "full paths to the libs in the list."
    lib_list=$(echo "$lib_list" | sed s#^/usr##g | sed s#^/lib/##g \
                | cut -d \( -f1)
elif [ "$os" = "Darwin" ]; then
    >&2 echo -n "Beware that in OS X we cut /System/Library/Frameworks/ and "
    >&2 echo    "/usr/lib/ prefixes from the full paths to the libs in the list."
    lib_list=$(echo "$lib_list" | sed s#/System/Library/Frameworks/##g \
                | sed s#^/usr/lib/##g)
fi

# Finally, we sort the list to remove duplicates.
echo "$lib_list" | sort | uniq
