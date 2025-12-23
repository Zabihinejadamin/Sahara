[app]

# (str) Title of your application
title = Sahara Raiders

# (str) Package name
package.name = sahararaiders

# (str) Package domain (needed for android/ios packaging)
package.domain = org.sahararaiders

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 0.1

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT_TO_PY

#
# OSX Specific
#

#
# author = © Copyright Info
# change the major version of python used by the app
osx.python_version = 3

# Kivy version to use
osx.kivy_version = 2.3.0

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
# Available values correspond to android's @android:color/...
#presplash.color = #FFFFFF

# (list) Permissions
#android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 20

# (str) Android NDK version to use
android.ndk = 19c

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
# android.skip_update = False

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy-based app
#android.apptheme = @android:style/Theme.NoTitleBar

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src =

# (list) Android AAR archives to add (same as add_jars, but should be AAR
# archives)
#android.add_aars =

# (list) Gradle dependencies to add (same as add_jars or add_aars,
# but for Gradle dependencies. Comma separated.)
# android.gradle_dependencies =

# (list) Java classes to add as activities to the manifest.
#android.add_activities = com.example.ExampleActivity

# (str) google analytics id
#android.google_analytics =

# (str) Push notification keys and stuff
#android.push_bullet_public_key = 
#android.push_bullet_secret_key =

# (str) OUYA Console category in which your app will be listed
#android.ouya.category = GAME

# (str) OUYA Console icon file path
#android.ouya.icon.filename = 

# (str) Filename to your Android certificate keystore file
#android.signing.keystore =

# (str) Password for Android signing keystore
#android.signing.keystore.password =

# (str) Alias of key in Android signing keystore
#android.signing.keyalias =

# (str) Password of key in Android signing keystore
#android.signing.keyalias.password =

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = armeabi-v7a

# (int) overrides automatic versionCode computation (used in build.gradle)
# this is not the same as app version and should only be edited if you know what you're doing
# android.numeric_version = 1

#
# Python for android (p4a) specific
#

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.local_recipes =

# (str) Filename to the hook for p4a
#p4a.hook =

# (str) Bootstrap to use for android builds (android or sdl2)
p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for booting a debug apk)
#p4a.port =

#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
#ios.kivy_ios_dir =
# Alternately, specify the directory in a custom build of kivy-ios
#ios.kivy_ios_url =

# (str) Name of the certificate to use for signing the debug version
# Get a list of available identities: buildozer ios list_identities
#ios.codesign.debug = "iPhone Developer: Python for iOS"

# (str) Name of the certificate to use for signing the release version
#ios.codesign.release = %(ios.codesign.debug)s

#
# OSX specific
#

# (str) Name of the certificate to use for signing the release version
#osx.codesign.release = 

# (str) Name of the certificate to use for signing debug version
#osx.codesign.debug = 

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of:
#source.exclude_patterns = license,images/*/*.jpg
#    This can be translated into:
#
#    [app:source.exclude_patterns]
#    license
#    images/*/*.jpg

#    -----------------------------------------------------------------------------
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you want to deploy a demo version of your application without
#    HD content. You could first change the title to add "(demo)" in the name
#    and extend the excluded directories to remove the HD content.
#
#    [app@demo]
#    title = My Application (demo)
#
#    [app:source.exclude_dirs@demo]
#    images_hd

#    -----------------------------------------------------------------------------
#    Note: this .spec file is essentially for Android builds with buildozer.
#    For iOS, you would need additional iOS-specific configurations.
