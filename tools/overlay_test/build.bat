@echo off
setlocal enabledelayedexpansion

echo === FloatMask Overlay Test APK Build ===

set PROJECT_DIR=E:\桌面\综合课程设计\tools\overlay_test
set BUILD_DIR=%PROJECT_DIR%\build
set SRC_DIR=%PROJECT_DIR%\src
set RES_DIR=%PROJECT_DIR%\res
set MANIFEST=%PROJECT_DIR%\AndroidManifest.xml

set ANDROID_SDK=%LOCALAPPDATA%\Android\Sdk
set BUILD_TOOLS=%ANDROID_SDK%\build-tools\35.0.1
set PLATFORM=%ANDROID_SDK%\platforms\android-35\android.jar

set JAVA_HOME=E:\Android Studio\jbr
rem (verified jbr exists at E:\Android Studio\jbr)
set JAVAC=%JAVA_HOME%\bin\javac.exe
set JAVA=%JAVA_HOME%\bin\java.exe

set AAPT=%BUILD_TOOLS%\aapt.exe
set D8=%BUILD_TOOLS%\d8.bat
set ZIPALIGN=%BUILD_TOOLS%\zipalign.exe
set APKSIGNER=%BUILD_TOOLS%\apksigner.bat

echo.
echo [1/6] Cleaning build directory...
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%\classes"
mkdir "%BUILD_DIR%\gen"

echo [2/6] Compiling resources with AAPT...
"%AAPT%" package -f -m -J "%BUILD_DIR%\gen" -M "%MANIFEST%" -S "%RES_DIR%" -I "%PLATFORM%" --auto-add-overlay
if errorlevel 1 (
    echo ERROR: AAPT resource compilation failed!
    exit /b 1
)

echo [3/6] Compiling Java source...
dir /s /b "%SRC_DIR%\*.java" > "%BUILD_DIR%\sources.txt"
dir /s /b "%BUILD_DIR%\gen\*.java" >> "%BUILD_DIR%\sources.txt"
"%JAVAC%" -source 1.8 -target 1.8 -bootclasspath "%PLATFORM%" -classpath "%PLATFORM%" -d "%BUILD_DIR%\classes" @"%BUILD_DIR%\sources.txt"
if errorlevel 1 (
    echo ERROR: Java compilation failed!
    exit /b 1
)

echo [4/6] Converting to DEX...
"%JAVA%" -cp "%BUILD_TOOLS%\lib\d8.jar" com.android.tools.r8.D8 --release --output "%BUILD_DIR%" --lib "%PLATFORM%" --min-api 26 --file-per-class "%BUILD_DIR%\classes\com\floatmask\test\*.class"
if errorlevel 1 (
    echo ERROR: D8 conversion failed!
    exit /b 1
)

echo [5/6] Packaging APK...
"%AAPT%" package -f -M "%MANIFEST%" -S "%RES_DIR%" -I "%PLATFORM%" -F "%BUILD_DIR%\floatmask-test.unsigned.apk" --auto-add-overlay
if errorlevel 1 (
    echo ERROR: APK packaging failed!
    exit /b 1
)

cd "%BUILD_DIR%"
"%JAVA%" -jar "%BUILD_TOOLS%\lib\apksigner.jar" sign --ks "%BUILD_DIR%\debug.keystore" --ks-pass pass:android --key-pass pass:android --ks-key-alias androiddebugkey "%BUILD_DIR%\floatmask-test.unsigned.apk"
if errorlevel 1 (
    echo ERROR: APK signing failed! Trying jarsigner...
    jarsigner -keystore "%BUILD_DIR%\debug.keystore" -storepass android -keypass android "%BUILD_DIR%\floatmask-test.unsigned.apk" androiddebugkey
)

echo [6/6] Zipaligning...
"%ZIPALIGN%" -f 4 "%BUILD_DIR%\floatmask-test.unsigned.apk" "%BUILD_DIR%\floatmask-test.apk"
if errorlevel 1 (
    echo WARNING: Zipalign failed, using unsigned APK
    copy "%BUILD_DIR%\floatmask-test.unsigned.apk" "%BUILD_DIR%\floatmask-test.apk"
)

echo.
echo === BUILD SUCCESSFUL ===
echo APK: %BUILD_DIR%\floatmask-test.apk
