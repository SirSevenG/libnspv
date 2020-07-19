#!/usr/bin/env python3
# Copyright (c) 2020 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://www.opensource.org/licenses/mit-license.php.


from test_framework.nspvlib import assert_equal, assert_in, assert_success,\
                                   assert_contains, assert_not_contains, assert_error
import pytest
import time

"""
   Simple unittest based on pytest framework for libnspv
   Make sure you have installed framework: pip3 install pytest
   Set wif to spend form and address to spend to as env vars:
   CHAIN="coin_ticker", WALL="wif", ADDRESS="coinaddress"
   Default test coin is RICK, it should be available in coins file
   You can add any new coins to test, please set coin_params dict entry in conftest.py
   To run tests do: "python3 -m pytest test_nspv.py -s" from rpctest directory
"""


@pytest.mark.usefixtures("proxy_connection")
class TestNSPV:

    def test_help_call(self, get_test_params):
        """ Response should contain "result": "success"
            Response should contain actual help data"""
        call = get_test_params.get('proxy')
        print('\n', "testing help call")
        rpc_call = call.help()
        if not rpc_call:
            pytest.exit("Can't connect daemon")
        assert_success(rpc_call)
        assert_contains(rpc_call, "methods")

    def test_getpeerinfo_call(self, get_test_params):
        """Response should not be empty, at least one node should be in sync"""
        print('\n', "testing peerinfo call, checking peers status")
        rpc_call = get_test_params.get('proxy').getpeerinfo()
        if not rpc_call[0]:
            raise Exception("Empty response :", rpc_call)
        assert_contains(rpc_call[0], "ipaddress")

    def test_check_balance(self, get_test_params):
        """Check if wif given has actual balance to perform further tests"""
        print('\n', "Checking wif balance")
        get_test_params.get('proxy').login(get_test_params.get("wif_real"))
        attempt = 0
        while attempt < 10:  # after login, libnspv might take a few seconds to get user balance
            res = get_test_params.get('proxy').listunspent()
            amount = res.get("balance")
            if amount < 0.1:
                attempt += 1
                print('Waiting for possible confirmations')
                time.sleep(5)
            else:
                break
        if attempt >= 10:
            pytest.exit("Not enough balance, please use another wif")

    def test_getinfo_call(self, get_test_params):
        """ Response should contain "result": "success"
            Response should contain actual data"""
        print('\n', "testing getinfo call")
        rpc_call = get_test_params.get('proxy').getinfo()
        assert_success(rpc_call)
        assert_contains(rpc_call, "notarization")
        assert_contains(rpc_call, "header")

    def test_hdrsproof_call(self, get_test_params):
        """ Response should be successful for case 2 and fail for others
            Response should contain actual headers"""
        print('\n', "testing hdrsproof call")
        prevheight = [False, get_test_params.get("chain_params").get("hdrs_proof_low")]
        nextheight = [False, get_test_params.get("chain_params").get("hdrs_proof_high")]

        # Case 1 - False data
        rpc_call = get_test_params.get('proxy').hdrsproof(prevheight[0], nextheight[0])
        assert_error(rpc_call)

        # Case 2 - known data
        rpc_call = get_test_params.get('proxy').hdrsproof(prevheight[1], nextheight[1])
        assert_success(rpc_call)
        assert_contains(rpc_call, "prevht")
        assert_contains(rpc_call, "nextht")
        assert_contains(rpc_call, "headers")
        hdrs_resp = rpc_call.get('numhdrs')
        assert_equal(hdrs_resp, get_test_params.get("chain_params").get("numhdrs_expected"))

    def test_notarization_call(self, get_test_params):
        """ Response should be successful for case 2
         Successful response should contain prev and next notarizations data"""
        print('\n', "testing notarization call")
        height = [False, get_test_params.get("chain_params").get("notarization_height")]

        # Case 1 - False data
        rpc_call = get_test_params.get('proxy').notarizations(height[0])
        assert_error(rpc_call)

        # Case 2 - known data
        rpc_call = get_test_params.get('proxy').notarizations(height[1])
        assert_success(rpc_call)
        assert_contains(rpc_call, "prev")
        assert_contains(rpc_call, "next")

    def getnewaddress_call(self, get_test_params):
        """ Get a new address, save it for latter calls"""
        print('\n', "testing getnewaddr call")
        rpc_call = get_test_params.get('proxy').getnewaddress()
        assert_contains(rpc_call, "wifprefix")
        assert_contains(rpc_call, "wif")
        assert_contains(rpc_call, "address")
        assert_contains(rpc_call, "pubkey")

    def test_login_call(self, get_test_params):
        """"login with fresh credentials
            Response should contain address, address should be equal to generated earlier one"""
        print('\n', "testing log in call")
        call = get_test_params.get('proxy')
        rpc_call = call.getnewaddress()
        wif = rpc_call.get('wif')
        addr = rpc_call.get('address')
        rpc_call = call.login(wif)
        assert_success(rpc_call)
        assert_contains(rpc_call, "status")
        assert_contains(rpc_call, "address")
        logged_address = rpc_call.get('address')
        if logged_address != addr:
            raise AssertionError("addr missmatch: ", addr, logged_address)

    def test_listtransactions_call(self, get_test_params):
        """"Successful response should [not] contain txids and same address as requested
            Case 1 - False data, user is logged in - should not print txids for new address"""
        print('\n', "testing listtransactions call")
        call = get_test_params.get('proxy')
        call.logout()
        real_addr = get_test_params.get("chain_params").get("tx_list_address")
        rpc_call = call.getnewaddress()
        wif = rpc_call.get('wif')
        addr = rpc_call.get('address')
        rpc_call = call.login(wif)
        logged_address = rpc_call.get('address')

        # Case 1 - False Data
        rpc_call = call.listtransactions(False, False, False)
        assert_success(rpc_call)
        assert_not_contains(rpc_call, "txids")
        addr_response = rpc_call.get('address')
        if addr_response != logged_address:
            raise AssertionError("addr missmatch: ", addr_response, logged_address)

        # Case 2 - known data
        rpc_call = call.listtransactions(real_addr, 0, 1)
        assert_success(rpc_call)
        assert_contains(rpc_call, "txids")
        addr_response = rpc_call.get('address')
        if addr_response != real_addr:
            raise AssertionError("addr missmatch: ", addr_response, real_addr)

        # Case 3 - known data, isCC = 1
        rpc_call = call.listtransactions(real_addr, 1, 1)
        assert_success(rpc_call)
        assert_not_contains(rpc_call, "txids")
        addr_response = rpc_call.get('address')
        if addr_response != real_addr:
            raise AssertionError("addr missmatch: ", addr_response, real_addr)

    def test_litunspent_call(self, get_test_params):
        """ Successful response should [not] contain utxos and same address as requested"""
        print('\n', "testing listunspent call")
        call = get_test_params.get('proxy')
        call.logout()
        real_addr = get_test_params.get("chain_params").get("tx_list_address")
        rpc_call = call.getnewaddress()
        wif = rpc_call.get('wif')
        rpc_call = call.login(wif)
        logged_address = rpc_call.get('address')

        # Case 1 - False dataf
        rpc_call = call.listunspent(False, False, False)
        assert_success(rpc_call)
        assert_not_contains(rpc_call, "utxos")
        addr_response = rpc_call.get('address')
        if addr_response != logged_address:
            raise AssertionError("addr missmatch: ", addr_response, logged_address)

        # Case 2 - known data
        rpc_call = call.listunspent(real_addr, 0, 0)
        assert_success(rpc_call)
        assert_contains(rpc_call, "utxos")
        addr_response = rpc_call.get('address')
        if addr_response != real_addr:
            raise AssertionError("addr missmatch: ", addr_response, real_addr)

        # Case 3 - known data, isCC = 1, should not return utxos
        rpc_call = call.listunspent(real_addr, 1, 0)
        assert_success(rpc_call)
        assert_not_contains(rpc_call, "utxos")
        addr_response = rpc_call.get('address')
        if addr_response != real_addr:
            raise AssertionError("addr missmatch: ", addr_response, real_addr)

    def test_spend_call(self, get_test_params):
        """Successful response should contain tx and transaction hex"""
        print('\n', "testing spend call")
        call = get_test_params.get('proxy')
        amount = [False, 0.1]
        address = [False, get_test_params.get("addr_send")]

        # Case 1 - false data
        rpc_call = call.spend(address[0], amount[0])
        assert_error(rpc_call)
        rpc_call = call.spend(address[1], amount[0])
        assert_error(rpc_call)

        # Case 2 - known data, no legged in user
        rpc_call = call.spend(address[1], amount[1])
        assert_error(rpc_call)

        # Case 3 - login with wif, create a valid transaction
        call.logout()
        time.sleep(15)
        call.login(get_test_params.get("wif_real"))
        time.sleep(10)
        rpc_call = call.spend(address[1], amount[1])
        assert_success(rpc_call)
        assert_contains(rpc_call, "tx")
        assert_contains(rpc_call, "hex")

    def test_broadcast_call(self, get_test_params):
        """Successful broadcasst should have equal hex broadcasted and expected"""
        print('\n', "testing broadcast call")
        call = get_test_params.get('proxy')
        call.logout()
        time.sleep(15)
        call.login(get_test_params.get("wif_real"))
        time.sleep(10)
        rpc_call = call.spend(get_test_params.get("addr_send"), 0.1)
        hex_res = rpc_call.get("hex")
        hex = [False, "norealhexhere", hex_res]
        retcode_failed = [-1, -2, -3]

        # Cae 1 - No hex given
        rpc_call = call.broadcast(hex[0])
        assert_error(rpc_call)

        # Case 2 - Non-valid hex, failed broadcast should contain appropriate retcode
        rpc_call = call.broadcast(hex[1])
        assert_in(rpc_call, "retcode", retcode_failed)

        # Case 3 - Hex of previous transaction
        rpc_call = call.broadcast(hex[2])
        assert_success(rpc_call)
        broadcast_res = rpc_call.get("broadcast")
        expected = rpc_call.get("expected")
        if broadcast_res == expected:
            pass
        else:
            raise AssertionError("Aseert equal braodcast: ", broadcast_res, expected)

    def test_mempool_call(self, get_test_params):
        """ Response should contain txids"""
        print('\n', "testing mempool call")
        call = get_test_params.get('proxy')
        rpc_call = call.mempool()
        assert_success(rpc_call)
        # call.assert_contains(rpc_call, "txids") - mempool() response not always contains "txids" key, even on success

    def test_spentinfo_call(self, get_test_params):
        """Successful response sould contain same txid and same vout"""
        print('\n', "testing spentinfo call")
        call = get_test_params.get('proxy')
        r_txids = [False, get_test_params.get("chain_params").get("tx_proof_id")]
        r_vouts = [False, 1]

        # Case 1 - False data
        rpc_call = call.spentinfo(r_txids[0], r_vouts[0])
        assert_error(rpc_call)

        # Case 2 - known data
        rpc_call = call.spentinfo(r_txids[1], r_vouts[1])
        assert_success(rpc_call)
        txid_resp = rpc_call.get("txid")
        if r_txids[1] != txid_resp:
            raise AssertionError("Unexpected txid: ", r_txids[1], txid_resp)
        vout_resp = rpc_call.get("vout")
        if r_vouts[1] != vout_resp:
            raise AssertionError("Unxepected vout: ", r_vouts[1], vout_resp)

    def test_gettransaction(self, get_test_params):
        """Not implemented yet"""
        call = get_test_params.get('proxy')
        print('\n', "testing gettransaction call")
        rpc_call = call.gettransaction()
        assert_error(rpc_call)

    def test_autologout(self, get_test_params):
        """Wif should expeire in 777 seconds"""
        print('\n', "testing auto logout")
        call = get_test_params.get('proxy')
        rpc_call = call.getnewaddress()
        wif = rpc_call.get('wif')
        rpc_call = call.login(wif)
        assert_success(rpc_call)
        time.sleep(778)
        rpc_call = call.spend(get_test_params.get("addr_send"), 0.1)
        assert_error(rpc_call)

    def test_cleanup(self, get_test_params):
        """Send funds to reset utxo amount in wallet
           Stop nspv process after tests"""
        print('\n', "Resending funds")
        call = get_test_params.get('proxy')
        maxfee = 0.01
        call.login(get_test_params.get("wif_real"))
        time.sleep(10)
        res = call.listunspent()
        amount = res.get("balance") - maxfee
        res = call.spend(get_test_params.get("addr_send"), amount)
        hexs = res.get("hex")
        call.broadcast(hexs)
        print('\n', "stopping nspv process")
