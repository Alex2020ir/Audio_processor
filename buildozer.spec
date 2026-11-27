[app]
title = Audio Processor
package.name = audioprocessor
package.domain = org.saber

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.exclude_dirs = bin,.buildozer,.github

version = 1.0

requirements = python3,kivy==2.3.0,numpy,pillow,matplotlib,kiwisolver,pyparsing,cycler,python-dateutil,six,fonttools,packaging,contourpy,pydub,arabic_reshaper,python-bidi,pyjnius,android

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png
icon.adaptive_foreground.filename = %(source.dir)s/assets/icon_fg.png
icon.adaptive_background.filename = %(source.dir)s/assets/icon_bg.png
presplash.filename = %(source.dir)s/assets/presplash.png
android.presplash_color = #0E1026

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO,MANAGE_EXTERNAL_STORAGE

android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
