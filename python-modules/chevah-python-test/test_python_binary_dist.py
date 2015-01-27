# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
import os
import sys
import platform
import subprocess
platform_system = platform.system().lower()
exit_code = 0

try:
    import zlib
    zlib
except:
    print '"zlib" missing.'
    exit_code = 1

try:
    import _hashlib
    _hashlib
except:
    print 'standard "ssl" missing.'
    exit_code = 1

try:
    from OpenSSL import SSL, crypto, rand
    SSL
    crypto
    rand
except:
    print '"OpenSSL" missing.'
    exit_code = 1

try:
    import Crypto
    Crypto
except:
    print '"PyCrypto" missing.'
    exit_code = 1


try:
    import crypt
    crypt
except:
    print '"crypt" missing.'
    exit_code = 1

try:
    import pysqlite2
    pysqlite2
except:
    print '"pysqlite2" missing.'
    exit_code = 1

try:
    import setproctitle
    setproctitle
except:
    print '"setproctitle" missing.'
    exit_code = 1

try:
    from ctypes import CDLL
    CDLL
except:
    print '"ctypes - CDLL" missing.'
    exit_code = 1

try:
    from ctypes.util import find_library
    find_library
except:
    print '"ctypes.utils - find_library" missing.'
    exit_code = 1

try:
    from Crypto.PublicKey import _fastmath
    _fastmath
except:
    print 'Crypto.PublicKey._fastmath missing. No GMP?'
    exit_code = 1

# Windows specific modules.
if os.name == 'nt':
    try:
        from ctypes import windll
        windll
    except:
        print '"ctypes - windll" missing.'
        exit_code = 1

# Linux specific modules.
if platform_system == 'linux':
    # On Linux we need spwd... but not on all Unix system, ex: AIX
    try:
        import spwd
        spwd
    except:
        print 'spwd missing.'
        exit_code = 1

    # We compare the deps of the new binaries with a minimal list of deps:
    # glibc, openssl and zlib.
    try:
        actual_deps = subprocess.check_output("./test_binaries_deps.sh", \
            shell=True).split()
    except:
        print "Couldn't determine the deps for the new binaries."
        exit_code = 13
    else:
        expected_deps = [ \
            "ld-linux", \
            "libc.so", \
            "libcrypt.so", \
            "libcrypto.so", \
            "libdl.so", \
            "libm.so", \
            "libnsl.so", \
            "libpthread.so", \
            "libssl.so", \
            "libutil.so", \
            "libz.so", \
            "linux-gate.so", \
            ]
        # We check actual deps one by one to see if there is a substring of
        # each of them in any dep from the list of expected deps.
        # This is so that an actual dep of libssl.so.0.9.8 or libssl.so.1.0.0
        # matches an expected dep of libssl.so when checking for OpenSSL.
        unexpected_deps = []
        for single_actual_dep in actual_deps:
            found_dep = ""
            for single_expected_dep in expected_deps:
                if single_expected_dep in single_actual_dep:
                    found_dep = single_expected_dep
                    break
            if not found_dep:
                unexpected_deps.append(single_actual_dep)
        if unexpected_deps:
            print "Got unexpected deps:"
            for single_dep_to_print in unexpected_deps:
                print "\t" , single_dep_to_print
            exit_code=14

sys.exit(exit_code)
