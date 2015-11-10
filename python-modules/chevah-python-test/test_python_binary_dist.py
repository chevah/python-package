# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
import os
import sys
import platform
import subprocess

script_helper = './get_binaries_deps.sh'
platform_system = platform.system().lower()
test_for_readline = False


def get_allowed_deps():
    """
    Return a hardcoded list of allowed deps for the current OS.
    """
    allowed_deps = []
    if platform_system == 'linux':
        # The minimal list of deps for Linux: glibc, openssl, zlib,
        # and, for readline support through libedit, a curses library.
        allowed_deps = [
            'ld-linux',
            'libc.so',
            'libcrypt.so',
            'libcrypto.so',
            'libdl.so',
            'libm.so',
            'libncursesw.so',
            'libnsl.so',
            'libpthread.so',
            'libssl.so',
            'libutil.so',
            'libz.so',
            'linux-gate.so',
            'linux-vdso.so',
            ]
        # Distro-specific deps to add. Now we may specify major versions too.
        with open('../DEFAULT_VALUES') as default_values_file:
            chevah_os = default_values_file.read().split(' ')[2]
        if ('rhel' in chevah_os):
            test_for_readline = True
            allowed_deps.extend([
                'libcom_err.so.2',
                'libgssapi_krb5.so.2',
                'libk5crypto.so.3',
                'libkrb5.so.3',
                'libresolv.so.2',
                ])
            rhel_version = int(chevah_os[4:])
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
                    'libtinfo.so.5',
                    ])
            if rhel_version >= 7:
                allowed_deps.extend([
                    'liblzma.so.5',
                    'libpcre.so.1',
                    ])
        elif ('sles' in chevah_os):
            test_for_readline = True
            sles_version = int(chevah_os[4:])
            if sles_version == 12:
                allowed_deps.extend([
                    'libtinfo.so.5',
                    ])
        elif ('ubuntu' in chevah_os):
            test_for_readline = True
            allowed_deps.extend([
                'libtinfo.so.5',
                ])
        elif ('raspbian' in chevah_os):
            test_for_readline = True
            allowed_deps.extend([
                'libcofi_rpi.so',
                'libgcc_s.so.1',
                'libncurses.so.5',
                'libtinfo.so.5',
                ])
    elif platform_system == 'aix':
        # This is the standard list of deps for AIX 5.3. Some of the links
        # for these libs moved in newer versions from '/usr/lib/' to '/lib/'.
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
        if aix_version >= 6:
            allowed_deps.extend([
                'libthread.a',
                ])
    elif platform_system == 'sunos':
        test_for_readline = True
        # This is the common list of deps for Solaris 10 & 11 builds.
        allowed_deps = [
            'libc.so.1',
            'libdl.so.1',
            'libintl.so.1',
            'libm.so.2',
            'libmd.so.1',
            'libmp.so.2',
            'libnsl.so.1',
            'libsocket.so.1',
            'libz.so.1',
            ]
        if platform.processor() == 'sparc':
            allowed_deps.extend([
                'libc_psr.so.1',
                'libmd_psr.so.1',
                ])
        # On Solaris, platform.release() can be: '5.9'. '5.10', '5.11' etc.
        solaris_version = platform.release().split('.')[1]
        if solaris_version == '10':
            # Specific deps to add for Solaris 10.
            allowed_deps.extend([
                'libaio.so.1',
                'libcrypt_i.so.1',
                'libcrypto.so.0.9.7',
                'libcrypto_extra.so.0.9.7',
                'libcurses.so.1',
                'libdoor.so.1',
                'libgen.so.1',
                'librt.so.1',
                'libscf.so.1',
                'libsqlite3.so',
                'libssl.so.0.9.7',
                'libssl_extra.so.0.9.7',
                'libthread.so.1',
                'libuutil.so.1',
                ])
        elif solaris_version == '11':
            # Specific deps to add for Solaris 11.
            allowed_deps.extend([
                'libcrypt.so.1',
                'libcrypto.so.1.0.0',
                'libcryptoutil.so.1',
                'libelf.so.1',
                'libncurses.so.5',
                'libsoftcrypto.so.1',
                'libsqlite3.so.0',
                'libssl.so.1.0.0',
                ])
    elif platform_system == 'darwin':
        # This is the list of deps for OS X 10.8, mostly sans versions.
        allowed_deps = [
            'ApplicationServices.framework/Versions/A/ApplicationServices',
            'Carbon.framework/Versions/A/Carbon',
            'CoreFoundation.framework/Versions/A/CoreFoundation',
            'CoreServices.framework/Versions/A/CoreServices',
            'SystemConfiguration.framework/Versions/A/SystemConfiguration',
            'libSystem.B.dylib',
            'libcrypto.0.9.8.dylib',
            'libssl.0.9.8.dylib',
            'libz.1.dylib',
            ]
    elif platform_system == 'openbsd':
        # This is the minimum list of deps for OpenBSD 5.8, sans versions.
        allowed_deps = [
            '/usr/lib/libc.so',
            '/usr/lib/libcrypto.so',
            '/usr/lib/libm.so',
            '/usr/lib/libpthread.so',
            '/usr/lib/libssl.so',
            '/usr/lib/libutil.so',
            '/usr/lib/libz.so',
            '/usr/libexec/ld.so',
            ]
    return allowed_deps


def get_actual_deps(script_helper):
    """
    Return a list of unique dependencies for the newly-built binaries.
    script_helper is a shell script that uses ldd (or equivalents) to examine
    dependencies for all binaries in the current sub-directory.
    """
    try:
        raw_deps = subprocess.check_output(script_helper).splitlines()
    except:
        sys.stderr.write('Could not get the deps for the new binaries.\n')
    else:
        libs_deps = []
        for line in raw_deps:
            if line.startswith('./'):
                # In some OS'es (at least AIX and OS X), the output includes
                # the examined binaries and those lines start with "./". It's
                # safe to ignore them because they point to paths in the
                # current hierarchy of directories.
                continue
            if platform_system == 'openbsd':
                # OpenBSD's ldd output is very particular, the name of the
                # examined files are in the 6th colon. Which also includes a
                # colon name, of which we'll get rid in the following check.
                deps = line.split()[6]
                # It also outputs the examined binaries with full path, so we
                # use the fact that there are no libs outside /usr in OpenBSD.
                if not deps.startswith('/usr'):
                    continue
            else:
                # Usually, the first field in each line is the needed file name.
                deps = line.split()[0]
            libs_deps.append(deps)
    return list(set(libs_deps))


def get_unwanted_deps(allowed_deps, actual_deps):
    """
    Return unwanted deps for the newly-built binaries.
    allowed_deps is a list of strings representing the allowed dependencies
    for binaries built for the current OS, hardcoded in get_allowed_deps().
    May include the major versioning, eg. "libssl.so" or "libssl.so.1".
    actual_deps is a list of strings representing the actual dependencies
    for the newly-built binaries as gathered through get_actual_deps().
    May include the path, eg. "libssl.so.1" or "/usr/lib/libssl.so.1".
    """
    unwanted_deps = []
    for single_actual_dep in actual_deps:
        for single_allowed_dep in allowed_deps:
            if single_allowed_dep in single_actual_dep:
                break
        else:
            unwanted_deps.append(single_actual_dep)
    return unwanted_deps


def test_dependencies():
    """
    Compare the list of allowed deps for the current OS with the list of
    actual deps for the newly-built binaries returned by the script helper.

    Return 0 on success, non zero on error.
    """
    if os.name == 'nt':
        # Not supported on Windows.
        return 0

    allowed_deps = get_allowed_deps()
    if not allowed_deps:
        sys.stderr.write('Got no allowed deps. Please check if {0} is a '
            'supported operating system.\n'.format(platform.system()))
        return 13

    actual_deps = get_actual_deps(script_helper)
    if not actual_deps:
        sys.stderr.write('Got no deps for the new binaries. Please check '
            'the "{0}" script in the "build/" dir.\n'.format(script_helper))
        return 14

    unwanted_deps = get_unwanted_deps(allowed_deps, actual_deps)
    if unwanted_deps:
        sys.stderr.write('Got unwanted deps:\n')
        for single_dep_to_print in unwanted_deps:
            sys.stderr.write('\t{0}\n'.format(single_dep_to_print))
        return 15

    return 0

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

    if os.name != 'nt':
        # Module only available on Linux / Unix
        try:
            import crypt
            crypt
        except:
            sys.stderr.write('"crypt" missing.\n')
            exit_code = 5

        try:
            import setproctitle
            setproctitle
        except:
            sys.stderr.write('"setproctitle" missing.\n')
            exit_code = 7

        try:
            from Crypto.PublicKey import _fastmath
            _fastmath
        except:
            sys.stderr.write('"Crypto.PublicKey._fastmath" missing. No GMP?\n')
            exit_code = 10

    try:
        import sqlite3
        sqlite3
    except:
        sys.stderr.write('"sqlite3" missing.\n')
        exit_code = 6

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

    # Windows specific modules.
    if os.name == 'nt':
        try:
            from ctypes import windll
            windll
        except:
            sys.stderr.write('"ctypes - windll" missing.\n')
            exit_code = 1
        try:
            import sqlite3
            sqlite3
        except:
            sys.stderr.write('"sqlite3" missing.\n')
            exit_code = 1

        # For now cryptography is only available on Winodws
        try:
            from cryptography.hazmat.backends.openssl.backend import backend
            openssl_version = backend.openssl_version_text()
        except:
            sys.stderr.write('"cryptography" failure.\n')
            exit_code = 3
        else:
            # Check OpenSSL version.
            assert openssl_version == '1.0.2d'

    else:
        # Linux and Unix checks.
        try:
            import setproctitle
            setproctitle
        except:
            sys.stderr.write('"setproctitle" missing.\n')
            exit_code = 1

        try:
            import crypt
            crypt
        except:
            sys.stderr.write('"crypt" missing.\n')
            exit_code = 1

        try:
            from Crypto.PublicKey import _fastmath
            _fastmath
        except:
            sys.stderr.write('Crypto.PublicKey._fastmath missing. No GMP?\n')
            exit_code = 1

    if ( platform_system == 'linux' ) or ( platform_system == 'sunos' ):
        try:
            import spwd
            spwd
        except:
            sys.stderr.write('"spwd" missing.\n')
            exit_code = 1

    # We compile the readline module using libedit only on selected platforms.
    if test_for_readline:
        try:
            import readline
            readline.get_history_length()
        except:
            sys.stderr.write('"readline" missing.\n')
            exit_code = 13

        exit_code = test_dependencies() | exit_code

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
