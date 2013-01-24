# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
import os
import sys
exit_code = 0

try:
    import zlib
    zlib
except:
    print '"zlib" missing.'
    exit_code = 1

try:
    import bz2
    bz2
except:
    print '"bz2" missing.'
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

if os.name == 'nt':
    try:
        from ctypes import windll
        windll
    except:
        print '"ctypes - windll" missing.'
        exit_code = 1

try:
    from ctypes.util import find_library
    find_library
except:
    print '"ctypes.utils - find_library" missing.'
    exit_code = 1

sys.exit(exit_code)
