call "C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.cmd" /x64 /release 
SET PATH=%PATH%;C:\Program Files\NASM;C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1\Bin
SET INCLUDE=C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\INCLUDE;C:\Program Files\Microsoft SDKs\Windows\v7.1\INCLUDE;C:\Program Files\Microsoft SDKs\Windows\v7.1\INCLUDE\gl;C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1\Include
SET LIB=%LIB%;C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1\Lib\x64

perl Configure %OPENSSL_BUILD_FLAGS_WINDOWS% VC-WIN64A no-shared
nmake
if %errorlevel% neq 0 exit /b %errorlevel%
nmake test
if %errorlevel% neq 0 exit /b %errorlevel%

SET INSTALL_DIR=..\python2.7-win-x64\lib
mkdir %INSTALL_DIR%\libs
move libcrypto.lib %INSTALL_DIR%\libs\
move libssl.lib %INSTALL_DIR%\libs\
move include %INSTALL_DIR%\
