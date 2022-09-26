// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;

import "openzeppelin-contracts-upgradeable/access/OwnableUpgradeable.sol";

contract CallForwarder is OwnableUpgradeable {
    ////////////////////////////////////////////////////////////////////////////
    // INITIALIZATION
    ////////////////////////////////////////////////////////////////////////////

    function initialize(address _owner) public initializer {
        __Ownable_init();

        transferOwnership(_owner);
    }

    ////////////////////////////////////////////////////////////////////////////
    // PUBLIC: Owner
    ////////////////////////////////////////////////////////////////////////////

    function doCall(address to, uint256 value, bytes memory data)
        public
        payable
        virtual
        onlyOwner
        returns (bool success)
    {
        success = execute(to, value, data, gasleft());
    }

    function execute(
        address to,
        uint256 value,
        bytes memory data,
        uint256 txGas
    ) internal returns (bool success) {
        assembly {
            success := call(txGas, to, value, add(data, 0x20), mload(data), 0, 0)
        }
    }

    receive() external payable {}
}