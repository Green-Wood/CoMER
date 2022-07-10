#!/bin/bash

version=$1

# install lgeval and tex2symlg (in CoMER folder)
export LgEvalDir=$(pwd)/lgeval
export Convert2SymLGDir=$(pwd)/convert2symLG
export PATH=$PATH:$LgEvalDir/bin:$Convert2SymLGDir

for y in '2014' '2016' '2019'
do
    echo '****************' start evaluating CROHME $y '****************'
    bash scripts/test/eval.sh $version $y 4
    echo 
done
