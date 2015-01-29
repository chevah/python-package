#!/usr/bin/env bash

# In Solaris 10, make sure we find OpenSSL libs.
uname -a | grep ^SunOS | grep " 5.10 " \
    && export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/sfw/lib/64"

# This portable invocation of find will get a raw list of linked libs
# for the current binaries in the 'build' sub-directory.
raw_list=$(find ./ -type f \( -name "python" -o -name "*.so" \) -exec ldd {} \;)

# We exclude the eventual occuring lines listing the examined files as we
# know they start with './' and we select the first field with awk.
lib_list=$(echo "$raw_list" | grep -v ^\\./ | awk '{print $1}')

# For AIX, the output of ldd is different...
uname | grep -v AIX > /dev/null \
    && lib_list=$(echo "$lib_list" | sed s#^/usr##g | sed s#^/lib/##g | cut -d \( -f1)

# Finally, we sort the list to eliminate duplicates.
echo "$lib_list" | sort | uniq
