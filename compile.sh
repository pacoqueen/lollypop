#!/bin/bash

# sudo apt install meson libglib2.0-dev yelp-tools libgirepository1.0-dev libgtk-3-dev

#cd lollypop-portal && ./compile.sh; cd ..

meson builddir --prefix=/home/`whoami`/.local
ninja -C builddir install
