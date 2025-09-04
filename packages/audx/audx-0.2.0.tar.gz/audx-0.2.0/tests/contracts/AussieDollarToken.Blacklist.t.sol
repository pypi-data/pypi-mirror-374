// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {AussieDollarTokenBase} from "./AussieDollarTokenBase.t.sol";

contract AussieDollarTokenBlacklistTest is AussieDollarTokenBase {
    // ============ Blacklist Tests ============

    function test_AddToBlacklist() public {
        vm.prank(blacklister);
        token.addToBlacklist(blacklistedUser);
        assertTrue(token.isBlacklisted(blacklistedUser));
    }

    function test_RemoveFromBlacklist() public {
        vm.prank(blacklister);
        token.addToBlacklist(blacklistedUser);
        assertTrue(token.isBlacklisted(blacklistedUser));

        vm.prank(blacklister);
        token.removeFromBlacklist(blacklistedUser);
        assertFalse(token.isBlacklisted(blacklistedUser));
    }

    function test_OnlyBlacklisterCanManageBlacklist() public {
        vm.prank(user1);
        vm.expectRevert();
        token.addToBlacklist(user2);

        vm.prank(user1);
        vm.expectRevert();
        token.removeFromBlacklist(user2);
    }

    function test_BlacklistedCannotTransfer() public {
        // Mint tokens to treasurer and transfer to user
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        vm.prank(treasurer1);
        token.transfer(user1, 500 * 10 ** 18);

        // Blacklist user1 and try to transfer
        vm.prank(blacklister);
        token.addToBlacklist(user1);

        vm.prank(user1);
        vm.expectRevert("Sender is blacklisted");
        token.transfer(user2, 100 * 10 ** 18);
    }

    function test_CannotTransferToBlacklisted() public {
        // Mint tokens to treasurer
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        // Blacklist user2
        vm.prank(blacklister);
        token.addToBlacklist(user2);

        // Try to transfer to blacklisted user
        vm.prank(treasurer1);
        vm.expectRevert("Recipient is blacklisted");
        token.transfer(user2, 100 * 10 ** 18);
    }

    // ============ Force Transfer Tests ============

    function test_ForceTransferFromBlacklisted() public {
        // Setup: Give tokens to user, then blacklist them
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        vm.prank(treasurer1);
        token.transfer(user1, 500 * 10 ** 18);

        vm.prank(blacklister);
        token.addToBlacklist(user1);

        // Force transfer from blacklisted to treasurer
        uint256 amount = 500 * 10 ** 18;
        vm.prank(salvager);
        token.forceTransfer(user1, treasurer2, amount);

        assertEq(token.balanceOf(user1), 0);
        assertEq(token.balanceOf(treasurer2), amount);
    }

    function test_CannotForceTransferFromNonBlacklisted() public {
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        vm.prank(salvager);
        vm.expectRevert("Sender must be blacklisted");
        token.forceTransfer(treasurer1, treasurer2, 100 * 10 ** 18);
    }

    function test_CannotForceTransferToNonTreasurer() public {
        // Setup blacklisted user with tokens
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);
        vm.prank(treasurer1);
        token.transfer(user1, 500 * 10 ** 18);
        vm.prank(blacklister);
        token.addToBlacklist(user1);

        vm.prank(salvager);
        vm.expectRevert("Recipient not a treasurer");
        token.forceTransfer(user1, user2, 100 * 10 ** 18);
    }

    function test_OnlySalvagerCanForceTransfer() public {
        // Setup blacklisted user with tokens
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);
        vm.prank(treasurer1);
        token.transfer(user1, 500 * 10 ** 18);
        vm.prank(blacklister);
        token.addToBlacklist(user1);

        vm.prank(user2);
        vm.expectRevert();
        token.forceTransfer(user1, treasurer2, 100 * 10 ** 18);
    }
}
