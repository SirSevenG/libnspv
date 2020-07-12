#!/usr/bin/env python3
# Copyright (c) 2020 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://www.opensource.org/licenses/mit-license.php.

import subprocess
import time
import os


def main():
    coin = os.environ.get('CHAIN')
    if not coin:
        raise Exception("Invalid setup file")

    command1 = ["./nspv", coin]
    command2 = ["python3", "-m", "pytest", "./rpctest/test_nspv.py", "-s"]

    nspv = subprocess.Popen(command1, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    if nspv.poll():
        print("nspv not running")
    else:
        print("nspv is running")
    time.sleep(25)
    subprocess.Popen(command2, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)


if __name__ == "__main__":
    main()
