"""
Unit test for AssetRPC using testnet configuration.

This test assumes that `evrmored` is running in testnet mode and that
the test addresses and asset exist with appropriate balances.

Note:
- No mocking is used. This will execute a real transaction on testnet.
- Use with caution and only on testnet.
"""

from evrpy import AssetsRPC
from itertools import product
import random
import string

# Testnet configuration — set these to valid testnet values before running
CLI_PATH = "/home/aethyn/mining/evrmore-2.0.0.test/bin/evrmore-cli"
DATA_DIR = "/home/aethyn/.evrmore-test/testnet1"
RPC_USER = "neubtrino_testnet"
RPC_PASS = "pass_testnet"
USE_TESTNET = True

rpc = AssetsRPC(
    cli_path=CLI_PATH,
    datadir=DATA_DIR,
    rpc_user=RPC_USER,
    rpc_pass=RPC_PASS,
    testnet=USE_TESTNET
)

# Testnet parameters — these must be changed to valid values
ASSET_NAME = "NEUBTRINO_IS_DUMB"
FROM_ADDRESS = "mjNgMNK73yeEwoCK19R6ewwpbTXuERhqpG"
TO_ADDRESS = "n4cjbVFC8J3fWkq9x6enERbdHW1P74hr5f"
TO_ADDRESSES = [
    "mjNgMNK73yeEwoCK19R6ewwpbTXuERhqpG",
    "n4cjbVFC8J3fWkq9x6enERbdHW1P74hr5f",
    "mhuwCVd3S4RVHku92dAQ39k8ZYWDe29nvA"
]
FROM_ADDRESSES = ["mm3YH7mGPdPav8o2in6mWYKccsbPFhdMfA",
    "mm7BqqZgkSBPkAgTa5UosFVLqbGggSXVKB",
    "mmD7ZNu3F699WJ2yZrw5RXzHsC6uVBo3FL",
    "mmKyzKGx2hFgf8AqydNeo4FjtsbBr5egp4",
    "mmMsiTpG6z4LKj7na41fsXV973sGnozFrN",
    "mmWxeDbLJQZUdpZZPZEXukGj8rVPnuqAid",
    "mmmASH2pqoeHmf66jnnCacZST4cR2JNDP6",
    "mmxKm6qwjRYwcBzThbr3Se49Jk5mieDBxM",
    "mmxkFjsXf21rGiwjxwbyaCySKw2LSGjj9P",
    "mmzVHgDsdYHmNtEp9oV9tsKp67xJNFYyCC",
    "mn1GRhCShB7kquuqWTrqoo2gyzQ6rACZ14",
    "mn8BBeegWf9SxMxoq5sG1LFNxsY9swp88i",
    "mnM1dezz9nN1A6UDPfPH5BwKiqgB4Vx55s",
    "mnQS1mjxbx6P1JBDkrTpin3ZSGYpFKYUNn",
    "mnVm1NR512tEGZBLAwduoS3oqUtCKyS5NY",
    "mnkY7xKHi1CX8YZEARG9dV4ji8n3XAwnSW",
    "mnsJseM6PzuY9UsRgwHCbySH53eTQXGAVe",
    "mnxRHPxfrtZjNbCPiJnGgqjC7TjrG64qPi",
    "mnxpa29tMK1yrZaZYziuLD3oALT5waVjQc",
    "mnzqqto4SSZxLHDjSfigjJWBWPZ5mqqyyv",
    "mo4J9wZR2dy79C6AegY9SvWdmeZ6nGRqfZ",
    "mo5Qgt6fJpY2imPLuu3TRqmtuyRB5F4fsq",
    "mo97DgYCaAwA7Nvt8XrgBrSFqSx2J5UT28",
    "moAx9Nov4HMgFwEYAn8KcyqKU3aCSvCLr4",
    "moBM6io3QKY5XXZAJwV6d9Y5Fcqz5eZRXn",
    "moEoaRkZdKJ8CjyxagF8xMJi9s8gAryH2d",
    "moJbC6oqmAm3BMQHZURrYdrMhzYutAHPHB",
    "moRV6GZV7fNgFrp8jDYL5eF3zTzNuu5Bcn",
    "moT9rQGNHXiFy5oN1p6HPpaEnxwMFEFNse",
    "moV6Ue9prJ2cnjd4ZXg4gUFok6sQ7otChF",
    "moVB6pKHCnzunGKqc7uDL8FkA2LvkMVFRW",
    "moVeuzh4S3PkorokYKnTKGR8h8GpMeoigw",
    "modPeGVDxiFyjpaQpgos6SZDonKypopMoR",
    "moeebhu2TYaCgpxNEEtXonMuA9rvsR6UQu",
    "mokjLYq1fcrZVMSzokXeoeEzz1wdASWDyX",
    "moqL1ubR9uMy3qdZ6ir1PzL8oiCzyfLAPB",
    "mou6B2dWG5bEvkCzqP4S3rUTRiqq9yssHc",
    "mowpqzw2iV1WDtenfSe5YSudJi2mqFE6Vd",
    "mox7oZbBatZFZSxHpiHoGYcUDYSzxoT2UK",
    "mp1QkCC7pmTZNZTiGKzC9EXSmH51UhbXeL",
    "mp25pUPQz6BUfZp8pFNPbAdQ6qhMrLjdEj",
    "mp4d7o5LoEm1qEXBzMQUetS3CWwqVJBpRs",
    "mpA3XCiWd5oKAwLgqF23ZgMcP4rso9EahS",
    "mpALq8fK7QUoAthLMLu2hGfGn1xE6J1853",
    "mpbxgLxHaeDga7z25Fhq24CaHUmamzWdVH",
    "mpmUFRUU9fsYkPcaiMqLoF88f4tmbMMTWw",
    "mpox67CMSdvyynDje2A7ZW7XnA2FWanmyP"]
QUANTITY = 3
AMOUNT = 3
CHANGE_AMOUNT = 2
OVERWRITE_TOLL_FEE = 0.05
TOLL_ASSET_NAME_1 = "NEUBTRINO/TOLL1"
TOLL_ASSET_NAME_2 = "NEUBTRINO/TOLL2"
ISSUE_QUANTITY = 21000000000
ISSUE_TO_ADDRESS = "mvZ1uUzjJHKKaV6Ar9t9yE8MZeMWESip39"
CHANGE_ADDRESS = "myuemRReAq7GbKn52216sxZ5NybQkvF7G2"
ASSET_CHANGE_ADDRESS= "mjNgMNK73yeEwoCK19R6ewwpbTXuERhqpG"
ISSUE_UNITS = 8 # 0 for integers/whole units "1", 8 for max precision "1.00000000"
REISSUABLE = True
HAS_IPFS = False
IPFS_HASH = "QmcUqJaj6QjALDPgwCX14a7bVZDKA954gBptkd699LpLQL"
PERMANENT_IPFS_HASH = "QmcUqJaj6QjALDPgwCX14a7bVZDKA954gBptkd699LpLQL"
TOLL_AMOUNT = 2 # toll to be paid
TOLL_ADDRESS = "n4Vv8eqPi3MV4PzjkaPZCy42dfuTrKwpdQ"  # toll paid to this address
TOLL_AMOUNT_MUTABILITY = True  # can the toll amount be changed in the future?
TOLL_ADDRESS_MUTABILITY = True  # can the toll address be changed in the future?
REMINTABLE = True  # can the asset be reminted if burned?
ROOT_NAME = "NEUBTRINO_IS_DUMB"
ASSET_TAGS_LIST_1 = ["HAWK", "TURTLE", "SCORPION"]
IPFS_HASHES_LIST_1 = ["Qmbaf8G26fzfjNE16jC95UvWDsTUMLWw7oZNySPGgNSwrV", "QmVEFJsRwhGggoJptYtBsAZtAdTjvP3xjswjT1Vf96x68M",
               "QmZEGdYa7MxambTphpABUmzrZVF5KHubGKBj37wMpb2i2w"]
PERMANENT_IPFS_HASH_LIST_1 = ["QmYEr6kpThDYZpFFsN2xx2wkGFNMgvS6L9dK6ZdnvkhdzR",
                              "QmYEr6kpThDYZpFFsN2xx2wkGFNMgvS6L9dK6ZdnvkhdzR",
                              "QmYEr6kpThDYZpFFsN2xx2wkGFNMgvS6L9dK6ZdnvkhdzR"]
ONLYTOTAL = False
COUNT = 30
START = 1
LIST_ASSETS_PARTIAL="NEUB*"
CONFS=1
NEW_IPFS="Qmbaf8G26fzfjNE16jC95UvWDsTUMLWw7oZNySPGgNSwrV"  #  evrmore defi image
PERMANENT_IPFS_HASH = "QmZEGdYa7MxambTphpABUmzrZVF5KHubGKBj37wMpb2i2w"  # evrmore minimal

ASSETS=[
    "NEUBTRINO#evrmore_defi",
    "NEUBTRINO#neubtrino",
    "NEUBTRINO#evrmore_minimal",
    "NEUBTRINO#unique1",
    "NEUBTRINO#unique2",
    "NEUBTRINO#unique3",
    "NEUBTRINO/TOLL2",
    "NEUBTRINO/TOLL1",
    "NEUBTRINO_VPS",
    "NEUBTRINO#002",
    "NEUBTRINO#001",
    "NEUBTRINO"
]
ADDRESSES=[
    "n4iLxDUVRsJrf4824Wdur2nVoZDAtGUtEv",
    "mmMsiTpG6z4LKj7na41fsXV973sGnozFrN",
    "miDaqMHxtJoAPwyLJUxp7wBb8DwJzxZfzX",
    "miJ5ZVrELyozpX2JxwYE7FrjgxfV5KT6ij",
    "miLJPFdNRBTQExRJ9rn6cgVdCe1vUAVw5h",
    "miNCgdGK3512tnunbJvjE1qM41Gv64jfys",
    "miNSDCc7kVGSy3To3bkCKT9NNYvazmDyXV",
    "miP2kWcB4UkMFNfeabwYFB2ap8sRFGawWm",
    "miRxnNdmtJnvQsDJSFpGovb6XvCrp91us9",
    "miUhnDFzW3TNkRAUKDAACc42hzriNabjc8",
    "miVwZWMGrPbFAkqU9M4fTJUy5RABLSMyp5",
    "mifR6xwX8uB9BXHniutgw1jxvUo433Tc7s",
    "mihd8CxxTsTmrMZKvsxBx5q2nPo6AWyk5j",
    "mikishF6qxcW9ghNHBpHNpTECMTMLDwL4j",
    "minyK8wxEGD56EkN6J8kJcs6ijrEjjCzgb",
    "mioT1jDgWBdVU5RgdHQeq9hK8NPaNf9Nzt",
    "mip8rTvahvaZu3zu4EBH8CqLL29jiZaGBk",
    "miqQbzv1qCx28VcaxV7S9NgWoXgVdPTkD8",
    "miqyZtD1xiJU57yoAeBUBPJBQBvtGshZ9L",
    "mj4deTbVz3V751HwBV5QS7hYTft867bf6Z",
    "mj7w8HWGNBBgrEbUosokFEZ5UymUZp2SvY",
    "mjJgyk4WwSRFX1iJkirwHoooKiLnBudr9a",
    "mjJhrQXS7BdeMiREXwjFwFZdiyGfVHFqqm",
    "mjPLUefugwrwsFdPjoDiYwWqt4sTjVuYyP",
    "mjTNzYRuL13CamitkfDXwWdbDARecRXmjT",
    "mjVD4PrctAkeahkbdZVpvxoHcJo6nixZy4",
    "mjZ8xiZ3QSQt3ohQcqxGTmmw7MGW1uqUsi",
    "mjZuA24YpukqWrRq2hWXYg6FYpUkWSQvBW",
    "mjeYKPCe7qy5wJYYrFSEwTzBZ5a5Hmxabg",
    "mjehdFfeUJbxxuR9qc3HTM2ZpdjBtJT3iQ",
    "mjeoQp765Zz3JVcSgGYnqSwzjKneYRcjen",
    "mjj9YjJKi7owLtXfmF6aHyoZfcEssrRmSq",
    "mjsjD3oRdz349smHYgAwGGJVuBnHryCJ8W",
    "mjzXkrUJoUSGr3LcJvzbewMuuAjeYCWeoa",
    "mk9m1sQuYc8NevNTQZ3wYp9XQN8utZCbPf",
    "mkCJtkQ2nh8ihc9kpg9c96LmYCjoHcXNop",
    "mkETprFDaRWMt2oDQr4mUujL2ckTEw91CE",
    "mkHRno9ppEqa4ZWN2xiMEuiX4SAwUVkEqx",
    "mkHwqErfEMqk2ha1313fQcrsZeqpKMZjVd",
    "mkJiEzqDHCDqy6BeNDY2KRHQum4BheqHqR",
    "mkLqdaYbB38MZTSJLHQc3D4gMnDVHgi3wT",
    "mkSQir3RfXHvRpuPCKQL64WxYCQRFzuPvv",
    "mkga2EZzBFvB5yVkyk2Rm6bABmMVWpSRdi",
    "mkh5DNx4c6J1nDCWNghLdDLXkTC9dYzdc4",
    "mknDisb7UFj1np6LKoQT75m2RvjbEvsvM5",
    "mknXbgb5YZZrwLHmmurZ9g2jMwYnso5xC2",
    "mkoGEBn8JW89FZW16c8BVwRUk5Prro871r",
    "mkokEN5EzpEZCdXwDdt7kTSHcKW54YfFDk",
    "mkroteQTFW2cHYa8s68nbXPUo32VtfK6b2",
    "mkx4qcKd1fSZLwMQeszuEdpVSZK8k77z5S",
    "mm3YH7mGPdPav8o2in6mWYKccsbPFhdMfA",
    "mm7BqqZgkSBPkAgTa5UosFVLqbGggSXVKB",
    "mmD7ZNu3F699WJ2yZrw5RXzHsC6uVBo3FL",
    "mmKyzKGx2hFgf8AqydNeo4FjtsbBr5egp4",
    "mmMsiTpG6z4LKj7na41fsXV973sGnozFrN",
    "mmWxeDbLJQZUdpZZPZEXukGj8rVPnuqAid",
    "mmmASH2pqoeHmf66jnnCacZST4cR2JNDP6",
    "mmxKm6qwjRYwcBzThbr3Se49Jk5mieDBxM",
    "mmxkFjsXf21rGiwjxwbyaCySKw2LSGjj9P",
    "mmzVHgDsdYHmNtEp9oV9tsKp67xJNFYyCC",
    "mn1GRhCShB7kquuqWTrqoo2gyzQ6rACZ14",
    "mn8BBeegWf9SxMxoq5sG1LFNxsY9swp88i",
    "mnM1dezz9nN1A6UDPfPH5BwKiqgB4Vx55s",
    "mnQS1mjxbx6P1JBDkrTpin3ZSGYpFKYUNn",
    "mnVm1NR512tEGZBLAwduoS3oqUtCKyS5NY",
    "mnkY7xKHi1CX8YZEARG9dV4ji8n3XAwnSW",
    "mnsJseM6PzuY9UsRgwHCbySH53eTQXGAVe",
    "mnxRHPxfrtZjNbCPiJnGgqjC7TjrG64qPi",
    "mnxpa29tMK1yrZaZYziuLD3oALT5waVjQc",
    "mnzqqto4SSZxLHDjSfigjJWBWPZ5mqqyyv",
    "mo4J9wZR2dy79C6AegY9SvWdmeZ6nGRqfZ",
    "mo5Qgt6fJpY2imPLuu3TRqmtuyRB5F4fsq",
    "mo97DgYCaAwA7Nvt8XrgBrSFqSx2J5UT28",
    "moAx9Nov4HMgFwEYAn8KcyqKU3aCSvCLr4",
    "moBM6io3QKY5XXZAJwV6d9Y5Fcqz5eZRXn",
    "moEoaRkZdKJ8CjyxagF8xMJi9s8gAryH2d",
    "moJbC6oqmAm3BMQHZURrYdrMhzYutAHPHB",
    "moRV6GZV7fNgFrp8jDYL5eF3zTzNuu5Bcn",
    "moT9rQGNHXiFy5oN1p6HPpaEnxwMFEFNse",
    "moV6Ue9prJ2cnjd4ZXg4gUFok6sQ7otChF",
    "moVB6pKHCnzunGKqc7uDL8FkA2LvkMVFRW",
    "moVeuzh4S3PkorokYKnTKGR8h8GpMeoigw",
    "modPeGVDxiFyjpaQpgos6SZDonKypopMoR",
    "moeebhu2TYaCgpxNEEtXonMuA9rvsR6UQu",
    "mokjLYq1fcrZVMSzokXeoeEzz1wdASWDyX",
    "moqL1ubR9uMy3qdZ6ir1PzL8oiCzyfLAPB",
    "mou6B2dWG5bEvkCzqP4S3rUTRiqq9yssHc",
    "mowpqzw2iV1WDtenfSe5YSudJi2mqFE6Vd",
    "mox7oZbBatZFZSxHpiHoGYcUDYSzxoT2UK",
    "mp1QkCC7pmTZNZTiGKzC9EXSmH51UhbXeL",
    "mp25pUPQz6BUfZp8pFNPbAdQ6qhMrLjdEj",
    "mp4d7o5LoEm1qEXBzMQUetS3CWwqVJBpRs",
    "mpA3XCiWd5oKAwLgqF23ZgMcP4rso9EahS",
    "mpALq8fK7QUoAthLMLu2hGfGn1xE6J1853",
    "mpbxgLxHaeDga7z25Fhq24CaHUmamzWdVH",
    "mpmUFRUU9fsYkPcaiMqLoF88f4tmbMMTWw",
    "mpox67CMSdvyynDje2A7ZW7XnA2FWanmyP"
]

RESERVED_NAMES = {
    "EVR", "EVER", "EVRMORE", "EVERMORE.", "EVERMORECOIN", "EVRS", "EVERS", "EVRMORES", "EVERMORES",
    "EVERMORECOINS", "EVRMORECOINS", "RVN", "RAVEN", "RAVENCOIN", "RVNS", "RAVENS", "RAVENCOINS"
}

# === Valid Asset Name Generator ===
def generate_valid_root_asset_name(length=11):
    base_chars = string.ascii_uppercase + string.digits
    name = ''.join(random.choices(base_chars, k=length))

    # 20% chance to include a single underscore not at start/end
    if random.random() < 0.2 and length > 3:
        pos = random.randint(1, length - 2)
        name = name[:pos] + '_' + name[pos+1:]

    return name[:31]  # enforce max length


def test_addresshasasset(assetName, address, min_quantity):



    result = rpc.addresshasasset(
        asset_name=assetName,
        address=address,
        required_quantity=min_quantity
    )

    print(f'\nBOOLEAN RESULT\nAddress: {address}\nhas the required minimum quantity: {min_quantity}\nof asset: {assetName}\n{result}\n')


def test_addresshasasset_paramgrid():
    param_grid = {
        "asset_name": ASSETS,
        "address": ADDRESSES,
        "required_quantity": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }

    for asset_name, address, quantity in product(
        param_grid["asset_name"],
        param_grid["address"],
        param_grid["required_quantity"]
    ):
        try:
            result = rpc.addresshasasset(
                asset_name=asset_name,
                address=address,
                required_quantity=quantity
            )
            print(f"Asset: {asset_name}, Address: {address}, Required: {quantity} -> Has Asset: {result}")
        except Exception as e:
            print(f"Error for Asset: {asset_name}, Address: {address}, Quantity: {quantity} -> {e}")


def test_getassetdata():



    result = rpc.getassetdata(
        asset_name=ASSET_NAME
    )

    print(f"\nAsset Data Info:\n{result}\n")
    print(f'\niterated result')
    for key, value in result.items():
        print(f"{key}: {value}")


def test_getassetdata_paramgrid():

    for asset_name in ASSETS:
        try:
            result = rpc.getassetdata(asset_name=asset_name)
            print(f"Asset: {asset_name} -> Name: {result.get('name', 'N/A')}")
        except Exception as e:
            print(f"Error for Asset: {asset_name} -> {e}")


def test_getburnaddresses():



    result = rpc.getburnaddresses()

    print(f"\nburn addresses:\n{result}")
    print(f'\niterated result')
    for key, value in result.items():
        print(f'{key}: {value}')

def test_getcacheinfo():



    result = rpc.getcacheinfo()

    print(f"\ncache info:\n{result}\n")
    print(f'\niterated result')
    result_length = len(result)
    for i in range(result_length):
        for key, value in result[i].items():
            print(f'{key}: {value}')

def test_getcalculatedtoll():



    result = rpc.getcalculatedtoll(
        asset_name="NEUBTRINO/TOLL1",
        amount=3,
        change_amount=0,
        overwrite_toll_fee=1.25
    )

    print(f'\nCalculated Toll for sending {AMOUNT} of {TOLL_ASSET_NAME_1} is\n')
    print(f'\niterated result')
    for key, value in result.items():
        print(f"{key}: {value}")

def test_getcalculatedtoll_paramgrid():

    param_grid = {
        "asset_name": ASSETS,
        "amount": [1, 2, 5, 10],
        "change_amount": [0, 1, 2, 3, 4, 5],
        "overwrite_toll_fee": [-1, 0.5, 1.0, 1.5, 100]
    }

    for asset_name, amount, change_amount, overwrite_fee in product(
        param_grid["asset_name"],
        param_grid["amount"],
        param_grid["change_amount"],
        param_grid["overwrite_toll_fee"]
    ):
        try:
            result = rpc.getcalculatedtoll(
                asset_name=asset_name,
                amount=amount,
                change_amount=change_amount,
                overwrite_toll_fee=overwrite_fee
            )
            print(f"Toll for {amount} {asset_name} (change={change_amount}, overwrite={overwrite_fee}): {result}")
        except Exception as e:
            print(f"Error for {asset_name}, amount={amount}, change={change_amount}, overwrite={overwrite_fee} -> {e}")

def test_getsnapshot():

    result = rpc.getsnapshot(
        asset_name="NEUBTRINO/TOLL1",
        block_height=1183819
    )

    print(f'snapshot: {result}')

def test_issue(asset, to_address):



    result = rpc.issue(
        asset_name=asset,
        qty=ISSUE_QUANTITY,
        to_address=to_address,
        change_address="moGWRxXk8VESStxj3NH4PoqpNxgpZ9m9Lc",
        units=ISSUE_UNITS,
        reissuable=REISSUABLE,
        has_ipfs=HAS_IPFS,
        ipfs_hash=IPFS_HASH,
        permanent_ipfs_hash=PERMANENT_IPFS_HASH,
        toll_amount=TOLL_AMOUNT,
        toll_address="moGWRxXk8VESStxj3NH4PoqpNxgpZ9m9Lc",
        toll_amount_mutability=TOLL_AMOUNT_MUTABILITY,
        toll_address_mutability=TOLL_ADDRESS_MUTABILITY,
        remintable=REMINTABLE
    )

    print(f"\nTXID for issuing asset {asset}: {result}\n")


def test_issue_paramgrid():
    seen_assets = set()

    ISSUE_QUANTITIES = [1, 2, 3, 4, 5, 6, 7]
    ISSUE_TO_ADDRESSES = FROM_ADDRESSES
    CHANGE_ADDRESSES = TO_ADDRESSES
    ISSUE_UNITS_LIST = [0,1,2,3,4,5,6,7]  # 0 through 8
    REISSUABLE_OPTIONS = [False, True]
    # HAS_IPFS_OPTIONS = [True, False]
    HAS_IPFS_OPTIONS = [False, True]
    IPFS_HASHES = IPFS_HASHES_LIST_1
    PERMANENT_IPFS_HASHES = PERMANENT_IPFS_HASH_LIST_1
    TOLL_AMOUNTS = [1, 2, 3, 4, 5]
    TOLL_ADDRESSES = TO_ADDRESSES
    # TOLL_AMOUNT_MUTABILITIES = [True, False]
    TOLL_AMOUNT_MUTABILITIES = [False, True]
    # TOLL_ADDRESS_MUTABILITIES = [True, False]
    TOLL_ADDRESS_MUTABILITIES = [False, True]
    # REMINTABLE_OPTIONS = [True, False]
    REMINTABLE_OPTIONS = [False, True]

    param_grid = product(
        ISSUE_QUANTITIES,
        ISSUE_TO_ADDRESSES,
        CHANGE_ADDRESSES,
        ISSUE_UNITS_LIST,
        REISSUABLE_OPTIONS,
        HAS_IPFS_OPTIONS,
        IPFS_HASHES,
        PERMANENT_IPFS_HASHES,
        TOLL_AMOUNTS,
        TOLL_ADDRESSES,
        TOLL_AMOUNT_MUTABILITIES,
        TOLL_ADDRESS_MUTABILITIES,
        REMINTABLE_OPTIONS
    )

    for (quantity, to_address, change_address, units, reissuable, has_ipfs, ipfs_hash,
         permanent_ipfs_hash, toll_amount, toll_address, toll_amount_mutability,
         toll_address_mutability, remintable) in param_grid:

        # Generate a new valid, unique asset name
        while True:
            asset = generate_valid_root_asset_name()
            if asset not in seen_assets:
                seen_assets.add(asset)
                break

        try:
            result = rpc.issue(
                asset_name=asset,
                qty=quantity,
                to_address=to_address,
                change_address="mvjxkMUMmAJ6bwvhgY3gGiBTvbRW6V7kYU",
                units=units,
                reissuable=reissuable,
                has_ipfs=has_ipfs,
                ipfs_hash=ipfs_hash,
                permanent_ipfs_hash=permanent_ipfs_hash,
                toll_amount=toll_amount,
                toll_address=toll_address,
                toll_amount_mutability=toll_amount_mutability,
                toll_address_mutability=toll_address_mutability,
                remintable=remintable
            )
            print(f"args for rpc.issue: ",quantity, to_address, change_address, units, reissuable, has_ipfs, ipfs_hash,
         permanent_ipfs_hash, toll_amount, toll_address, toll_amount_mutability,
         toll_address_mutability, remintable)
            print(f"TXID for issuing asset {asset}: {result}\n")
        except Exception as e:
            print(f"\nFailed to issue {asset} with error: {e}")


def test_issueunique(assetTagList1, ipfsHashList1, permIpfsHashList2):


    print(f'address has asset: {test_addresshasasset(assetName="NEUBTRINO_UNIQUE_ADMIN!", address="mxyqbZA6FdS8H2buPF7mkbmhkK9T74RXy2", min_quantity=1)}')

    result = rpc.issueunique(
        root_name=ROOT_NAME,
        asset_tags=assetTagList1,
        ipfs_hashes=ipfsHashList1,
        to_address="moGWRxXk8VESStxj3NH4PoqpNxgpZ9m9Lc",
        change_address="moGWRxXk8VESStxj3NH4PoqpNxgpZ9m9Lc",
        permanent_ipfs_hashes=permIpfsHashList2,
        toll_address="moGWRxXk8VESStxj3NH4PoqpNxgpZ9m9Lc",
        toll_amount=TOLL_AMOUNT,
        toll_amount_mutability=TOLL_AMOUNT_MUTABILITY,
        toll_address_mutability=TOLL_ADDRESS_MUTABILITY
    )

    print(f"\nTXID for issuing unique assets {assetTagList1}: {result}\n")


def test_listaddressesbyasset():
    """
    Test function for the `listaddressesbyasset` method.

    This function calls the `listaddressesbyasset` method with specific parameters to test
    its functionality. It retrieves and prints the result based on the specified asset name,
    `only_total` setting, count limit, and starting index.

    Parameters:
        No parameters are passed directly. The method configurations include:
            - asset_name (str): The name of the asset to query.
                Example values (commented in the code):
                "NEUBTRINO#unique1", "NEUBTRINO_VPS", or "NEUBTRINO/TOLL1".
            - only_total (bool): Whether to return only the total count of addresses
              or the detailed list with balances.
            - count (int): The maximum number of addresses to retrieve.
            - start (int): The starting index for retrieval (default is 0).

    Returns:
        None: This test function prints the result to the console for verification.

    Example:
        Executing this test function might print:
        ```
        result:
        {
            "n1abc...": 34.5,
            "n2xyz...": 12.0
        }
        ```
        Or, if `only_total` is True:
        ```
        result:
        2
        ```
    """


    result = rpc.listaddressesbyasset(
        # asset_name="NEUBTRINO#unique1",
        # asset_name="NEUBTRINO_VPS",
        # asset_name="NEUBTRINO/TOLL1",
        asset_name=ASSET_NAME,
        onlytotal=ONLYTOTAL,
        count=50000,
        start=0
    )

    print(f"\nresult: {result}\n")


def test_listassetbalancesbyaddress():
    """
    Test function for the `listassetbalancesbyaddress` method.

    This function calls the `listassetbalancesbyaddress` method of the `AssetRPC` class
    with specific parameters to verify its functionality. It retrieves asset balances or
    the total count of assets for a given Evrmore address and prints the result.

    Parameters:
        No parameters are passed directly. The function uses predefined test configurations:
            - address: The Evrmore address to query (ISSUE_TO_ADDRESS).
            - onlytotal: A boolean flag indicating whether to fetch only the total count of
                         assets (ONLYTOTAL).
            - count: The maximum number of results to retrieve (COUNT).
            - start: The starting index for the retrieval process (set to 0).

    Returns:
        None: The function outputs the result to the console for validation.

    Example Output:
        If `onlytotal` is False:
        ```
        result:
        {
          "ASSET1": 100.5,
          "ASSET2": 50.0
        }
        ```
        If `onlytotal` is True:
        ```
        result:
        2
        ```
    """


    result = rpc.listassetbalancesbyaddress(
        address=ISSUE_TO_ADDRESS,
        onlytotal=ONLYTOTAL,
        count=COUNT,
        start=0
    )

    print(f"\nresult: {result}\n")


def test_listassets():
    """
    Test function for the `listassets` method.

    This function tests the `listassets` method of the `AssetRPC` class. It retrieves a filtered list
    of assets or detailed metadata based on predefined test parameters. The results are printed for
    validation.

    Parameters:
        None. The function uses predefined test configurations:
            - asset: A partial asset name for filtering (`LIST_ASSETS_PARTIAL`).
            - verbose: Whether to retrieve detailed metadata or just asset names (True).
            - count: The maximum number of results to retrieve (`COUNT`).
            - start: The starting index for the retrieval (`START`).

    Returns:
        None: The function prints the output to the console for review.

    Example Output:
        If `verbose` is False:
        ```
        result: [
          "ASSET1",
          "ASSET2",
          ...
        ]
        ```
        If `verbose` is True:
        ```
        result: {
          "ASSET1": {
            "amount": 1000000,
            "units": 8,
            "reissuable": 1,
            "has_ipfs": 1,
            "ipfs_hash": "Qm123...abc"
          },
          "ASSET2": {
            "amount": 500,
            "units": 0,
            "reissuable": 0,
            "has_ipfs": 0
          },
          ...
        }
        ```
    """


    result = rpc.listassets(
        asset=LIST_ASSETS_PARTIAL,
        verbose=True,
        count=COUNT,
        start=START
    )

    print(f"\nresult: {result}\n")


def test_listmyassets():



    result = rpc.listmyassets(
        asset=LIST_ASSETS_PARTIAL,
        verbose=True,
        count=COUNT,
        start=START,
        confs=CONFS
    )

    print(f"\nresult: {result}\n")

    for key, value in result.items():
        print(f'{key}: {value}')


def test_reissue():
    """
    Tests the `reissue` method of the `AssetRPC` class.

    This function makes a call to the `reissue` RPC command with specific parameters for asset reissuance.
    It verifies that the function properly handles the reissuance and prints the returned transaction ID.

    Parameters:
        None. All required variables (e.g., `ASSET_NAME`, `TO_ADDRESS`, `CHANGE_ADDRESS`, etc.)
        are assumed to be set elsewhere in the associated test environment.

    Returns:
        None. The function prints the reissuance transaction ID to the console.

    Example:
        Assuming all required variables are correctly set:
            >>> test_reissue()
            TXID: <transaction_id>

    Notes:
        - Ensure that `rpc` is initialized properly with necessary credentials and network configurations.
        - The required variables (`ASSET_NAME`, `TO_ADDRESS`, `CHANGE_ADDRESS`, etc.) must be valid for the
          testnet or mainnet environment, depending on the setup.
        - This is a test function and should be run in an isolated test environment to avoid unintended
          consequences in a live system.
    """


    result = rpc.reissue(
        asset_name="NEUBTRINO_DEFI",
        qty=0,
        to_address="myyxSimyWF3cCX3AuLax98rq6bSbHWCmsR",
        change_address="myyxSimyWF3cCX3AuLax98rq6bSbHWCmsR",
        reissuable=True,
        new_units=-1,
        new_ipfs="QmYEr6kpThDYZpFFsN2xx2wkGFNMgvS6L9dK6ZdnvkhdzR",
        new_permanent_ipfs="",
        change_toll_amount=False,
        new_toll_amount=0,
        new_toll_address="myyxSimyWF3cCX3AuLax98rq6bSbHWCmsR",
        toll_amount_mutability=True,
        toll_address_mutability=True

    )

    print(f"\nTXID: {result}\n")


def test_remint():

    result = rpc.remint(
        asset_name="NEUBTRINO_IS_DUMB",
        qty=1,
        to_address="moGWRxXk8VESStxj3NH4PoqpNxgpZ9m9Lc",
        change_address="moGWRxXk8VESStxj3NH4PoqpNxgpZ9m9Lc",
        update_remintable=True
    )

    print(f'\nTXID: {result}\n')


def test_transfer(address):

    result = rpc.transfer(asset_name=ASSET_NAME, qty=QUANTITY, to_address=address, message="", expire_time=0,
                          change_address=CHANGE_ADDRESS, asset_change_address=ISSUE_TO_ADDRESS)

    print(f"\nTXID: {result}\n")


def test_transferfromaddress():
    """
    Tests transferring an asset from one address to another on testnet.

    This test checks:
    - That a command can be built and run successfully
    - That the result is either a TXID or a well-formatted error message

    The test will fail if no Evrmore daemon is running or the config is incorrect.
    """

    result = rpc.transferfromaddress(
        asset_name="NEUBTRINO_IS_DUMB",
        from_address="moGWRxXk8VESStxj3NH4PoqpNxgpZ9m9Lc",
        qty=1,
        to_address="mvhZvFzxaG6fu5DE7q1x7QQTjfR1nZHS1D",
        message=None,  # optional, still allowed
        expire_time=None,  # optional
        evr_change_address="moGWRxXk8VESStxj3NH4PoqpNxgpZ9m9Lc",
        asset_change_address="moGWRxXk8VESStxj3NH4PoqpNxgpZ9m9Lc"
    )

    print(f"\nTXID: {result}\n")


def test_transferfromaddresses(): # is this supposed to transfer qty from each address in FROM_ADDRESSES?

    result = rpc.transferfromaddresses(
        asset_name="NEUBTRINO_IS_DUMB",
        from_addresses=["mvhZvFzxaG6fu5DE7q1x7QQTjfR1nZHS1D", "moGWRxXk8VESStxj3NH4PoqpNxgpZ9m9Lc"],  # list
        # from_addresses=TO_ADDRESSES,
        qty=2,
        to_address="n1BurnXXXXXXXXXXXXXXXXXXXXXXU1qejP",
        message="",
        expire_time=0,
        evr_change_address="moGWRxXk8VESStxj3NH4PoqpNxgpZ9m9Lc",
        asset_change_address="moGWRxXk8VESStxj3NH4PoqpNxgpZ9m9Lc"
    )

    print(f"\nTXID: {result}")


def test_updatemetadata():

    result = rpc.updatemetadata(
        asset_name=ASSET_NAME,
        change_address=CHANGE_ADDRESS,
        ipfs_hash=IPFS_HASH,
        permanent_ipfs="",
        toll_address=TOLL_ADDRESS,
        change_toll_amount=False,
        new_toll_amount=-1,
        toll_amount_mutability=True,
        toll_address_mutability=True
    )

    print(f"\nTXID: {result}\n")


if __name__ == "__main__":
    # test_addresshasasset("NEUBTRINO_RESTRICTED_2!", "n4bpZEyAm2hbhNPoKWicf82C4RX44Ung4Z", 1    )
    # test_getassetdata()
    # test_getburnaddresses()
    # test_getcacheinfo()
    # test_getcalculatedtoll()
    # test_getsnapshot()
    # test_issue(asset="NEUBTRINO_IS_DUMB", to_address="moGWRxXk8VESStxj3NH4PoqpNxgpZ9m9Lc") # be sure to change asset name
    # test_issueunique(ASSET_TAGS_LIST_1, IPFS_HASHES_LIST_1, PERMANENT_IPFS_HASH_LIST_1)
    # test_listaddressesbyasset()
    # test_listassetbalancesbyaddress()
    # test_listassets()
    test_listmyassets()
    # test_reissue()
    # test_remint()
    # test_transferfromaddress()
    # print(f'transferring to TO_ADDRESSES')
    # for address in TO_ADDRESSES:
    #     test_transfer(address)
    # print(f'transferring to FROM_ADDRESSES')
    # for address in FROM_ADDRESSES:
    #     test_transfer(address)
    # test_transferfromaddresses()
    # test_updatemetadata()

    """
    Next are parameter grid implementations of the test functions
    to test them across various iterations of inputs.
    """
    # test_addresshasasset_paramgrid()
    # test_getassetdata_paramgrid()
    # test_getburnaddresses()
    # test_getcacheinfo()
    # test_getcalculatedtoll_paramgrid()
    # test_issue_paramgrid()