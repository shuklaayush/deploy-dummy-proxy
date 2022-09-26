import brownie
import pytest
from brownie import accounts, AdminUpgradeabilityProxy, CallForwarder


@pytest.fixture
def deployer():
    return accounts[0]


@pytest.fixture
def owner():
    return accounts[1]


@pytest.fixture
def proxyAdmin():
    return accounts[2]


@pytest.fixture
def rando():
    return accounts[3]


@pytest.fixture
def logic(deployer):
    yield CallForwarder.deploy({"from": deployer})


@pytest.fixture
def proxy(deployer, logic, owner, proxyAdmin):
    dummy = AdminUpgradeabilityProxy.deploy(
        logic, proxyAdmin, logic.initialize.encode_input(owner), {"from": deployer}
    )
    AdminUpgradeabilityProxy.remove(dummy)
    yield CallForwarder.at(dummy.address)


def test_params(proxy, owner):
    assert proxy.owner() == owner


def test_permissions(proxy, deployer, rando):
    for actor in [deployer, rando]:
        with brownie.reverts("Ownable: caller is not the owner"):
            proxy.doCall(actor, 1e18, "", {"from": actor})

        with brownie.reverts("Ownable: caller is not the owner"):
            proxy.transferOwnership(actor, {"from": actor})


def test_double_initialize(proxy, deployer):
    with brownie.reverts("Initializable: contract is already initialized"):
        proxy.initialize(deployer, {"from": deployer})


def test_transfer_ownership(proxy, owner, rando):
    assert proxy.owner() == owner

    proxy.transferOwnership(rando, {"from": owner})

    assert proxy.owner() == rando


def test_call(proxy, owner, deployer, rando):
    deployer.transfer(proxy, 1e18)

    rando_balance_before = rando.balance()
    proxy.doCall(rando, 1e18, "", {"from": owner})

    assert rando.balance() - rando_balance_before == 1e18
