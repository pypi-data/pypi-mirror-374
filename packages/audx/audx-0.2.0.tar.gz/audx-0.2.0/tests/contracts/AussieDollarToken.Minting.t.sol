// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {AussieDollarTokenBase} from "./AussieDollarTokenBase.t.sol";

contract AussieDollarTokenMintingTest is AussieDollarTokenBase {
    // ============ Treasurer Management Tests ============

    function test_AddTreasurer() public {
        address newTreasurer = makeAddr("newTreasurer");

        vm.prank(admin);
        token.addTreasurer(newTreasurer);
        assertTrue(token.isTreasurer(newTreasurer));
    }

    function test_RemoveTreasurer() public {
        vm.prank(admin);
        token.removeTreasurer(treasurer1);
        assertFalse(token.isTreasurer(treasurer1));
    }

    function test_OnlyAdminCanManageTreasurers() public {
        address newTreasurer = makeAddr("newTreasurer");

        vm.prank(user1);
        vm.expectRevert();
        token.addTreasurer(newTreasurer);

        vm.prank(user1);
        vm.expectRevert();
        token.removeTreasurer(treasurer1);
    }

    // ============ Minting Tests ============

    function test_MintToTreasurer() public {
        uint256 amount = 1000 * 10 ** 18;

        vm.prank(minter);
        vm.expectEmit(true, true, false, true);
        emit Transfer(address(0), treasurer1, amount);
        token.mint(treasurer1, amount);

        assertEq(token.balanceOf(treasurer1), amount);
        assertEq(token.totalSupply(), amount);
    }

    function test_CannotMintToNonTreasurer() public {
        uint256 amount = 1000 * 10 ** 18;

        vm.prank(minter);
        vm.expectRevert("Recipient not a treasurer");
        token.mint(user1, amount);
    }

    function test_OnlyMinterCanMint() public {
        uint256 amount = 1000 * 10 ** 18;

        vm.prank(user1);
        vm.expectRevert();
        token.mint(treasurer1, amount);
    }

    function testFuzz_MintAmount(uint256 amount) public {
        vm.assume(amount > 0 && amount < type(uint256).max / 2);

        vm.prank(minter);
        token.mint(treasurer1, amount);
        assertEq(token.balanceOf(treasurer1), amount);
    }

    function test_MintingBlockedWhenPaused() public {
        vm.prank(pauser);
        token.pause();

        vm.prank(minter);
        vm.expectRevert();
        token.mint(treasurer1, 100 * 10 ** 18);
    }
}
