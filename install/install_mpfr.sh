#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
  then echo "Root access is required to run this script. If you prefer ti install MPFR yourself, please visit https://www.mpfr.org/"
  exit
fi

mpfrdir=$HOME/mpfr/
cwd=$(pwd)

mkdir $mpfrdir
cd $mpfrdir


wget https://www.mpfr.org/mpfr-current/mpfr-4.0.2.tar.bz2
tar -C . -xvf mpfr-4.0.2.tar.bz2
rm mpfr-4.0.2.tar.bz2
cd mpfr-4.0.2

./configure
make
make check
make install

cd $cwd