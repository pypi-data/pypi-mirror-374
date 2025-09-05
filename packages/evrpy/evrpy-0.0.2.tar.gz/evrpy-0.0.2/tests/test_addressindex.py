"""
Unit test for WalletRPC using testnet configuration.

This test assumes that `evrmored` is running in testnet mode and that
the test addresses and assets exist with appropriate balances.

Note:
- No mocking is used. This will execute a real transaction on testnet.
- Use with caution and only on testnet.
"""

from evrpy import AddressindexRPC
import random

# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = AddressindexRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)

FROM_ADDRESS = ["mt9SMCXuqpdxdANbginxLrhUCF2iqkz34r","n4iLxDUVRsJrf4824Wdur2nVoZDAtGUtEv"]
TO_ADDRESS = "mpBNmmYYqxYAJK9UPnU5n7XJ3HcTjhrch1"
INCLUDE_ASSETS = [True, False]
SATOSHI_VALUE_CONVERTER = 10**(-8)

def test_getaddressbalance():
    asset_inclusion = random.choice(INCLUDE_ASSETS)
    address = FROM_ADDRESS
    print(f'asset_inclusion: {asset_inclusion}')
    result = rpc.getaddressbalance(
        addresses=address,
        include_assets=asset_inclusion
    )
    # print(f'result: {result}')


    if asset_inclusion:
        for i in range(len(result)):
            for addy in address:
                print(f'Address: {addy}\n'
                    f'Asset Name: {result[i]["assetName"]}\n'
                    f'Balance: {result[i]["balance"]*SATOSHI_VALUE_CONVERTER}\n'
                    f'Received: {result[i]["received"]*SATOSHI_VALUE_CONVERTER}\n\n')

    else:
        for addy in address:
            print(f"\nEVR balance information for {addy}:\n"
                f"EVR Balance  = {result['balance']*SATOSHI_VALUE_CONVERTER}\n"
                f"EVR Balance  = {result['received']*SATOSHI_VALUE_CONVERTER}\n"
                f"\nfull result below(NOT converted from satoshis):\n{result}")


def test_getaddressdeltas():
    address = FROM_ADDRESS
    result = rpc.getaddressdeltas(
        addresses=address,
        start=1,
        end=1062559,
        chain_info="True",
        asset_name="Neubtrino"
    )

    print(f'address deltas:\n{result}')


def test_getaddressmempool():
    address = FROM_ADDRESS
    result = rpc.getaddressmempool(
        addresses=address,
        include_assets=True
    )

    print(f'address mempool:\n{result}')


def test_getaddresstxids():
    address = FROM_ADDRESS
    result = rpc.getaddresstxids(
        addresses=address,
        include_assets=True
    )

    print(f'address TXIDs:\n{result}')


def test_getaddressutxos():
    address = FROM_ADDRESS
    result = rpc.getaddressutxos(
        addresses=address,
        chain_info=True,
        asset_name='*'
    )  # result is expected to be a Python dict returned by the RPC call.
       # It should contain top-level keys like "utxos" (list of dicts) and possibly "chainInfo" (dict).

    print(f'address UTXOs:\n{result}')
    # Prints the entire result dictionary. Data type: dict

    print(f'\niterated result')
    # Marker print statement to show the next section of output

    for key, value in result.items():
        # Iterates through the dictionary's key-value pairs.
        # 'key' is a str, 'value' can be a dict, list, str, int, etc. depending on the key.
        print(f'key: {key}\nvalue: {value}\n')
        # Prints each key (str) and its corresponding value (varies by key)

    print(f'result[utxos]: {result["utxos"]}')
    # Prints the value stored under the "utxos" key.
    # Data type: list of dicts, where each dict represents one UTXO.

    print(f'\niterated through result[utxos]')
    # Marker print statement for clarity

    for key, value in result['utxos'][0].items():
        # Iterates through the first UTXO dictionary in the list.
        # 'key' is a str (e.g., "address", "assetName", "txid", "satoshis"),
        # 'value' is usually str or int depending on the field.
        print(f'{key}: {value}')
        # Prints each field name and value for the first UTXO





if __name__ == "__main__":
    # test_getaddressbalance()
    # test_getaddressdeltas()
    # test_getaddressmempool()
    # test_getaddresstxids()
    test_getaddressutxos()