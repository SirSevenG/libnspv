#!/usr/bin/env python3
# Copyright (c) 2020 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://www.opensource.org/licenses/mit-license.php.

import pytest
from test_framework.nspvlib import prepare_proxy_connection
import os


chain_params = {
                    "KMD": {
                            'tx_list_address': 'RGShWG446Pv24CKzzxjA23obrzYwNbs1kA',
                            'min_chain_height': 1468080,
                            'notarization_height': '1468000',
                            'hdrs_proof_low': '1468100',
                            'hdrs_proof_high': '1468200',
                            'numhdrs_expected': 151,
                            'tx_proof_id': 'f7beb36a65bc5bcbc9c8f398345aab7948160493955eb4a1f05da08c4ac3784f',
                            'tx_spent_height': 1456212,
                            'port': '7771',
                           },
                    "ILN": {
                            'tx_list_address': 'RUp3xudmdTtxvaRnt3oq78FJBjotXy55uu',
                            'min_chain_height': 3689,
                            'notarization_height': '2000',
                            'hdrs_proof_low': '2000',
                            'hdrs_proof_high': '2100',
                            'numhdrs_expected': 113,
                            'tx_proof_id': '67ffe0eaecd6081de04675c492a59090b573ee78955c4e8a85b8ac0be0e8e418',
                            'tx_spent_height': 2681,
                            'port': '12986',
                           },
                    "HUSH": {
                             'tx_list_address': 'RCNp322uAXmNo37ipQAEjcGQgBXY9EW9yv',
                             'min_chain_height': 69951,
                             'notarization_height': '69900',
                             'hdrs_proof_low': '66100',
                             'hdrs_proof_high': '66200',
                             'numhdrs_expected': 123,
                             'tx_proof_id': '661bae364443948a009fa7f706c3c8b7d3fa6b0b27eca185b075abbe85bbdedc',
                             'tx_spent_height': 2681,
                             'port': '18031'
                            },
                    "RICK": {
                             'tx_list_address': 'RFNGdjCCApFfqUY8yWrvS9NG8QLrKFkM7K',
                             'min_chain_height': 495000,
                             'notarization_height': '435000',
                             'hdrs_proof_low': '495337',
                             'hdrs_proof_high': '495390',
                             'numhdrs_expected': 77,
                             'tx_proof_id': 'ac891ff08f952398ff544e12960dad254b1e628ce915b8185386151bd7782259',
                             'tx_spent_height': 495327,
                             'port': '25435'
                            }
                    }


@pytest.fixture(scope='session')
def proxy_connection():
    connected = []

    def _proxy_conenction(url):
        call = prepare_proxy_connection(url)
        connected.append(call)
        return call

    yield _proxy_conenction

    print("\nStopping background nspv process")
    for each in connected:
        each.stop()


@pytest.fixture(scope='session')
def get_test_params(proxy_connection):
    wif_real = os.environ.get('WALL')
    addr_send = os.environ.get('ADDRESS')
    coin = os.environ.get('CHAIN')
    userpass = "userpass"
    url = "http://127.0.0.1:" + chain_params.get(coin).get('port')
    proxy = proxy_connection(url)
    test_params = {
        "wif_real": wif_real,
        "addr_send": addr_send,
        'coin': coin,
        "chain_params": chain_params.get(coin),
        'proxy': proxy
    }
    proxy.logout()
    return test_params
