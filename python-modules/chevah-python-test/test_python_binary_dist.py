# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
import os
import sys
import platform
import subprocess

script_helper = './get_binaries_deps.sh'
platform_system = platform.system().lower()


def get_allowed_deps():
    """
    Return a hardcoded list of allowed deps for the current OS.
    """
    allowed_deps = []
    if platform_system == 'linux':
        # The minimal list of deps covering Debian, Ubuntu and SUSE:
        # glibc, openssl and zlib.
        allowed_deps = [
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
            allowed_deps.extend([
                'libcom_err.so.2',
                'libgssapi_krb5.so.2',
                'libk5crypto.so.3',
                'libkrb5.so.3',
                'libresolv.so.2',
                ])
            rhel_version = int(platform.linux_distribution()[1].split('.')[0])
            if rhel_version >= 5:
                allowed_deps.extend([
                    'libkeyutils.so.1',
                    'libkrb5support.so.0',
                    'libselinux.so.1',
                    'libsepol.so.1',
                ])
            if rhel_version >= 6:
                allowed_deps.extend([
                    'libfreebl3.so',
                ])
            if rhel_version >= 7:
                allowed_deps.extend([
                    'liblzma.so.5',
                    'libpcre.so.1',
                ])
    elif platform_system == 'aix':
        # This is the standard list of deps for AIX 5.3.
        allowed_deps = [
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
            allowed_deps.extend([
                'libthread.a',
            ])
    elif platform_system == 'sunos':
        # This is the standard list of deps for a Solaris 10 build.
        # For now, we include the major versions for Solaris libs.
        allowed_deps = [
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
    elif platform_system == 'darwin':
        # This is the minimum list of deps for OS X.
        allowed_deps = [
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
    return allowed_deps


def get_actual_deps():
    """
    Return the list of actual deps for the newly-built binaries.
    """
    try:
        raw_deps = subprocess.check_output(script_helper).splitlines()
    except:
        sys.stderr.write('Could not get the deps for the new binaries.\n')
    else:
        libs_deps = []
        for line in raw_deps:
            # We exclude any occuring lines listing the examined files as we
            # know they start with './' (this is a problem in AIX and OS X).
            if line[:2] != './' :
                libs_deps.append(line.split()[0])
        return list(set(libs_deps))


def get_unwanted_deps(allowed_deps, actual_deps):
    """
    Return unwanted deps for the newly-built binaries.
    allowed_deps are hardcoded deps for binaries built for the current OS.
    actual_deps are the deps found for the newly-built binaries.
    """
    # Check actual deps one by one to see if there is a substring of each of
    # them in any dep from the list of allowed deps. This is so that an actual
    # dep of libssl.so.0.9.8 or libssl.so.1.0.0 matches an allowed dep of
    # libssl.so when checking for OpenSSL.
    unwanted_deps = []
    for single_actual_dep in actual_deps:
        for single_allowed_dep in allowed_deps:
            if single_allowed_dep in single_actual_dep:
                break
        else:
            unwanted_deps.append(single_actual_dep)
    return unwanted_deps


def main():
    """
    Launch tests to check required modules and OS-specific dependencies.
    Exit with a relevant error code.
    """
    exit_code = 0

    try:
        import zlib
        zlib
    except:
        sys.stderr.write('"zlib" missing.\n')
        exit_code = 1

    try:
        import _hashlib
        _hashlib
    except:
        sys.stderr.write('standard "ssl" missing.\n')
        exit_code = 2

    try:
        from OpenSSL import SSL, crypto, rand
        SSL
        crypto
        rand
    except:
        sys.stderr.write('"OpenSSL" missing.\n')
        exit_code = 3

    try:
        import Crypto
        Crypto
    except:
        sys.stderr.write('"PyCrypto" missing.\n')
        exit_code = 4

    try:
        import crypt
        crypt
    except:
        sys.stderr.write('"crypt" missing.\n')
        exit_code = 5

    try:
        import pysqlite2
        pysqlite2
    except:
        sys.stderr.write('"pysqlite2" missing.\n')
        exit_code = 6

    try:
        import setproctitle
        setproctitle
    except:
        sys.stderr.write('"setproctitle" missing.\n')
        exit_code = 7

    try:
        from ctypes import CDLL
        CDLL
    except:
        sys.stderr.write('"ctypes - CDLL" missing.\n')
        exit_code = 8

    try:
        from ctypes.util import find_library
        find_library
    except:
        sys.stderr.write('"ctypes.utils - find_library" missing.\n')
        exit_code = 9

    try:
        from Crypto.PublicKey import _fastmath
        _fastmath
    except:
        sys.stderr.write('Crypto.PublicKey._fastmath missing. No GMP?\n')
        exit_code = 10

    # Windows specific modules.
    if os.name == 'nt':
        try:
            from ctypes import windll
            windll
        except:
            sys.stderr.write('"ctypes - windll" missing.\n')
            exit_code = 11

    if ( platform_system == 'linux' ) or ( platform_system == 'sunos' ):
        # On Linux and Solaris we need spwd, but not on AIX or OS X.
        try:
            import spwd
            spwd
        except:
            sys.stderr.write('spwd missing.\n')
            exit_code = 12

    # Compare the list of allowed deps for the current OS with the list of
    # actual deps for the newly-built binaries returned by the script helper.
    allowed_deps = get_allowed_deps()
    if not allowed_deps:
        sys.stderr.write('Got no allowed deps. Please check if {0} is a ' \
            'supported operating system.\n'.format(platform.system()))
        exit_code = 13
    else:
        actual_deps = get_actual_deps()
        if not actual_deps:
            sys.stderr.write('Got no deps for the new binaries. Please check ' \
                'the "{0}" script in the "build/" dir.\n'.format(script_helper))
            exit_code = 14
        else:
            unwanted_deps = get_unwanted_deps(allowed_deps, actual_deps)
            if unwanted_deps:
                sys.stderr.write('Got unwanted deps:\n')
                for single_dep_to_print in unwanted_deps:
                    sys.stderr.write('\t{0}\n'.format(single_dep_to_print))
                exit_code = 15

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
