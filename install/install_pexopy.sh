#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
  then echo "Root access is required to run this script. If you prefer ti install GMP yourself, please visit https://gmplib.org/"
  exit
fi

### install R, this requires sudo
apt-get install r-base
# install R libraries
Rscript install_dependencies.R


### download PEXO
pexodir=$HOME/.pexo # target directory
mkdir $pexodir

# set the PEXODIR variable, used by PEXOpy
export PEXODIR=$pexodir
echo "export PEXODIR=$pexodir" >> $HOME/.bashrc # add an entry to your .bashrc
# clone PEXO
git clone https://github.com/phillippro/pexo.git $pexodir