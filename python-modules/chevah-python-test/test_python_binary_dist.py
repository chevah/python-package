# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
import os
import sys
import platform
import subprocess

script_helper = './get_binaries_deps.sh'
platform_system = platform.system().lower()

try:
    CHEVAH_OS = os.environ.get('OS')
    CHEVAH_ARCH = os.environ.get('ARCH')
except:
    print 'Coult not get $OS/$ARCH Chevah env vars.'
    sys.exit(101)

BUILD_CFFI = os.environ.get('BUILD_CFFI', 'no').lower() == 'yes'
BUILD_LIBEDIT = os.environ.get('BUILD_LIBEDIT', 'no').lower() == 'yes'


def get_allowed_deps():
    """
    Return a hardcoded list of allowed deps for the current OS.
    """
    allowed_deps = []
    if platform_system == 'linux':
        if 'lnx' in CHEVAH_OS:
            # Deps without paths for generic Linux builds.
            # Only glibc 2.x libs are allowed.
            # Tested on SLES 11 with glibc 2.11.3.
            allowed_deps=[
                'libc.so.6',
                'libcrypt.so.1',
                'libdl.so.2',
                'libm.so.6',
                'libpthread.so.0',
                'libutil.so.1',
                ]
            if 'arm64' in CHEVAH_ARCH:
                # Additional deps without paths for arm64 generic Linux builds.
                # From Ubuntu 16.04 w/ glibc 2.23 (on Pine A64+ and X-Gene 3).
                allowed_deps.extend([
                    'libgcc_s.so.1',
                    ])
        elif 'rhel' in CHEVAH_OS:
            # Common deps for supported RHEL with full paths (x86_64 only).
            allowed_deps = [
                '/lib64/libcom_err.so.2',
                '/lib64/libcrypt.so.1',
                '/lib64/libc.so.6',
                '/lib64/libdl.so.2',
                '/lib64/libfreebl3.so',
                '/lib64/libgssapi_krb5.so.2',
                '/lib64/libk5crypto.so.3',
                '/lib64/libkeyutils.so.1',
                '/lib64/libkrb5.so.3',
                '/lib64/libkrb5support.so.0',
                '/lib64/libm.so.6',
                '/lib64/libnsl.so.1',
                '/lib64/libpthread.so.0',
                '/lib64/libresolv.so.2',
                '/lib64/libselinux.so.1',
                '/lib64/libutil.so.1',
                '/lib64/libz.so.1',
                ]
            rhel_version = CHEVAH_OS[4:]
            if rhel_version.startswith("7"):
                allowed_deps.extend([
                    '/lib64/libcrypto.so.10',
                    '/lib64/libffi.so.6',
                    '/lib64/libncursesw.so.5',
                    '/lib64/libpcre.so.1',
                    '/lib64/libssl.so.10',
                    '/lib64/libtinfo.so.5',
                    ])
            if rhel_version.startswith("8"):
                allowed_deps.extend([
                    '/lib64/libcrypto.so.1.1',
                    '/lib64/libffi.so.6',
                    '/lib64/libncursesw.so.6',
                    '/lib64/libssl.so.1.1',
                    '/lib64/libtinfo.so.6',
                    ])
        elif 'amzn' in CHEVAH_OS:
            # Deps for Amazon Linux 2 (x86_64 only).
            allowed_deps=[
                '/lib64/libcom_err.so.2',
                '/lib64/libcrypto.so.10',
                '/lib64/libcrypt.so.1',
                '/lib64/libc.so.6',
                '/lib64/libdl.so.2',
                '/lib64/libffi.so.6',
                '/lib64/libgssapi_krb5.so.2',
                '/lib64/libk5crypto.so.3',
                '/lib64/libkeyutils.so.1',
                '/lib64/libkrb5.so.3',
                '/lib64/libkrb5support.so.0',
                '/lib64/libm.so.6',
                '/lib64/libncursesw.so.6',
                '/lib64/libpcre.so.1',
                '/lib64/libpthread.so.0',
                '/lib64/libresolv.so.2',
                '/lib64/libselinux.so.1',
                '/lib64/libssl.so.10',
                '/lib64/libtinfo.so.6',
                '/lib64/libutil.so.1',
                '/lib64/libz.so.1',
                ]
        elif 'ubuntu' in CHEVAH_OS:
            ubuntu_version = CHEVAH_OS[6:]
            # Common deps for supported Ubuntu LTS with full paths (x86_64).
            allowed_deps=[
                '/lib/x86_64-linux-gnu/libc.so.6',
                '/lib/x86_64-linux-gnu/libcrypt.so.1',
                '/lib/x86_64-linux-gnu/libdl.so.2',
                '/lib/x86_64-linux-gnu/libm.so.6',
                '/lib/x86_64-linux-gnu/libnsl.so.1',
                '/lib/x86_64-linux-gnu/libpthread.so.0',
                '/lib/x86_64-linux-gnu/libutil.so.1',
                '/lib/x86_64-linux-gnu/libz.so.1',
                ]
            if ubuntu_version == "1604":
                allowed_deps.extend([
                    '/lib/x86_64-linux-gnu/libcrypto.so.1.0.0',
                    '/lib/x86_64-linux-gnu/libssl.so.1.0.0',
                    '/lib/x86_64-linux-gnu/libtinfo.so.5',
                    '/usr/lib/x86_64-linux-gnu/libffi.so.6',
                ])
            elif ubuntu_version == "1804":
                allowed_deps.extend([
                    '/lib/x86_64-linux-gnu/libtinfo.so.5',
                    '/usr/lib/x86_64-linux-gnu/libcrypto.so.1.1',
                    '/usr/lib/x86_64-linux-gnu/libssl.so.1.1',
                    '/usr/lib/x86_64-linux-gnu/libffi.so.6',
                ])
            else:
                # Tested on 20.04, might cover future releases as well.
                allowed_deps.extend([
                    '/lib/x86_64-linux-gnu/libcrypto.so.1.1',
                    '/lib/x86_64-linux-gnu/libssl.so.1.1',
                    '/lib/x86_64-linux-gnu/libtinfo.so.6',
                    '/lib/x86_64-linux-gnu/libffi.so.7',
                ])
            if 'arm64' in CHEVAH_ARCH:
                # Deps with full paths for Ubuntu 16.04 on a Pine64 board.
                allowed_deps=[
                    '/lib/aarch64-linux-gnu/libc.so.6',
                    '/lib/aarch64-linux-gnu/libcrypt.so.1',
                    '/lib/aarch64-linux-gnu/libcrypto.so.1.0.0',
                    '/lib/aarch64-linux-gnu/libdl.so.2',
                    '/lib/aarch64-linux-gnu/libgcc_s.so.1',
                    '/lib/aarch64-linux-gnu/libm.so.6',
                    '/lib/aarch64-linux-gnu/libnsl.so.1',
                    '/lib/aarch64-linux-gnu/libpthread.so.0',
                    '/lib/aarch64-linux-gnu/libssl.so.1.0.0',
                    '/lib/aarch64-linux-gnu/libtinfo.so.5',
                    '/lib/aarch64-linux-gnu/libutil.so.1',
                    '/lib/aarch64-linux-gnu/libz.so.1',
                    '/usr/lib/aarch64-linux-gnu/libffi.so.6',
                    ]
        elif 'alpine' in CHEVAH_OS:
            # Full deps with paths, but no minor versions, for Alpine 3.6+.
            alpine_version = CHEVAH_OS[6:]
            allowed_deps=[
                '/lib/ld-musl-x86_64.so.1',
                '/lib/libc.musl-x86_64.so.1',
                '/lib/libz.so.1',
                '/usr/lib/libncursesw.so.6',
                ]
            if alpine_version in [ "36", "37", "38" ]:
                # These versions use LibreSSL by default.
                allowed_deps.extend([
                    '/lib/libcrypto.so.42',
                    '/lib/libssl.so.44',
                    '/usr/lib/libffi.so.6',
                    ])
            elif alpine_version in [ "39", "310", "311" ]:
                # Alpine Linux 3.9 reverted to OpenSSL by default.
                allowed_deps.extend([
                    '/lib/libcrypto.so.1',
                    '/lib/libssl.so.1',
                    '/usr/lib/libffi.so.6',
                    ])
            else:
                # Alpine Linux 3.12+ has FFI 3.3.
                allowed_deps.extend([
                    '/lib/libcrypto.so.1',
                    '/lib/libssl.so.1',
                    '/usr/lib/libffi.so.7',
                    ])
    elif platform_system == 'aix':
        # Deps for AIX 7.1, many added with psutil.
        allowed_deps = [
            '/lib/libbsd.a(shr.o)',
            '/lib/libc.a(pse.o)',
            '/lib/libc.a(shr.o)',
            '/lib/libcrypt.a(shr.o)',
            '/lib/libdl.a(shr.o)',
            '/lib/libnsl.a(shr.o)',
            '/lib/libpthreads.a(shr.o)',
            '/lib/libpthreads.a(shr_comm.o)',
            '/lib/libpthreads.a(shr_xpg5.o)',
            '/lib/libpthreads_compat.a(shr.o)',
            '/lib/libthread.a(shr.o)',
            '/lib/libtli.a(shr.o)',
            '/usr/lib/libc.a(shr.o)',
            '/usr/lib/libcfg.a(shr.o)',
            '/usr/lib/libcorcfg.a(shr.o)',
            '/usr/lib/libcrypt.a(shr.o)',
            '/usr/lib/libdl.a(shr.o)',
            '/usr/lib/liblvm.a(shr.o)',
            '/usr/lib/libodm.a(shr.o)',
            '/usr/lib/libperfstat.a(shr.o)',
            '/usr/lib/libpthread.a(shr_xpg5.o)',
            '/usr/lib/libpthreads.a(shr_comm.o)',
            '/usr/lib/libpthreads.a(shr_xpg5.o)',
            '/usr/lib/libsrc.a(shr.o)',
            '/unix',
            ]
    elif platform_system == 'sunos':
        # On Solaris, platform.release() can be: '5.9'. '5.10', '5.11' etc.
        solaris_version = platform.release().split('.')[1]
        # This is the list of deps for Solaris 11.4 64bit builds.
        allowed_deps = [
            '/lib/64/libc.so.1',
            '/lib/64/libcrypto.so.1.0.0',
            '/lib/64/libdl.so.1',
            '/lib/64/libm.so.2',
            '/lib/64/libnsl.so.1',
            '/lib/64/libsocket.so.1',
            '/lib/64/libssl.so.1.0.0',
            '/lib/64/libz.so.1',
            '/usr/lib/64/libbz2.so.1',
            '/usr/lib/64/libcrypt.so.1',
            '/usr/lib/64/libkstat.so.1',
            '/usr/lib/64/libncursesw.so.5',
            '/usr/lib/64/libpthread.so.1',
            '/usr/lib/64/libsqlite3.so.0',
            ]
        if 'sparc' in CHEVAH_ARCH:
            # True for 11.2, hopefully for 11.4 as well.
            allowed_deps.extend([
                '/usr/lib/sparcv9/libc.so.1',
                ])
        else:
            allowed_deps.extend([
                '/lib/64/libelf.so.1',
                '/usr/lib/amd64/libc.so.1',
                ])
    elif platform_system == 'darwin':
        # Deps for macOS 10.13, with full path.
        allowed_deps = [
            '/System/Library/Frameworks/ApplicationServices.framework/Versions/A/ApplicationServices',
            '/System/Library/Frameworks/Carbon.framework/Versions/A/Carbon',
            '/System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation',
            '/System/Library/Frameworks/CoreGraphics.framework/Versions/A/CoreGraphics',
            '/System/Library/Frameworks/CoreServices.framework/Versions/A/CoreServices',
            '/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit',
            '/System/Library/Frameworks/Security.framework/Versions/A/Security',
            '/System/Library/Frameworks/SystemConfiguration.framework/Versions/A/SystemConfiguration',
            '/usr/lib/libbz2.1.0.dylib',
            '/usr/lib/libffi.dylib',
            '/usr/lib/libncurses.5.4.dylib',
            '/usr/lib/libSystem.B.dylib',
            '/usr/lib/libz.1.dylib',
            ]
    elif platform_system == 'freebsd':
        # This is the common list of deps for FreeBSD 10 and newer, with paths.
        allowed_deps = [
            '/lib/libc.so.7',
            '/lib/libcrypt.so.5',
            '/lib/libdevstat.so.7',
            '/lib/libm.so.5',
            '/lib/libncurses.so.8',
            '/lib/libthr.so.3',
            '/lib/libutil.so.9',
            '/lib/libz.so.6',
            '/usr/lib/libbz2.so.4',
            ]
        # On FreeBSD this can be: '10.3-RELEASE-p20', '11.0-RELEASE', etc.
        freebsd_version = platform.release().split('.')[0]
        if freebsd_version == '10':
            # Additional deps, specific for FreeBSD 10.
            allowed_deps.extend([
                '/lib/libcrypto.so.7',
                '/lib/libkvm.so.6',
                '/usr/lib/libssl.so.7',
            ])
        elif freebsd_version == '11':
            # Additional deps, specific for FreeBSD 11.
            allowed_deps.extend([
                '/lib/libcrypto.so.8',
                '/lib/libelf.so.2',
                '/lib/libkvm.so.7',
                '/usr/lib/libdl.so.1',
                '/usr/lib/libssl.so.8',
            ])
        else:
            # Additional deps, specific for FreeBSD 12.
            allowed_deps.extend([
                '/lib/libcrypto.so.111',
                '/lib/libelf.so.2',
                '/lib/libkvm.so.7',
                '/usr/lib/libdl.so.1',
                '/usr/lib/libssl.so.111',
            ])
    elif platform_system == 'openbsd':
        # This is the list of deps for OpenBSD 5.8 or newer, sans versions.
        allowed_deps = [
            '/usr/lib/libc.so',
            '/usr/lib/libcrypto.so',
            '/usr/lib/libcurses.so',
            '/usr/lib/libkvm.so',
            '/usr/lib/libm.so',
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
    # OpenBSD's ldd output is special, both the name of the examined files and
    # the needed libs are in the 7th colon, which also includes a colon header.
    openbsd_ignored_strings = ( 'Name', os.getcwd(), './', )
    # On Linux with glibc we ignore ld-linux*, virtual deps and other special
    # libs and messages, to only get deps of regular libs with full paths.
    linux_ignored_strings = (
                            'linux-gate.so',
                            'linux-vdso.so',
                            'ld-linux.so',
                            'ld-linux-x86-64.so',
                            'ld-linux-aarch64.so',
                            'ld-linux-armhf.so',
                            'arm-linux-gnueabihf/libcofi_rpi.so',
                            'arm-linux-gnueabihf/libarmmem.so',
                            'statically linked',
                            )

    try:
        raw_deps = subprocess.check_output(script_helper).splitlines()
    except:
        sys.stderr.write('Could not get the deps for the new binaries.\n')
    else:
        libs_deps = []
        for line in raw_deps:
            if line.startswith('./') or not line:
                # In some OS'es (AIX, macOS, etc.), the output includes
                # the examined binaries, and those lines start with "./".
                # It's safe to ignore them because they point to paths in
                # the current hierarchy of directories.
                continue
            if platform_system in [ 'aix', 'darwin' ]:
                # When ignoring lines from the above conditions, ldd's output
                # lists the libs with full path in the 1st colon on these OS'es.
                dep = line.split()[0]
            elif platform_system == 'openbsd':
                dep = line.split()[6]
                if dep.startswith(openbsd_ignored_strings):
                    continue
            elif platform_system == 'linux':
                # On Alpine we don't use regular ldd, the output is different.
                if 'alpine' in CHEVAH_OS:
                    dep = line.split()[0]
                else:
                    if any(string in line for string in linux_ignored_strings):
                        continue
                    dep = line.split()[2]
            else:
                # For other OS'es, the third field in each line is what we need.
                dep = line.split()[2]
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
    except:
        sys.stderr.write('"zlib" missing.\n')
        exit_code = 1
    else:
        print 'zlib %s' % (zlib.__version__,)

    try:
        from ssl import OPENSSL_VERSION
        import _hashlib
        exit_code = egg_check(_hashlib) | exit_code
    except:
        sys.stderr.write('standard "ssl" missing.\n')
        exit_code = 2
    else:
        print 'stdlib ssl %s' % (OPENSSL_VERSION,)

    # cryptography module and latest pyOpenSSL are only available on
    # systems with cffi.
    if BUILD_CFFI:
        try:
            from cryptography.hazmat.backends.openssl.backend import backend
            import cryptography
            # Check OpenSSL version on OS'es with static OpenSSL libs.
            openssl_version = backend.openssl_version_text()
            if CHEVAH_OS.startswith(("win", "lnx", "macos", "aix")):
                # On some OS'es we build against our own OpenSSL.
                expecting = u'OpenSSL 1.1.1j  16 Feb 2021'
                if CHEVAH_OS.startswith("win"):
                    # On Windows we are stuck with latest upstream wheels.
                    expecting = u'OpenSSL 1.1.1i  8 Dec 2020'
                if CHEVAH_OS.startswith("aix"):
                    # On AIX we are stuck with a patched 1.0.2.
                    expecting = u'OpenSSL 1.0.2v-chevah2  22 Feb 2021'
                if openssl_version != expecting:
                    sys.stderr.write('Expecting %s, got %s.\n' % (
                        expecting, openssl_version))
                    exit_code = 13
        except Exception as error:
            sys.stderr.write('"cryptography" failure. %s\n' % (error,))
            exit_code = 14
        else:
            print 'cryptography %s - %s' % (
                cryptography.__version__, openssl_version)

    try:
        from OpenSSL import SSL, crypto, rand, __version__ as pyopenssl_version
        crypto
        rand
    except Exception as error:
        sys.stderr.write('"OpenSSL" missing. %s\n' % (error,))
        exit_code = 3
    else:
        print 'pyOpenSSL %s - %s' % (
            pyopenssl_version,
            SSL.SSLeay_version(SSL.SSLEAY_VERSION),
            )

    try:
        import Crypto
        pycrypto_version = Crypto.__version__
    except:
        sys.stderr.write('"PyCrypto" missing.\n')
        exit_code = 4
    else:
        print 'PyCrypto %s' % (pycrypto_version)

    try:
        import Cryptodome
        pycryptodome_version = Cryptodome.__version__
    except:
        sys.stderr.write('"PyCryptodome" missing.\n')
        exit_code = 11
    else:
        print 'PyCryptodome %s' % (pycryptodome_version)

    try:
        from ctypes import CDLL
        import ctypes
        CDLL
    except:
        sys.stderr.write('"ctypes - CDLL" missing. %s\n')
        exit_code = 8
    else:
        print 'ctypes %s' % (ctypes.__version__,)

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
        sys.stderr.write('"multiprocessing" missing or broken.\n')
        exit_code = 16

    # The pure-Python scandir package is always available.
    try:
        import scandir
        for item in scandir.scandir('/'):
            if item.is_dir():
                break
    except:
        sys.stderr.write('"scandir" missing or broken.\n')
        exit_code = 17

    try:
        import gmpy2
        print 'gmpy2 %s with:' % (gmpy2.version())
        print '\tMP (Multiple-precision library) - %s' % (gmpy2.mp_version())
        print '\tMPFR (Floating-point library) - %s' % (gmpy2.mpfr_version())
        print '\tMPC (Complex library) - %s' % (gmpy2.mpc_version())
        x=gmpy2.mpz(123456789123456789)
        if not x==gmpy2.from_binary(gmpy2.to_binary(x)):
            sys.stderr.write('"gmpy2" present, but broken!\n')
            exit_code = 20
    except:
        try:
            import gmpy
            print 'gmpy %s with:' % (gmpy.version())
            print '\tGMP library - %s' % (gmpy.gmp_version())
            x=gmpy.mpz(123456789123456789)
            if not x==gmpy.mpz(gmpy.binary(x), 256):
                sys.stderr.write('"gmpy" present, but broken!\n')
                exit_code = 21
        except:
            sys.stderr.write('"gmpy2" and "gmpy" missing.\n')
            exit_code = 19

    try:
        import Cython
    except:
        sys.stderr.write('"Cython" missing.\n')
        exit_code = 24
    else:
        print 'Cython %s' % (Cython.__version__,)

    try:
        import subprocess32 as subprocess
        dir_output = subprocess.check_output('ls')
    except:
        sys.stderr.write('"subprocess32" missing or broken.\n')
        exit_code = 25
    else:
        print '"subprocess32" module is present.'

    try:
        import bcrypt
        password = b"super secret password"
        # Hash the password with a randomly-generated salt.
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        # Check that an unhashed password matches hashed one.
        if bcrypt.checkpw(password, hashed):
            print 'bcrypt %s' % (bcrypt.__version__,)
        else:
            sys.stderr.write('"bcrypt" present, but broken.\n')
            exit_code = 27
    except:
        sys.stderr.write('"bcrypt" missing.\n')
        exit_code = 26

    try:
        import bz2
        test_string = b"just a random string to quickly test bz2"
        test_string_bzipped = bz2.compress(test_string)
        if bz2.decompress(test_string_bzipped) == test_string:
            print '"bz2" is present.'
        else:
            sys.stderr.write('"bzip" present, but broken.\n')
            exit_code = 29
    except:
        sys.stderr.write('"bz2" missing.\n')
        exit_code = 28

    # Windows specific modules.
    if os.name == 'nt':
        try:
            from ctypes import windll
            windll
        except:
            sys.stderr.write('"ctypes - windll" missing.\n')
            exit_code = 15

        try:
            from sqlite3 import dbapi2 as sqlite
        except:
            sys.stderr.write('"sqlite3" missing or broken.\n')
            exit_code = 6
        else:
            print 'sqlite3 %s - sqlite %s' % (
                    sqlite.version, sqlite.sqlite_version)

        try:
            import win32service
            win32service.EnumWindowStations()
        except:
            sys.stderr.write('"pywin32" missing or broken.\n')
            exit_code = 22

    else:
        # Linux / Unix stuff.
        try:
            import crypt
            crypt
        except:
            sys.stderr.write('"crypt" missing.\n')
            exit_code = 5

        try:
            from pysqlite2 import dbapi2 as sqlite
        except:
            sys.stderr.write('"pysqlite2" missing.\n')
            exit_code = 6
        else:
            print 'pysqlite2 %s - sqlite %s' % (
                    sqlite.version, sqlite.sqlite_version)

        try:
            import setproctitle
            current_process_title = setproctitle.getproctitle()
        except:
            sys.stderr.write('"setproctitle" missing or broken.\n')
            exit_code = 7
        else:
            print 'setproctitle %s' % (setproctitle.__version__,)

        # Check for the git revision in Python's sys.version on Linux and Unix.
        try:
            git_rev_cmd = ['git', 'rev-parse', '--short=8', 'HEAD']
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
            if len(bin_ver) != 8:
                sys.stderr.write("Bad length for binary version, expected 8!\n"
                                 "\tBin ver: {0}".format(bin_ver) + "\n")
                exit_code = 119

        try:
            import _scandir
            exit_code = egg_check(_scandir) | exit_code
        except:
            sys.stderr.write('"_scandir" missing.\n')
            exit_code = 18

    try:
        import psutil
        cpu_percent = psutil.cpu_percent()
    except:
        sys.stderr.write('"psutil" missing or broken.\n')
        exit_code = 23
    else:
        print 'psutil %s' % (psutil.__version__,)

    if platform_system in [ 'linux', 'sunos' ]:
        try:
            import spwd
            spwd
        except:
            sys.stderr.write('"spwd" missing, but it should be present.\n')
            exit_code = 11
        else:
            print '"spwd" module is present.'

    # We compile the readline module using libedit only on selected platforms.
    if BUILD_LIBEDIT:
        try:
            import readline
            readline.get_history_length()
        except:
            sys.stderr.write('"readline" missing or broken.\n')
            exit_code = 12
        else:
            print '"readline" module is present.'


    exit_code = test_dependencies() | exit_code


    sys.exit(exit_code)


if __name__ == '__main__':
    main()
