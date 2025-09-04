// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {AussieDollarTokenBase} from "./AussieDollarTokenBase.t.sol";
import {IERC20Errors} from "@openzeppelin/contracts/interfaces/draft-IERC6093.sol";

contract AussieDollarTokenERC20Test is AussieDollarTokenBase {
    // ============ ERC20 Standard Tests ============

    function test_Transfer() public {
        // Setup
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        // Transfer
        vm.prank(treasurer1);
        vm.expectEmit(true, true, false, true);
        emit Transfer(treasurer1, user1, 100 * 10 ** 18);
        token.transfer(user1, 100 * 10 ** 18);

        assertEq(token.balanceOf(treasurer1), 900 * 10 ** 18);
        assertEq(token.balanceOf(user1), 100 * 10 ** 18);
    }

    function test_TransferFrom() public {
        // Setup
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        // Approve
        vm.prank(treasurer1);
        token.approve(user1, 200 * 10 ** 18);

        // TransferFrom
        vm.prank(user1);
        token.transferFrom(treasurer1, user2, 150 * 10 ** 18);

        assertEq(token.balanceOf(treasurer1), 850 * 10 ** 18);
        assertEq(token.balanceOf(user2), 150 * 10 ** 18);
        assertEq(token.allowance(treasurer1, user1), 50 * 10 ** 18);
    }

    function test_Approve() public {
        vm.prank(user1);
        vm.expectEmit(true, true, false, true);
        emit Approval(user1, user2, 100 * 10 ** 18);
        token.approve(user2, 100 * 10 ** 18);

        assertEq(token.allowance(user1, user2), 100 * 10 ** 18);
    }

    function test_Burn() public {
        // Setup
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        // Burn
        vm.prank(treasurer1);
        token.burn(200 * 10 ** 18);

        assertEq(token.balanceOf(treasurer1), 800 * 10 ** 18);
        assertEq(token.totalSupply(), 800 * 10 ** 18);
    }

    function test_BurnFrom() public {
        // Setup
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        // Approve for burning
        vm.prank(treasurer1);
        token.approve(user1, 300 * 10 ** 18);

        // BurnFrom
        vm.prank(user1);
        token.burnFrom(treasurer1, 200 * 10 ** 18);

        assertEq(token.balanceOf(treasurer1), 800 * 10 ** 18);
        assertEq(token.totalSupply(), 800 * 10 ** 18);
        assertEq(token.allowance(treasurer1, user1), 100 * 10 ** 18);
    }

    function test_TransferInsufficientBalance() public {
        vm.prank(minter);
        token.mint(treasurer1, 100 * 10 ** 18);

        vm.prank(treasurer1);
        vm.expectRevert(
            abi.encodeWithSelector(
                IERC20Errors.ERC20InsufficientBalance.selector, treasurer1, 100 * 10 ** 18, 200 * 10 ** 18
            )
        );
        token.transfer(user1, 200 * 10 ** 18);
    }

    function test_TransferFromInsufficientAllowance() public {
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        vm.prank(treasurer1);
        token.approve(user1, 100 * 10 ** 18);

        vm.prank(user1);
        vm.expectRevert(
            abi.encodeWithSelector(
                IERC20Errors.ERC20InsufficientAllowance.selector, user1, 100 * 10 ** 18, 200 * 10 ** 18
            )
        );
        token.transferFrom(treasurer1, user2, 200 * 10 ** 18);
    }

    function test_TransferToZeroAddress() public {
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        vm.prank(treasurer1);
        vm.expectRevert(abi.encodeWithSelector(IERC20Errors.ERC20InvalidReceiver.selector, address(0)));
        token.transfer(address(0), 100 * 10 ** 18);
    }

    function test_TransferFromZeroAddress() public {
        // This should not be possible in normal flow, but testing for completeness
        vm.prank(user1);
        vm.expectRevert();
        token.transferFrom(address(0), user2, 100 * 10 ** 18);
    }

    function test_ApproveToZeroAddress() public {
        vm.prank(user1);
        vm.expectRevert(abi.encodeWithSelector(IERC20Errors.ERC20InvalidSpender.selector, address(0)));
        token.approve(address(0), 100 * 10 ** 18);
    }

    function testFuzz_Transfer(uint256 amount) public {
        vm.assume(amount > 0 && amount <= 1000 * 10 ** 18);

        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        vm.prank(treasurer1);
        token.transfer(user1, amount);

        assertEq(token.balanceOf(treasurer1), 1000 * 10 ** 18 - amount);
        assertEq(token.balanceOf(user1), amount);
    }

    function testFuzz_Approve(uint256 amount) public {
        vm.assume(amount < type(uint256).max);

        vm.prank(user1);
        token.approve(user2, amount);
        assertEq(token.allowance(user1, user2), amount);
    }
}
