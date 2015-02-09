# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
import os
import sys
import platform
import subprocess

platform_system = platform.system().lower()


def set_expected_deps():
    """
    Returns a hardcoded list of expected deps for every supported OS.
    """
    expected_deps = []
    # Linux specific deps.
    if platform_system == 'linux':
        # The minimal list of deps covering Debian, Ubuntu and SUSE:
        # glibc, openssl and zlib.
        expected_deps = [
            'ld-linux',
            'libc.so',
            'libcrypt.so',
            'libcrypto.so',
            'libdl.so',
            'libm.so',
            'libnsl.so',
            'libpthread.so',
            'libssl.so',
            'libutil.so',
            'libz.so',
            'linux-gate.so',
            'linux-vdso.so',
            ]
        # Distro-specific deps to add. Now we may specify major versions too.
        linux_distro_name = platform.linux_distribution()[0]
        if ('Red Hat' in linux_distro_name) or ('CentOS' in linux_distro_name):
            expected_deps.extend([
                'libcom_err.so.2',
                'libgssapi_krb5.so.2',
                'libk5crypto.so.3',
                'libkrb5.so.3',
                'libresolv.so.2',
                ])
            rhel_version = int(platform.linux_distribution()[1].split('.')[0])
            if rhel_version >= 5:
                expected_deps.extend([
                    'libkeyutils.so.1',
                    'libkrb5support.so.0',
                    'libselinux.so.1',
                    'libsepol.so.1',
                ])
            if rhel_version >= 6:
                expected_deps.extend([
                    'libfreebl3.so',
                ])
            if rhel_version >= 7:
                expected_deps.extend([
                    'liblzma.so.5',
                    'libpcre.so.1',
                ])
    # AIX specific deps.
    elif platform_system == 'aix':
        # This is the standard list of deps for AIX 5.3.
        expected_deps = [
            '/unix',
            'libbsd.a',
            'libc.a',
            'libcrypt.a',
            'libcrypto.a',
            'libdl.a',
            'libnsl.a',
            'libpthreads.a',
            'libpthreads_compat.a',
            'libssl.a',
            'libtli.a',
            'libz.a',
            ]
        # sys.platform could be 'aix5', 'aix6' etc.
        aix_version = int(sys.platform[-1])
        if aix_version >= 7:
            expected_deps.extend([
                'libthread.a',
            ])
    # Solaris specific deps.
    elif platform_system == 'sunos':
        # This is the standard list of deps for a Solaris 10 build.
        # For now, we include the major versions for Solaris libs.
        expected_deps = [
            'libaio.so.1',
            'libc.so.1',
            'libcrypt_i.so.1',
            'libcrypto.so.0.9.7',
            'libcrypto_extra.so.0.9.7',
            'libdl.so.1',
            'libdoor.so.1',
            'libgen.so.1',
            'libintl.so.1',
            'libm.so.2',
            'libmd.so.1',
            'libmp.so.2',
            'libnsl.so.1',
            'librt.so.1',
            'libscf.so.1',
            'libsocket.so.1',
            'libsqlite3.so.0',
            'libssl.so.0.9.7',
            'libssl_extra.so.0.9.7',
            'libuutil.so.1',
            'libz.so.1',
            ]
    # OS X specific deps.
    elif platform_system == 'darwin':
        # This is the minimum list of deps for OS X.
        expected_deps = [
            'ApplicationServices.framework/Versions/A/ApplicationServices',
            'Carbon.framework/Versions/A/Carbon',
            'CoreFoundation.framework/Versions/A/CoreFoundation',
            'CoreServices.framework/Versions/A/CoreServices',
            'SystemConfiguration.framework/Versions/A/SystemConfiguration',
            'libSystem.B.dylib',
            'libcrypto.0.9.8.dylib',
            'libgcc_s.1.dylib',
            'libssl.0.9.8.dylib',
            'libz.1.dylib',
            ]
    return expected_deps


def get_actual_deps():
    """
    Returns the list of actual deps obtained using a bash script helper.
    """
    try:
        actual_deps = subprocess.check_output('./get_binaries_deps.sh',
            shell=True).split()
    except:
        print 'Could not determine the deps for the new binaries.'
    else:
        return actual_deps


def check_deps(expected_deps, actual_deps):
    """
    Returns unwanted deps for the python binary or the .so files in 'build/'.
    """
    # Check actual deps one by one to see if there is a substring of each of
    # them in any dep from the list of expected deps. This is so that an actual
    # dep of libssl.so.0.9.8 or libssl.so.1.0.0 matches an expected dep of
    # libssl.so when checking for OpenSSL.
    unwanted_deps = []
    for single_actual_dep in actual_deps:
        for single_expected_dep in expected_deps:
            if single_expected_dep in single_actual_dep:
                break
        else:
            unwanted_deps.append(single_actual_dep)
    return unwanted_deps

def main():
    """
    Launches tests to check required modules and OS-specific dependencies.
    Exits with a relevant error code.
    """
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

    if ( platform_system == 'linux' ) or ( platform_system == 'sunos' ):
        # On Linux and Solaris we need spwd, but not on AIX or OS X.
        try:
            import spwd
            spwd
        except:
            print 'spwd missing.'
            exit_code = 1

    # Finally, compare the list of expected deps for the current OS with the
    # list of actual deps returned by the shell script helper.
    expected_deps = set_expected_deps()
    if not expected_deps:
        print 'List of expected deps is empty. Unsupported OS?'
        exit_code = 13
    else:
        actual_deps = get_actual_deps()
        if not actual_deps:
            print 'List of deps is empty. Problems running the script helper?'
            exit_code = 14
        else:
            unwanted_deps = check_deps(expected_deps, actual_deps)
            if unwanted_deps:
                print 'Got unwanted deps:'
                for single_dep_to_print in unwanted_deps:
                    print '\t' , single_dep_to_print
                exit_code = 15

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
