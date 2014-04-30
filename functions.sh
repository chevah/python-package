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

    target_tar=../dist/${kind}/${OS}/${ARCH}/${target_folder}-${TIMESTAMP}.tar
    target_tar_gz=../dist/${kind}/${OS}/${ARCH}/${target_folder}-${TIMESTAMP}.tar.gz

    tar_gz_file=${target_folder}.tar.gz
    tar_gz_timestamp_file=${target_folder}-${TIMESTAMP}.tar.gz

    # Create a clean dist folder.
    execute rm -rf ${DIST_FOLDER}
    execute mkdir -p ${DIST_FOLDER}/${kind}/${OS}/${ARCH}

    # Create tar inside dist folder.
    execute pushd ${BUILD_FOLDER}
        echo "Creating $target_tar_gz from $target_folder."
        execute tar -cf $target_tar $target_folder
        execute gzip $target_tar
    execute popd

    # Create symlink.
    execute pushd ${DIST_FOLDER}/${kind}
        execute ln -sf ${OS}/${ARCH}/${tar_gz_timestamp_file} ${tar_gz_file}
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


