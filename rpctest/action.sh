#!/bin/bash
echo "starting nspv"
cd ..
nohup ./nspv ${CHAIN} &>/dev/null &
sleep 25
cd rpctest
echo "running tests"
python3 -m pytest -s -vv test_nspv.py
