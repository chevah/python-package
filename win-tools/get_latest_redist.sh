#!/bin/sh

# Microsoft Visual C++ 2008 version/revision to collect.
export REDISTRIBUTABLE_VERSION=9.0.30729.9518

for ARCH in x86 amd64; do
    echo "Creating $REDISTRIBUTABLE_VERSION/$ARCH sub-dir..."
    mkdir -p $REDISTRIBUTABLE_VERSION/$ARCH
    echo "Copying over $ARCH DLLs..."
    cp -v $(find /c/Windows/WinSxS -name 'msvc?90.dll' | grep 9.0.30729.9518 | grep WinSxS/$ARCH) $REDISTRIBUTABLE_VERSION/$ARCH/
done
