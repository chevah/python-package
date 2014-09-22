#!/usr/bin/env bash
# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
#
# Put default values and create them as global variables.
OS='not-detected-yet'
ARCH='x86'
PYTHON_BIN="/bin/python"
PYTHON_VERSION="python2.7"

write_default_values() {
    echo ${PYTHON_VERSION} ${OS} ${ARCH} > DEFAULT_VALUES
}


detect_os() {
    OS=`uname -s | tr "[A-Z]" "[a-z]"`

    if [ "${OS%mingw*}" = "" ] ; then

        OS='windows'
        ARCH='x86'
        PYTHON_BIN="/lib/python.exe"
        PYTHON_LIB="/lib/Lib/"

    elif [ "${OS}" = "sunos" ] ; then

        OS="solaris"
        ARCH="`isainfo -n`"
        VERSION=`uname -r`

        if [ "$ARCH" = "i386" ] ; then
            ARCH='x86'
        elif [ "$ARCH" = "amd64" ]; then
            ARCH='x64'
        elif [ "$ARCH" = "sparcv9" ] ; then
            ARCH='sparc64'
        fi

        if [ "$VERSION" = "5.10" ] ; then
            OS="solaris10"
        fi

    elif [ "${OS}" = "aix" ] ; then

        release=`oslevel`
        case $release in
            5.1.*)
                OS='aix51'
                ARCH='ppc'
                ;;
            *)
                # By default we go for AIX 5.3 on PPC64
                OS='aix53'
                ARCH='ppc64'
            ;;
        esac

    elif [ "${OS}" = "hp-ux" ] ; then

        OS="hpux"
        ARCH=`uname -m`

    elif [ "${OS}" = "linux" ] ; then

        ARCH=`uname -m`

        if [ -f /etc/redhat-release ] ; then
            # Careful with the indentation here.
            # Make sure rhel_version does not has spaces before and after the
            # number.
            rhel_version=`\
                cat /etc/redhat-release | sed s/.*release\ // | sed s/\ .*//`
            # RHEL4 glibc is not compatible with RHEL 5 and 6.
            rhel_major_version=${rhel_version%%.*}
            if [ "$rhel_major_version" = "4" ] ; then
                OS='rhel4'
            elif [ "$rhel_major_version" = "5" ] ; then
                OS='rhel5'
            elif [ "$rhel_major_version" = "6" ] ; then
                OS='rhel6'
            elif [ "$rhel_major_version" = "7" ] ; then
                OS='rhel7'
            else
                echo 'Unsupported RHEL version.'
                exit 1
            fi
        elif [ -f /etc/SuSE-release ] ; then
            sles_version=`\
                grep VERSION /etc/SuSE-release | sed s/VERSION\ =\ //`
            if [ "$sles_version" = "11" ] ; then
                OS='sles11'
            else
                echo 'Unsuported SLES version.'
                exit 1
            fi
        elif [ -f /etc/lsb-release ] ; then
            release=`lsb_release -sr`
            case $release in
                '10.04' | '10.10' | '11.04' | '11.10')
                    OS='ubuntu1004'
                ;;
                '12.04' | '12.10' | '13.04' | '13.10')
                    OS='ubuntu1204'
                    PYTHON_LIB="/lib/${PYTHON_VERSION}/"
                ;;
                '14.04' | '14.10' | '15.04' | '15.10')
                    OS='ubuntu1404'
                ;;
                *)
                    echo 'Unsupported Ubuntu version.'
                    exit 1
                ;;
            esac
    	    
        elif [ -f /etc/slackware-version ] ; then

            # For Slackware, for now we use Ubuntu 10.04.
            # Special dedication for all die hard hackers like Ion.
    	    OS="ubuntu1004"

        elif [ -f /etc/debian_version ] ; then
            OS="debian"

        fi

    elif [ "${OS}" = "darwin" ] ; then
        osx_version=`sw_vers -productVersion`
        osx_major_version=${osx_version%.*}
    	if [ "$osx_major_version" = "10.4" ] ; then
    		OS='osx104'
    	else
    		echo 'Unsuported OS X version.'
    		exit 1
    	fi
    	
    	osx_arch=`uname -m`
    	if [ "$osx_arch" = "Power Macintosh" ] ; then
    		ARCH='ppc'
    	else
    		echo 'Unsuported OS X architecture.'
    		exit 1
    	fi
    else
        echo 'Unsuported operating system.'
        exit 1
    fi

    # Fix arch names.
    if [ "$ARCH" = "i686" ] ; then
        ARCH='x86'

    fi
    if [ "$ARCH" = "i386" ] ; then
        ARCH='x86'
    fi

    if [ "$ARCH" = "x86_64" ] ; then
        ARCH='x64'
    fi
}

detect_os
write_default_values
