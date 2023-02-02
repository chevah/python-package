#!/usr/bin/env bash
#
# Shared code for all binary-dist scripts.
#

# Bash checks (chevahbs scripts source them from here)
set -o nounset    # always check if variables exist
set -o errexit    # always exit on error
set -o errtrace   # trap errors in functions as well
set -o pipefail   # don't ignore exit codes when piping output

# Define global variables
COMMAND=""
OS=""
INSTALL_FOLDER=""

# Check if debugging environment variable is set and initialize with 0 if not.
DEBUG=${DEBUG-0}


help_text_help=\
"Show help for a command."
command_help() {
    if [ -n "${1-}" ]; then
        local command=$1
    else
        local command=""
    fi
    local help_command="help_$command"
    # Test to see if we have a valid help method,
    # otherwise call the general help.
    set +o errexit
    type $help_command &> /dev/null
    if [ $? -eq 0 ]; then
        $help_command
    else
        echo "Available commands are:"
        for help_text in `compgen -A variable help_text_`
        do
            command_name=${help_text#help_text_}
            echo -e "$command_name\t\t${!help_text}"
        done
    fi
    set -o errexit
}

#
# Main command selection.
#
# Select fuctions which are made public.
#
select_command() {
    if [ -n "${1-}" ]; then
        local command=$1
        shift
    else
        local command=""
    fi
    case $command in
        "")
            command_help
            exit 1
            ;;
        *)
            # Test to see if we have a valid command, otherwise call
            # the general help.
            call_command="command_$command"
            set +o errexit
            type $call_command &> /dev/null
            if [ $? -eq 0 ]; then
                $call_command $@
            else
                command_help
                echo ""
                echo "Unknown command: ${command}."
                exit 1
            fi
            set -o errexit
        ;;
    esac
}


#
# Chevah Build Script command selection.
#
select_chevahbs_command() {
    if [ $DEBUG -ne 0 ]; then
        echo "select_chevahbs_command:" $@
    fi
    COMMAND=$1
    OS=$2
    INSTALL_FOLDER=$3
    # Shift the standard arguments, and the rest will be passed to all
    # commands.
    shift 3

    chevahbs_command="chevahbs_$COMMAND"
    type $chevahbs_command &> /dev/null
    if [ $? -eq 0 ]; then
        $chevahbs_command $@
    else
        echo "Don't know what to do with command: ${COMMAND}."
        exit 1
    fi
}


#
# Internal function for calling build script on each source.
#
chevahbs_build() {
    if [ -n "$(type -t chevahbs_patch)" ]; then
        # Looks like the chevahbs script has patches to apply.
        echo "Patching..."
        chevahbs_patch $@
    fi
    echo "Configuring..."
    chevahbs_configure $@
    echo "Compiling..."
    chevahbs_compile $@
    echo "Installing..."
    chevahbs_install $@
}


exit_on_error() {
    exit_code=$1
    if [ $exit_code -ne 0 ]; then
        exit 1
    fi
}


execute() {
    if [ $DEBUG -ne 0 ]; then
        echo "Executing:" $@
    fi

    #Make sure $@ is called in quotes as otherwise it will not work.
    "$@"
    exit_code=$?
    if [ $DEBUG -ne 0 ]; then
        echo "Exit code was: $exit_code"
    fi
    if [ $exit_code -ne 0 ]; then
        echo "PWD :" `pwd`
        echo "Fail:" $@
        exit 1
    fi
}


build() {
    project_folder=$1
    version_folder=$2
    target_folder=$3

    if [ "$project_folder" = "." ]; then
        project_folder=${version_folder}
        source_folder="src/${version_folder}"
    else
        source_folder="src/${project_folder}/${version_folder}"
    fi

    install_folder=$PWD/${BUILD_FOLDER}/${target_folder}
    execute mkdir -p ${install_folder}

    build_folder=${BUILD_FOLDER}/${version_folder}
    execute rm -rf ${build_folder}
    echo "Copying source code ${build_folder}..."
    execute cp -r ${source_folder} ${build_folder}
    execute cp src/${project_folder}/chevahbs ${build_folder}/
    if [ $(ls src/${project_folder}/*.patch 2>/dev/null | wc -l) -gt 0 ]; then
        echo "The following patches are to be copied:"
        ls -1 src/${project_folder}/*.patch
        execute cp src/${project_folder}/*.patch ${build_folder}/
    fi
    if [ $(ls src/${project_folder}/*.diff 2>/dev/null | wc -l) -gt 0 ]; then
        echo "The following hot fixes are to be copied:"
        ls -1 src/${project_folder}/*.diff
        execute cp src/${project_folder}/*.diff ${build_folder}/
    fi
    execute cp 'functions.sh' ${build_folder}/

    execute pushd ${build_folder}
        execute ./chevahbs build $OS ${install_folder}
        if [ -e "Makefile" ]; then
            lib_config_folder="${install_folder}/lib/config"
            makefile_name="Makefile.${OS}.${version_folder}"
            execute mkdir -p ${lib_config_folder}
            execute cp 'Makefile' ${lib_config_folder}/${makefile_name}
        fi
    execute popd
}


#
# Create the distributable archive.
#
# It also generates the symlink to latest build.
#
# Args:
#  * kind = (agent|python2.5)
#  * target_folder = name of the folder to be archived.
#
make_dist(){
    kind=$1
    target_folder=$2

    target_path=../dist/${kind}/${OS}/${ARCH}
    target_common=python-${PYTHON_BUILD_VERSION}.${PYTHON_PACKAGE_VERSION}-${OS}-${ARCH}
    target_tar=${target_path}/${target_common}.tar
    target_tar_gz=${target_tar}.gz

    tar_gz_file=${target_folder}.tar.gz
    tar_gz_source_file=${target_common}.tar.gz

    # Create a clean dist folder.
    execute rm -rf ${DIST_FOLDER}
    execute mkdir -p ${DIST_FOLDER}/${kind}/${OS}/${ARCH}

    # Create tar inside dist folder.
    execute pushd ${BUILD_FOLDER}
        echo "Creating $target_tar_gz from $target_folder."
        execute tar -cf $target_tar $target_folder
        execute gzip $target_tar
    execute popd
}


#
# Wipe the manifest of source.
#
wipe_manifest() {
    local source=$1
    local manifest_wiper=$CHEVAH_BUILD_PATH/../../win-tools/manifest-wiper.exe

    echo "Extracting manifests for $source"
    execute $manifest_wiper --verbose --extract ${source}.embedded $source

    echo "Patching manifests to use our redistributable version"
    execute sed -e \
        "s|version=\"9.0.21022.8\"|version=\"${REDISTRIBUTABLE_VERSION}\"|" \
        < ${source}.embedded \
        > ${source}.manifest

    execute rm -f --verbose ${source}.embedded
}


#
# Get number of CPUs on supported OS'es.
#
get_number_of_cpus() {
    case "$OS" in
        win)
            # Logical CPUs (including hyper-threading) in Windows 2000 or newer.
            CPUS="$NUMBER_OF_PROCESSORS"
            ;;
        aix*)
            # Physical CPUs on AIX 5.3/6.1/7.1, including (v)WPARs.
            # CPU threads don't help us on PPC64 with this workload.
            CPUS=$(lparstat -i | grep ^"Active Physical CPUs" | cut -d\: -f2)
            if [ $CPUS -gt 8 ]; then
                # In IBM's cloud, OpenSSL compilation breaks with lots of CPUs.
                CPUS=8
            fi
            ;;
        sol*)
            # Physical CPUs. SPARC has lots of threads lately, but they don't
            # help much here. Tested on Solaris 10/11 on X86/AMD64/SPARC.
            CPUS=$(/usr/sbin/psrinfo -p)
            ;;
        macos|fbsd*|obsd*)
            # Logical CPUs.
            CPUS=$(sysctl -n hw.ncpu)
            ;;
        *)
            # Only Linux distros should be left.
            # Logical CPUS.
            # Don't use lscpu/nproc or other stuff not present on older distros.
            CPUS=$(getconf _NPROCESSORS_ONLN)
            ;;
    esac
}


#
# Hack for not finding ld_so_aix & co. in AIX, even with the changes lifted
# from upstream issue tracker. More at https://bugs.python.org/issue18235.
#
aix_ld_hack() {

    if [ "${OS%aix*}" != "" ]; then
        return
    fi

    custom_python_dir="/lib/$PYTHON_VERSION"
    case $* in
        init)
            if [ -e "$custom_python_dir" ]; then
                (>&2 echo "$custom_python_dir already exists, not proceeding!")
                exit 99
            fi
            execute sudo mkdir -p "$custom_python_dir"/config
            execute sudo cp "$INSTALL_FOLDER"/lib/"$PYTHON_VERSION"/config/* \
                "$custom_python_dir"/config/
            ;;
        cleanup)
            execute sudo rm -rf "$custom_python_dir"
            ;;
    esac
}


#
# Put stuff where it's expected and remove some of the cruft.
#
cleanup_install_dir() {
    local python_lib_file="lib${PYTHON_VERSION}.a"

    echo "::group::Clean up Python install dir"

    execute pushd ${BUILD_FOLDER}/${PYTHON_BUILD_FOLDER}
        echo "Cleaning up Python's caches and compiled files..."
        find lib/ | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

        case $OS in
            win)
                # Remove Tcl/Tk stuff.
                execute rm -rf lib/tcl/ lib/Lib/lib-tk/ lib/DLLs/t{k,cl}8*.dll
                # Remove docs / test stuff.
                execute rm -rf lib/Doc/ lib/Lib/test/
                ;;
            *)
                # Remove test stuff
                execute rm -rf lib/python2.7/test/
                # Move all binaries to lib/config
                execute mkdir -p lib/config
                execute mv bin/ lib/config/
                execute mkdir bin
                execute pushd lib/config/bin/
                    # Move Python binary back as bin/python, then link to it.
                    execute mv $PYTHON_VERSION ../../../bin/python
                    execute ln -s ../../../bin/python $PYTHON_VERSION
                    # OS-related fixed for the Python binaries.
                    case $OS in
                        macos)
                            # The binary is already stripped on macOS.
                            execute rm python2
                            execute ln -s $PYTHON_VERSION python2
                            ;;
                        *)
                            execute strip $PYTHON_VERSION
                            ;;
                    esac
                execute popd
                # OS-related stripping for libs.
                # Not sure why this particular lib is like that on Python 2.7,
                # we'll set the original permissions after stripping the lib.
                chmod u+w lib/libpython2.7.a
                case $OS in
                    macos)
                        # Darwin's strip command is different.
                        execute strip -r lib/lib*.a
                        ;;
                    *)
                        execute strip lib/lib*.a
                        # On CentOS 5, libffi and OpenSSL install to lib64/.
                        if [ -d lib64 ]; then
                            echo "/lib64 found!"
                            exit 98
                        fi
                        ;;
                esac
                chmod u-w lib/libpython2.7.a
                # Symlink the copy of libpython*.a too.
                execute pushd lib/$PYTHON_VERSION/config/
                    execute rm $python_lib_file
                    execute ln -s ../../$python_lib_file
                execute popd
                # Remove OpenSSL files if present.
                execute rm -rf ssl/
                # Remove (mostly OpenSSL) docs and manuals.
                execute rm -rf share/
                # Remove pysqlite2 CSS files.
                execute rm -rf pysqlite2-doc
                # Remove man files.
                execute rm -rf man/
                # Move stray pkgconfig/* to lib/pkgconfig/.
                if [ -d pkgconfig ]; then
                    execute mv pkgconfig/* lib/pkgconfig/
                    execute rmdir pkgconfig/
                fi
                # Move include/ to lib/include/.
                execute mv include/ lib/
                ;;
        esac
    execute popd

    # Output version / rev / os / arch to a dedicated file in the archive.
    echo "${PYTHON_BUILD_VERSION}.${PYTHON_PACKAGE_VERSION}-${OS}-${ARCH}" \
        > ${BUILD_FOLDER}/${PYTHON_BUILD_FOLDER}/lib/PYTHON_PACKAGE_VERSION

    echo "::endgroup::"
}


#
# Safety DB IDs to be ignored when using cryptography 3.2.
#
add_ignored_safety_ids_for_cryptography32() {
    # Safety ID 36252:
    #     Cryptography 3.3 no longer allows loading of finite field
    #     Diffie-Hellman parameters of less than 512 bits in length.
    #     This change is to conform with an upcoming OpenSSL release
    #     that no longer supports smaller sizes. These keys were
    #     already wildly insecure and should not have been used in
    #     any application outside of testing.
    # Safety ID 36533 (CVE-2020-36242):
    #     In the cryptography package before 3.3.2 for Python,
    #     certain sequences of update calls to symmetrically encrypt
    #     multi-GB values could result in an integer overflow and
    #     buffer overflow, as demonstrated by the Fernet class.
    SAFETY_IGNORED_OPTS="$SAFETY_IGNORED_OPTS -i 39252 -i 39606"
}


#
# Construct a SFTP batch for uploading testing packages through GitHub actions.
# Files are uploaded with a temporary name and then renamed to final name.
#
build_publish_dist_sftp_batch() {
    local full_ver="${PYTHON_BUILD_VERSION}.${PYTHON_PACKAGE_VERSION}"
    local local_dir="${DIST_FOLDER}/python/${OS}/${ARCH}/"
    local upload_dir="testing/${full_ver}"
    local pkg_file="python-${full_ver}-${OS}-${ARCH}.tar.gz"
    local local_file="${local_dir}/${pkg_file}"
    local dest_file="${upload_dir}/${pkg_file}"

    # The mkdir command is prefixed with '-' to allow it to fail because
    # $upload_dir exists if this is not the first upload for this version.
    echo "-mkdir $upload_dir"                    > build/publish_dist_sftp_batch
    echo "put $local_file ${dest_file}.part"    >> build/publish_dist_sftp_batch
    echo "rename ${dest_file}.part $dest_file"  >> build/publish_dist_sftp_batch

    # Add missing vars to the file to be sourced by the sftp upload script.
    echo DIST_FOLDER="$DIST_FOLDER" >> BUILD_ENV_VARS
    echo UPLOAD_FOLDER="$upload_dir" >> BUILD_ENV_VARS
}
