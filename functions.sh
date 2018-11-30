#!/usr/bin/env bash
#
# Shared code for all binary-dist scripts.
#


# Define global variables
COMMAND=""
OS=""
INSTALL_FOLDER=""

# Check if debugging environment variable is set and initialize with 0 if not.
if [ -z "$DEBUG" ] ; then
    DEBUG=0
fi


help_text_help=\
"Show help for a command."
command_help() {
    local command=$1
    local help_command="help_$command"
    # Test to see if we have a valid help method, otherwise call
    # the general help.
    type $help_command &> /dev/null
    if [ $? -eq 0 ]; then
        $help_command
    else
        echo "Commands are:"
        for help_text in `compgen -A variable help_text_`
        do
            command_name=${help_text#help_text_}
            echo -e "  $command_name\t\t${!help_text}"
        done
    fi
}

#
# Main command selection.
#
# Select fuctions which are made public.
#
select_command() {
    local command=$1
    shift
    case $command in
        "")
            command_help
            exit 1
            ;;
        *)
            # Test to see if we have a valid command, otherwise call
            # the general help.

            call_command="command_$command"
            type $call_command &> /dev/null
            if [ $? -eq 0 ]; then
                $call_command $@
            else
                command_help
                echo ""
                echo "Unknown command: ${command}."
                exit 1
            fi
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

# Move source to target, making sure mv will not fail if a folder
# already exists.
#
# The move is done by merging the folders.
safe_move() {
    source=$1
    target=$2
    execute cp -r $source $target
    execute rm -rf $source
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
    # FIXME:
    # Use $REDISTRIBUTABLE_VERSION for version matching here.
    execute sed -e \
        's|version="9.0.21022.8"|version="9.00.30729.6161"|' \
        -e 's|publicKeyToken="1fc8b3b9a1e18e3b"||' \
        < ${source}.embedded \
        > ${source}.manifest

    execute rm -f --verbose ${source}.embedded

}

#
# Get number of CPUs on supported OS'es.
#
get_number_of_cpus() {
    case "$OS" in
        windows*)
            # Logical CPUs (including hyper-threading) in Windows 2000 or newer.
            CPUS="$NUMBER_OF_PROCESSORS"
            ;;
        aix*)
            # Physical CPUs on AIX 5.3/6.1/7.1, including (v)WPARs.
            # CPU threads don't help us on PPC64 with this workload.
            CPUS=$(lparstat -i | grep ^"Active Physical CPUs" | cut -d\: -f2)
            ;;
        solaris*)
            # Physical CPUs. SPARC has lots of threads lately, but they don't
            # help much here. Tested on Solaris 10/11 on X86/AMD64/SPARC.
            CPUS=$(/usr/sbin/psrinfo -p)
            ;;
        hpux*)
            # Logical CPUs. Tested on HP-UX 11.31 running on Itaniums.
            CPUS=$(/usr/sbin/ioscan -kFC processor | wc -l)
            ;;
        osx*|macos*|freebsd*|openbsd*|netbsd*)
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
# Safety DB IDs to be ignored when using pyOpenSSL 0.13.1.
# Reported upstream at https://github.com/pyupio/safety/issues/174.
#
add_ignored_safety_ids_for_pyopenssl_false_positives() {
    # ID 36533: Python Cryptographic Authority pyopenssl version prior to
    #     version 17.5.0 contains a CWE-416: Use After Freevulnerability
    #     in X509 object handling that can result in Use after free can
    #     lead to possible denial of service or remote code execution.
    #     This attack appear to be exploitable via Depends on the calling
    #     application and if it retains a reference to the memory..
    #     This vulnerability appears to have been fixed in 17.5.0.
    # ID 36534: Python Cryptographic Authority pyopenssl version Before
    #     17.5.0 contains a CWE - 401 : Failure to Release Memory Before
    #     Removing Last Reference vulnerability in PKCS #12 Store that can
    #     result in Denial of service if memory  runs low or is exhausted.
    SAFETY_FALSE_POSITIVES_OPTS="$SAFETY_FALSE_POSITIVES_OPTS -i 36533 -i 36534"
}
