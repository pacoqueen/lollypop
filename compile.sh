#!/bin/bash

./autogen.sh --prefix=/home/`whoami`/.local
make
# checkinstall
make install
