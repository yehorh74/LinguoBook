[app]

# (str) Title of your application
title = LinguoBook

# (str) Package name
package.name = linguobook

# (str) Package domain (needed for android/ios packaging)
package.domain = org.daned

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,ttf,fb2,kv,json

# (str) Application versioning (method 1)
version = 1.4.0

presplash.filename = LinguoBook_splash.png

android.presplash_color = #A2C2E8

icon.filename = LinguoBook_fixed.png

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0,pyjnius,android,deep-translator,requests,urllib3,openssl,certifi,beautifulsoup4,typing_extensions,kivymd==1.2.0

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

#
# Android specific
#

# (list) Permissions
android.permissions = READ_EXTERNAL_STORAGE,INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 24

# (int) Android NDK API to use
android.ndk_api = 24

# (str) Android NDK version to use
android.ndk = 25c

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (str) Path to custom AndroidManifest.xml
# android.manifest.xml = ./android_manifest.xml

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1