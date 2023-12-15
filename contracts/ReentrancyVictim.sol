// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.9;

contract ReentrancyVictim {

    mapping(address => uint) public balances;

    function addBalance() public payable 
	{
        balances[msg.sender] += msg.value;
    }

    function withdraw() public 
	{
        require(balances[msg.sender] > 0);
        (bool sent, ) = msg.sender.call{value: balances[msg.sender]}("");
        require(sent, "Failed to send ether");
        balances[msg.sender] = 0;
    }
}