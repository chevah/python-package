# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
import os
import sys
import platform
import subprocess

script_helper = './get_binaries_deps.sh'
platform_system = platform.system().lower()
with open('../DEFAULT_VALUES') as default_values_file:
    [ chevah_os, chevah_arch ] = default_values_file.read().strip('\n').split(' ')[2:4]
BUILD_CFFI = os.environ.get('BUILD_CFFI', 'no').lower() == 'yes'
BUILD_LIBEDIT = os.environ.get('BUILD_LIBEDIT', 'no').lower() == 'yes'


def get_allowed_deps():
    """
    Return a hardcoded list of allowed deps for the current OS.
    """
    allowed_deps = []
    if platform_system == 'linux':
        # The minimal list of deps for Linux: glibc, openssl and zlib.
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
        if ('rhel' in chevah_os):
            allowed_deps.extend([
                'libcom_err.so.2',
                'libgssapi_krb5.so.2',
                'libk5crypto.so.3',
                'libkrb5.so.3',
                'libncursesw.so.5',
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
            sles_version = int(chevah_os[4:6])
            allowed_deps.extend([
                'libncursesw.so.5',
                ])
            if sles_version >= 12:
                allowed_deps.extend([
                    'libtinfo.so.5',
                    ])
        elif ('ubuntu' in chevah_os):
            allowed_deps.extend([
                'libtinfo.so.5',
                ])
            if 'arm64' in chevah_arch:
                allowed_deps.extend([
                    'libgcc_s.so.1',
                    ])
        elif ('raspbian' in chevah_os):
            raspbian_version = int(chevah_os[8:])
            allowed_deps.extend([
                'libgcc_s.so.1',
                'libncurses.so.5',
                'libtinfo.so.5',
                ])
            if raspbian_version == 7:
                allowed_deps.extend([
                    '/usr/lib/arm-linux-gnueabihf/libcofi_rpi.so',
                    ])
            elif raspbian_version >= 8:
                allowed_deps.extend([
                    '/usr/lib/arm-linux-gnueabihf/libarmmem.so',
                    ])
        elif ('alpine' in chevah_os):
            # This is a peculiar distro, so we start the list from scratch.
            # Full deps with paths, but no minor versions, for Alpine 3.6.
            allowed_deps=([
                '/lib/ld-musl-x86_64.so.1',
                '/lib/libc.musl-x86_64.so.1',
                '/lib/libcrypto.so.41',
                '/lib/libssl.so.43',
                '/lib/libz.so.1',
                '/usr/lib/libncursesw.so.6',
                ])
        else:
            # Debian 7 x64 (aka linux-x64) needs this for cffi.
            allowed_deps.extend([
                'libgcc_s.so.1',
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
        # On Solaris, platform.release() can be: '5.9'. '5.10', '5.11' etc.
        solaris_version = platform.release().split('.')[1]
        if '64' in chevah_arch:
            # This is the common list of deps for Solaris 10 & 11 64bit builds.
            allowed_deps = [
                '/lib/64/libc.so.1',
                '/lib/64/libdl.so.1',
                '/lib/64/libintl.so.1',
                '/lib/64/libm.so.2',
                '/lib/64/libnsl.so.1',
                '/lib/64/libsocket.so.1',
                ]
            if solaris_version == '10':
                # Specific deps to add for Solaris 10.
                allowed_deps.extend([
                    '/lib/64/libaio.so.1',
                    '/lib/64/libgen.so.1',
                    '/lib/64/libmd.so.1',
                    '/lib/64/librt.so.1',
                    '/lib/64/libthread.so.1',
                    '/usr/lib/64/libcrypt_i.so.1',
                    '/usr/lib/64/libz.so.1',
                    '/usr/lib/mps/64/libsqlite3.so',
                    '/usr/sfw/lib/64/libcrypto.so.0.9.7',
                    '/usr/sfw/lib/64/libssl.so.0.9.7',
                    ])
            elif solaris_version == '11':
                # Specific deps to add for Solaris 11.
                allowed_deps.extend([
                    '/lib/64/libcrypto.so.1.0.0',
                    '/lib/64/libssl.so.1.0.0',
                    '/lib/64/libz.so.1',
                    '/usr/lib/64/libcrypt.so.1',
                    '/usr/lib/64/libsqlite3.so.0',
                    ])
                if 'sparc' in chevah_arch:
                    allowed_deps.extend([
                        '/usr/lib/sparcv9/libc.so.1',
                        ])
                else:
                    allowed_deps.extend([
                        '/lib/64/libelf.so.1',
                        '/usr/lib/amd64/libc.so.1',
                        ])
        else:
            # This is the common list of deps for Solaris 10 & 11 32bit builds.
            allowed_deps = [
                '/lib/libc.so.1',
                '/lib/libdl.so.1',
                '/lib/libintl.so.1',
                '/lib/libm.so.2',
                '/lib/libnsl.so.1',
                '/lib/libsocket.so.1',
                ]
            if solaris_version == '10':
                # Specific deps to add for all Solaris 10 versions.
                allowed_deps.extend([
                    '/lib/libaio.so.1',
                    '/lib/libgen.so.1',
                    '/lib/librt.so.1',
                    '/usr/lib/libcrypt_i.so.1',
                    '/usr/sfw/lib//libcrypto.so.0.9.7',
                    '/usr/sfw/lib//libssl.so.0.9.7',
                    ])
                if 'solaris10u3' in chevah_os:
                    # Specific deps for Solaris 10u3 up to 10u7.
                    allowed_deps.extend([
                        '/lib/libmd5.so.1',
                        '/lib/libresolv.so.2',
                        '/usr/lib/mps/libsqlite3.so.0',
                        '/usr/sfw/lib//libgcc_s.so.1',
                        ])
                else:
                    # Specific deps for Solaris 10u8 and newer.
                    allowed_deps.extend([
                        '/lib/libmd.so.1',
                        '/usr/lib/libz.so.1',
                        '/usr/lib/mps/libsqlite3.so',
                        '/lib/libthread.so.1',
                        ])
            elif solaris_version == '11':
                # Specific deps to add for Solaris 11.
                allowed_deps.extend([
                    '/lib/libcrypto.so.1.0.0',
                    '/lib/libssl.so.1.0.0',
                    '/lib/libz.so.1',
                    '/usr/lib/libcrypt.so.1',
                    '/usr/lib/libsqlite3.so.0',
                    ])
    elif platform_system == 'hp-ux':
        # Specific deps for HP-UX 11.31, with full path.
        allowed_deps = [
            '/usr/lib/hpux32/libc.so.1',
            '/usr/lib/hpux32/libcrypto.so.1.0.0',
            '/usr/lib/hpux32/libdl.so.1',
            '/usr/lib/hpux32/libm.so.1',
            '/usr/lib/hpux32/libnsl.so.1',
            '/usr/lib/hpux32/libpthread.so.1',
            '/usr/lib/hpux32/librt.so.1',
            '/usr/lib/hpux32/libssl.so.1.0.0',
            '/usr/lib/hpux32/libxnet.so.1',
            '/usr/lib/hpux32/libxti.so.1',
            ]
    elif platform_system == 'darwin':
        # Common deps for OS X 10.8 and macOS 10.12, with full path.
        allowed_deps = [
            '/System/Library/Frameworks/ApplicationServices.framework/Versions/A/ApplicationServices',
            '/System/Library/Frameworks/Carbon.framework/Versions/A/Carbon',
            '/System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation',
            '/System/Library/Frameworks/CoreServices.framework/Versions/A/CoreServices',
            '/System/Library/Frameworks/Security.framework/Versions/A/Security',
            '/System/Library/Frameworks/SystemConfiguration.framework/Versions/A/SystemConfiguration',
            '/usr/lib/libSystem.B.dylib',
            '/usr/lib/libz.1.dylib',
            ]
        if ('osx' in chevah_os):
            # Additional deps when using the OS-included OpenSSL.
            allowed_deps.extend([
                '/usr/lib/libcrypto.0.9.8.dylib',
                '/usr/lib/libssl.0.9.8.dylib',
                '/usr/lib/libncurses.5.4.dylib',
                ])
        elif ('macos' in chevah_os):
            # Additional deps when using Homebrew's OpenSSL.
            allowed_deps.extend([
                '/usr/lib/libgcc_s.1.dylib',
                '/usr/local/opt/openssl/lib/libcrypto.1.0.0.dylib',
                '/usr/local/opt/openssl/lib/libssl.1.0.0.dylib',
                ])
    elif platform_system == 'freebsd':
        # This is the common list of deps for FreeBSD 10 and newer, with paths.
        allowed_deps = [
            '/lib/libc.so.7',
            '/lib/libcrypt.so.5',
            '/lib/libm.so.5',
            '/lib/libthr.so.3',
            '/lib/libutil.so.9',
            '/lib/libz.so.6',
            ]
        # On FreeBSD this can be: '10.3-RELEASE-p20', '11.0-RELEASE', etc.
        freebsd_version = platform.release().split('.')[0]
        if freebsd_version == '10':
            # Additional deps, specific for FreeBSD 10.
            allowed_deps.extend([
                '/lib/libcrypto.so.7',
                '/usr/lib/libssl.so.7',
            ])
        else:
            # Additional deps, specific for FreeBSD 11 and maybe newer.
            allowed_deps.extend([
                '/lib/libcrypto.so.8',
                '/usr/lib/libssl.so.8',
            ])
    elif platform_system == 'openbsd':
        # This is the list of deps for OpenBSD 5.8 or newer, sans versions.
        allowed_deps = [
            '/usr/lib/libc.so',
            '/usr/lib/libcrypto.so',
            '/usr/lib/libm.so',
            '/usr/lib/libncursesw.so.14.0',
            '/usr/lib/libpthread.so',
            '/usr/lib/libssl.so',
            '/usr/lib/libutil.so',
            '/usr/lib/libz.so',
            '/usr/libexec/ld.so',
            ]
    elif platform_system == 'netbsd':
        # This is the list of specific deps for NetBSD 7.x, with paths.
        allowed_deps = [
            '/lib/libcrypt.so.1',
            '/usr/lib/libc.so.12',
            '/usr/lib/libcrypt.so.1',
            '/usr/lib/libcrypto.so.8',
            '/usr/lib/libcurses.so.7',
            '/usr/lib/libgcc_s.so.1',
            '/usr/lib/libintl.so.1',
            '/usr/lib/libm.so.0',
            '/usr/lib/libpthread.so.1',
            '/usr/lib/libssl.so.10',
            '/usr/lib/libterminfo.so.1',
            '/usr/lib/libutil.so.7',
            '/usr/lib/libz.so.1',
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
            if line.startswith('./') or not line:
                # In some OS'es (AIX, HP-UX, OS X, BSDs), the output includes
                # the examined binaries, and those lines start with "./".
                # It's safe to ignore them because they point to paths in
                # the current hierarchy of directories.
                # In HP-UX, ldd also outputs an empty first line.
                continue
            if platform_system in [ 'sunos', 'hp-ux', 'freebsd', 'netbsd' ]:
                # When ignoring lines from the above conditions, ldd's output
                # lists the libs with full path in the 3th colon on these OS'es.
                dep = line.split()[2]
            elif platform_system == 'openbsd':
                # OpenBSD's ldd output is very particular, both the name of the
                # examined files and the needed libs are in the 7th colon, which
                # also includes a colon name, of which we'll get rid below.
                dep = line.split()[6]
                strings_to_ignore = ( 'Name', os.getcwd(), './', )
                if dep.startswith(strings_to_ignore):
                    continue
            else:
                # Usually, the first field in each line is the needed file name.
                dep = line.split()[0]
            libs_deps.append(dep)
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
        return 113

    actual_deps = get_actual_deps(script_helper)
    if not actual_deps:
        sys.stderr.write('Got no deps for the new binaries. Please check '
            'the "{0}" script in the "build/" dir.\n'.format(script_helper))
        return 114

    unwanted_deps = get_unwanted_deps(allowed_deps, actual_deps)
    if unwanted_deps:
        sys.stderr.write('Got unwanted deps:\n')
        for single_dep_to_print in unwanted_deps:
            sys.stderr.write('\t{0}\n'.format(single_dep_to_print))
        return 115

    return 0


def egg_check(module):
    """
    Check that the tested module is in the current path.
    If not, it may be pulled from ~/.python-eggs and we don't want that.

    Return 0 on success, non zero on error.
    """
    if not os.getcwd() in module.__file__:
        sys.stderr.write(
            "{0} module not in current path, ".format(module.__name__) +
                "is zip_safe set to True for it?\n"
            "\tcurrent path: {0}".format(os.getcwd()) + "\n"
            "\tmodule file: {0}".format(module.__file__) + "\n"
            )
        return 116

    return 0


def main():
    """
    Launch tests to check required modules and OS-specific dependencies.
    Exit with a relevant error code.
    """
    exit_code = 0
    import sys
    print 'python %s' % (sys.version,)

    try:
        import zlib
        print 'zlib %s' % (zlib.__version__,)
    except:
        sys.stderr.write('"zlib" missing.\n')
        exit_code = 1

    try:
        import ssl
        print 'stdlib ssl %s' % (ssl.OPENSSL_VERSION,)
        import _hashlib
        exit_code = egg_check(_hashlib) | exit_code
    except:
        sys.stderr.write('standard "ssl" missing.\n')
        exit_code = 2

    # cryptography module and latest pyOpenSSL are only available on
    # systems with cffi.
    if BUILD_CFFI:
        try:
            from cryptography.hazmat.backends.openssl.backend import backend
            import cryptography
            openssl_version = backend.openssl_version_text()
            print 'cryptography %s - OpenSSL %s' % (
                cryptography.__version__, openssl_version)

            if chevah_os == 'windows':
                # Check OpenSSL version on windows.
                expecting = u'OpenSSL 1.1.0f  25 May 2017'
                if openssl_version != expecting:
                    sys.stderr.write('Expecting %s got %s.\n' % (
                        expecting, openssl_version))
                    exit_code = 13
        except Exception as error:
            sys.stderr.write('"cryptography" failure. %s\n' % (error,))
            exit_code = 14

    try:
        from OpenSSL import SSL, crypto, rand, __version__ as pyopenssl_version
        crypto
        rand
        print 'pyopenssl %s - OpenSSL %s' % (
            pyopenssl_version,
            SSL.SSLeay_version(SSL.SSLEAY_VERSION),
            )
    except Exception as error:
        sys.stderr.write('"OpenSSL" missing. %s\n' % (error,))
        exit_code = 3

    try:
        import Crypto
        print 'PyCrypto %s' % (Crypto.__version__,)
    except:
        sys.stderr.write('"PyCrypto" missing.\n')
        exit_code = 4

    try:
        from ctypes import CDLL
        import ctypes
        CDLL
        print 'ctypes %s' % (ctypes.__version__,)
    except:
        sys.stderr.write('"ctypes - CDLL" missing. %s\n')
        exit_code = 8

    try:
        from ctypes.util import find_library
        find_library
    except:
        sys.stderr.write('"ctypes.utils - find_library" missing.\n')
        exit_code = 9

    try:
        import multiprocessing
        multiprocessing.current_process()
    except:
        sys.stderr.write('"multiprocessing" missing.\n')
        exit_code = 16

    # The pure-Python scandir package is always available.
    try:
        import scandir
    except:
        sys.stderr.write('"scandir" missing.\n')
        exit_code = 17

    # Windows specific modules.
    if os.name == 'nt':
        try:
            from ctypes import windll
            windll
        except:
            sys.stderr.write('"ctypes - windll" missing.\n')
            exit_code = 15
        try:
            import sqlite3
            sqlite3
        except:
            sys.stderr.write('"sqlite3" missing.\n')
            exit_code = 6

    else:
        # Linux / Unix stuff.
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
            print 'setproctitle %s' % (setproctitle.__version__,)
        except:
            sys.stderr.write('"setproctitle" missing.\n')
            exit_code = 7

        try:
            from Crypto.PublicKey import _fastmath
            exit_code = egg_check(_fastmath) | exit_code
        except:
            sys.stderr.write('Crypto.PublicKey._fastmath missing. No GMP?\n')
            exit_code = 10

        # Check for the git revision in Python's sys.version on Linux and Unix.
        try:
            git_rev_cmd = ['git', 'rev-parse', '--short', 'HEAD']
            git_rev = subprocess.check_output(git_rev_cmd).strip()
        except:
            sys.stderr.write("Couldn't get the git rev for the current tree.\n")
            exit_code = 117
        else:
            bin_ver = sys.version.split('(')[1].split(',')[0]
            if bin_ver != git_rev:
                sys.stderr.write("Python version doesn't match git revision!\n"
                                 "\tBin ver: {0}".format(bin_ver) + "\n"
                                 "\tGit rev: {0}".format(git_rev) + "\n")
                exit_code = 118

        try:
            import _scandir
            exit_code = egg_check(_scandir) | exit_code
        except:
            sys.stderr.write('"_scandir" missing.\n')
            exit_code = 18


    if ( platform_system == 'linux' ) or ( platform_system == 'sunos' ):
        try:
            import spwd
            spwd
        except:
            sys.stderr.write('"spwd" missing.\n')
            exit_code = 11


    # We compile the readline module using libedit only on selected platforms.
    if BUILD_LIBEDIT:
        try:
            import readline
            readline.get_history_length()
        except:
            sys.stderr.write('"readline" missing.\n')
            exit_code = 12
        else:
            print '"readline" module is present.'


    exit_code = test_dependencies() | exit_code


    sys.exit(exit_code)


if __name__ == '__main__':
    main()
