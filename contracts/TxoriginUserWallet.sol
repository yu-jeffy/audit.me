// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.9;

contract TxoriginUserWallet {
    address owner;

    constructor() payable 
	{
        owner = msg.sender;
    }

	receive() external payable {}  // collect ether

    function withdrawAll(address payable _to) public 
	{
        require(tx.origin == owner);

        (bool sent, ) = _to.call{value: address(this).balance}("");
        require(sent, "Failed to send Ether");
    }
}