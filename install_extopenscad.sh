#!/usr/bin/env bash

sudo apt-get install ghc cabal-install zlib1g-dev
cabal update && cabal install implicit