# run dali-core utc
stdbuf -i0 -o0 -e0 python ./runtct-main.py utc dali-core

## run dali-toolkit utc
#stdbuf -i0 -o0 -e0 python ./runtct-main.py utc dali-toolkit

## run dali-core utc from 1278th tc function
#stdbuf -i0 -o0 -e0 python ./runtct-main.py utc dali-core 1278

## run dali-core utc from 10th to 20th tc function
#stdbuf -i0 -o0 -e0 python ./runtct-main.py utc dali-core 10 20
