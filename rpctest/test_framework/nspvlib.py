#!/usr/bin/env python3
# Copyright (c) 2020 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://www.opensource.org/licenses/mit-license.php.

from pycurl import error as pycurlerr
from slickrpc import Proxy
import ujson
import time
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO


class NSPVProxy(Proxy):
    def __getattr__(self, method):
        conn = self.conn
        _id = next(self._ids)

        def call(*params):
            postdata = ujson.dumps({"jsonrpc": "2.0",
                                    "method": method,
                                    "params": params,
                                    "id": _id})
            body = StringIO()
            conn.setopt(conn.WRITEFUNCTION, body.write)
            conn.setopt(conn.POSTFIELDS, postdata)
            conn.perform()
            resp = ujson.loads(body.getvalue())
            return resp
        return call


def assert_equal(first, second):
    if first != second:
        raise AssertionError(first, "not equal to", second)


def assert_success(result):
    assert_equal(result.get('result'), 'success')


def assert_in(result, key, compare_list):
    content = result.get(key)
    if content in compare_list:
        pass
    else:
        raise AssertionError("Error:", content, "not in", compare_list)


def assert_contains(result, key):
    """assert key contains expected data"""
    content = result.get(key)
    if content:
        pass
    else:
        raise AssertionError("Unexpected response, missing param: ", key)


def assert_not_contains(result, key):
    """assert key contains expected data"""
    content = result.get(key)
    if not content:
        pass
    else:
        raise AssertionError("Unexpected response, missing param: ", key)


def assert_error(result):
    """ assert there is an error with known error message """
    error_msg = ['no height', 'invalid height range', 'invalid method', 'timeout', 'error', 'no hex',
                 'couldnt get addressutxos', 'invalid address or amount too small', 'not enough funds',
                 'invalid address or amount too small', 'invalid utxo', 'wif expired', 'not implemented yet',
                 'invalid utxo']
    error = result.get('error')
    if error:
        if error in error_msg:
            pass
        else:
            raise AssertionError("Unknown error message")
    else:
        raise AssertionError("Unexpected response")


def prepare_proxy_connection(url):
    attempt = 0
    proxy = NSPVProxy(url, timeout=240)
    while attempt < 10:
        try:
            proxy.help()
            break
        except pycurlerr as e:
            attempt += 1
            if attempt >= 10:
                raise ConnectionError(e)
            time.sleep(6)
    return proxy
