#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
  then echo "Root access is required to run this script. If you prefer ti install GMP yourself, please visit https://gmplib.org/"
  exit
fi

gmpdir=$HOME/gmp/
cwd=$(pwd)

mkdir $gmpdir
cd $gmpdir

# dependencies?
# from https://www.mersenneforum.org/showthread.php?t=23079
apt-get install g++ m4 zlib1g-dev make p7zip

# see https://gmplib.org/
wget https://gmplib.org/download/gmp/gmp-6.1.2.tar.bz2
tar -C . -xvf gmp-6.1.2.tar.bz2
rm gmp-6.1.2.tar.bz2
cd gmp-6.1.2

# see https://gmplib.org/manual/Installing-GMP.html
./configure
make
make check
make install

cd $cwd