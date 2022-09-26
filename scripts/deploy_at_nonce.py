from brownie import accounts, chain, AdminUpgradeabilityProxy, CallForwarder

# graviAURA (Mainnet)
TARGET_ADDRESS = "0xBA485b556399123261a5F9c95d413B4f93107407"

DEPLOYER = "0x7c1D678685B9d2F65F1909b9f2E544786807d46C"
TARGET_NONCE = 29

# Badger addresses (Optimism)
TECHOPS = "0x8D05c5DA2a3Cb4BeB4C5EB500EE9e3Aa71670733"
PROXY_ADMIN = "0x52FE2D2332FFCE104959DabF45383c6F25c3C21b"


def main():
    deployer = accounts.at(DEPLOYER, force=True)
    accounts.default = deployer

    # Deployer has balance to do txs
    assert deployer.balance() > 0.1e18

    # At least two nonces, one for logic and one for proxy 
    assert deployer.nonce + 1 < TARGET_NONCE

    logic = CallForwarder.deploy(publish_source=False)

    while deployer.nonce < TARGET_NONCE:
        deployer.transfer(deployer, 0)

    assert deployer.nonce == TARGET_NONCE

    dummy_proxy = AdminUpgradeabilityProxy.deploy(
        logic, PROXY_ADMIN, logic.initialize.encode_input(TECHOPS), publish_source=False
    )

    assert dummy_proxy == TARGET_ADDRESS
