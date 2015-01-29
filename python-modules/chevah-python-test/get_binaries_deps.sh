#!/usr/bin/env bash

checker=ldd

# In Solaris 10, make sure we find OpenSSL libs (both 64/32 binaries).
uname -a | grep ^SunOS | grep " 5.10 " >/dev/null \
    && export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/sfw/lib/64:/usr/sfw/lib/"

os=$(uname)

# In OS X, there's no ldd.
[ "$os" = "Darwin" ] \
    && checker="otool -L"

# This portable invocation of find will get a raw list of linked libs
# for the current binaries in the 'build' sub-directory.
raw_list=$(find ./ -type f \( -name "python" -o -name "*.so" \) \
            -exec $checker {} \;)

# We exclude the eventual occuring lines listing the examined files as we
# know they start with './' and we select the first field with awk.
lib_list=$(echo "$raw_list" | grep -v ^\\./ | awk '{print $1}')

# For AIX and OS X, the output includes the full path. More so, some AIX 5.x
# libs from /usr/lib/ have moved to /lib in newer versions of AIX.
[ "$os" = "AIX" ] \
    && lib_list=$(echo "$lib_list" | sed s#^/usr##g | sed s#^/lib/##g \
                | cut -d \( -f1)
[ "$os" = "Darwin" ] \
    && lib_list=$(echo "$lib_list" | sed s#/System/Library/Frameworks/##g \
    | sed s#^/usr/lib/##g)

# Finally, we sort the list to eliminate duplicates.
echo "$lib_list" | sort | uniq
