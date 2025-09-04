// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {AussieDollarTokenBase} from "./AussieDollarTokenBase.t.sol";

contract AussieDollarTokenPausableTest is AussieDollarTokenBase {
    // ============ Pausable Tests ============

    function test_Pause() public {
        vm.prank(pauser);
        vm.expectEmit(true, false, false, false);
        emit Paused(pauser);
        token.pause();

        assertTrue(token.paused());
    }

    function test_Unpause() public {
        vm.prank(pauser);
        token.pause();
        assertTrue(token.paused());

        vm.prank(pauser);
        vm.expectEmit(true, false, false, false);
        emit Unpaused(pauser);
        token.unpause();

        assertFalse(token.paused());
    }

    function test_OnlyPauserCanPause() public {
        vm.prank(user1);
        vm.expectRevert();
        token.pause();

        vm.prank(user1);
        vm.expectRevert();
        token.unpause();
    }

    function test_TransfersBlockedWhenPaused() public {
        // Setup tokens
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        // Pause contract
        vm.prank(pauser);
        token.pause();

        // Try to transfer
        vm.prank(treasurer1);
        vm.expectRevert();
        token.transfer(user1, 100 * 10 ** 18);
    }

    function test_TransferFromBlockedWhenPaused() public {
        // Setup tokens and approval
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        vm.prank(treasurer1);
        token.approve(user1, 500 * 10 ** 18);

        // Pause contract
        vm.prank(pauser);
        token.pause();

        // Try to transferFrom
        vm.prank(user1);
        vm.expectRevert();
        token.transferFrom(treasurer1, user2, 100 * 10 ** 18);
    }

    function test_BurnBlockedWhenPaused() public {
        // Setup tokens
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        // Pause contract
        vm.prank(pauser);
        token.pause();

        // Try to burn
        vm.prank(treasurer1);
        vm.expectRevert();
        token.burn(100 * 10 ** 18);
    }

    function test_BurnFromBlockedWhenPaused() public {
        // Setup tokens and approval
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        vm.prank(treasurer1);
        token.approve(user1, 500 * 10 ** 18);

        // Pause contract
        vm.prank(pauser);
        token.pause();

        // Try to burnFrom
        vm.prank(user1);
        vm.expectRevert();
        token.burnFrom(treasurer1, 100 * 10 ** 18);
    }

    function test_ForceTransferBlockedWhenPaused() public {
        // Setup: Give tokens to user, then blacklist them
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        vm.prank(treasurer1);
        token.transfer(user1, 500 * 10 ** 18);

        vm.prank(blacklister);
        token.addToBlacklist(user1);

        // Pause the contract
        vm.prank(pauser);
        token.pause();

        // Force transfer should also be blocked when paused
        vm.prank(salvager);
        vm.expectRevert();
        token.forceTransfer(user1, treasurer2, 500 * 10 ** 18);
    }
}
