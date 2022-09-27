import requests
from brownie import accounts, Contract, AdminUpgradeabilityProxy, CallForwarder, web3

# graviAURA strategy (Mainnet)
TARGET_ADDRESS = "0x3c0989eF27e3e3fAb87a2d7C38B35880C90E63b5"

DEPLOYER = "0x7c1D678685B9d2F65F1909b9f2E544786807d46C"
TARGET_NONCE = 34

# Badger addresses (Optimism)
TECHOPS = "0x8D05c5DA2a3Cb4BeB4C5EB500EE9e3Aa71670733"
PROXY_ADMIN = "0x52FE2D2332FFCE104959DabF45383c6F25c3C21b"

LOGIC = "0x584b4489A357615d181e16CE3cbC50cBE5a94FF7"
HIDDEN_HAND_DISTRIBUTOR = "0x0b139682D5C9Df3e735063f46Fb98c689540Cf3A"


def get_hh_data():
    data = requests.get(f"https://hhand.xyz/reward/10/{TARGET_ADDRESS}")
    data = data.json()["data"]

    return [
        (
            item["claimMetadata"]["identifier"],
            item["claimMetadata"]["account"],
            item["claimMetadata"]["amount"],
            item["claimMetadata"]["merkleProof"],
        )
        for item in data
    ]


def main():
    deployer = accounts.at(DEPLOYER, force=True)
    accounts.default = deployer

    # Deployer has balance to do txs
    assert deployer.balance() > 0.1e18

    # At least two nonces, one for logic and one for proxy
    assert deployer.nonce < TARGET_NONCE

    logic = CallForwarder.at(LOGIC)

    while deployer.nonce < TARGET_NONCE:
        deployer.transfer(deployer, 0)

    assert deployer.nonce == TARGET_NONCE

    dummy_proxy = AdminUpgradeabilityProxy.deploy(
        logic, PROXY_ADMIN, logic.initialize.encode_input(TECHOPS), publish_source=False
    )

    print("-" * 80)
    print(f"Proxy address: {dummy_proxy}")
    print("-" * 80)

    assert dummy_proxy == TARGET_ADDRESS

    assert dummy_proxy.balance() == 0

    distributor = Contract(HIDDEN_HAND_DISTRIBUTOR)
    data = get_hh_data()
    tx = distributor.claim(data)

    print(tx.events)
    print(dummy_proxy.balance())

    assert dummy_proxy.balance() > 0