#!/bin/bash

yum install wget qt5-qtbase qt5-qtbase-devel alsa-lib alsa-lib-devel alsa-plugins-pulseaudioy freetype freetype-devel fontconfig fontconfig-devel libX11 libX11-devel libXi libXi-devel libXinerama libXinerama-devel

# SDL2
cd ~/
wget https://www.libsdl.org/release/SDL2-2.0.4.tar.gz
tar -zxvf SDL2-2.0.4.tar.gz
rm -fr SDL2-2.0.4.tar.gz
cd SDL2-2.0.4
mkdir build
cd build
../configure
make -j4
make install

# SDL-ttf2
cd ~/
wget https://www.libsdl.org/projects/SDL_ttf/release/SDL2_ttf-2.0.14.tar.gz
tar -zxvf SDL2_ttf-2.0.14.tar.gz
rm -fr SDL2_ttf-2.0.14.tar.gz
cd SDL2_ttf-2.0.14
mkdir build
cd build
../configure
make -j4
make install

cd /io/
git clone https://github.com/M-J-Murray/mame
cd mame
make SUBTARGET=arcade -j4
mkdir -p /io/binary
cp mamearcade64 /io/binary/mame

# python3 path /opt/python/cp3*/bin