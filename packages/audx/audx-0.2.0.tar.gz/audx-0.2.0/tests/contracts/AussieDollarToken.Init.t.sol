// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {AussieDollarTokenBase} from "./AussieDollarTokenBase.t.sol";
import {IAccessControl} from "@openzeppelin/contracts/access/IAccessControl.sol";

contract AussieDollarTokenInitTest is AussieDollarTokenBase {
    // ============ Initialization Tests ============

    function test_Initialization() public view {
        assertEq(token.name(), "Aussie Dollar Token");
        assertEq(token.symbol(), "AUDX");
        assertEq(token.decimals(), 18);
        assertEq(token.totalSupply(), 0);
    }

    function test_RolesAssignment() public view {
        assertTrue(token.hasRole(DEFAULT_ADMIN_ROLE, admin));
        assertTrue(token.hasRole(PAUSER_ROLE, pauser));
        assertTrue(token.hasRole(MINTER_ROLE, minter));
        assertTrue(token.hasRole(UPGRADER_ROLE, upgrader));
        assertTrue(token.hasRole(BLACKLISTER_ROLE, blacklister));
        assertTrue(token.hasRole(SALVAGER_ROLE, salvager));
    }

    function test_CannotInitializeTwice() public {
        vm.expectRevert();
        token.initialize(admin, pauser, minter, upgrader, blacklister, salvager);
    }

    function test_ImplementationInitializersDisabled() public {
        vm.expectRevert();
        implementation.initialize(admin, pauser, minter, upgrader, blacklister, salvager);
    }

    // ============ Access Control Tests ============

    function test_OnlyAdminCanGrantRoles() public {
        address newMinter = makeAddr("newMinter");

        vm.prank(admin);
        token.grantRole(MINTER_ROLE, newMinter);
        assertTrue(token.hasRole(MINTER_ROLE, newMinter));

        bytes32 adminRole = token.getRoleAdmin(MINTER_ROLE);
        vm.prank(user1);
        vm.expectRevert(
            abi.encodeWithSelector(IAccessControl.AccessControlUnauthorizedAccount.selector, user1, adminRole)
        );
        token.grantRole(MINTER_ROLE, user2);
    }

    function test_OnlyAdminCanRevokeRoles() public {
        vm.prank(admin);
        token.revokeRole(MINTER_ROLE, minter);
        assertFalse(token.hasRole(MINTER_ROLE, minter));

        // Add minter back and try with non-admin
        vm.prank(admin);
        token.grantRole(MINTER_ROLE, minter);

        bytes32 adminRole = token.getRoleAdmin(MINTER_ROLE);
        vm.prank(user1);
        vm.expectRevert(
            abi.encodeWithSelector(IAccessControl.AccessControlUnauthorizedAccount.selector, user1, adminRole)
        );
        token.revokeRole(MINTER_ROLE, minter);
    }

    function test_ComplexPermissionScenario() public {
        // Grant multiple roles to one account
        vm.startPrank(admin);
        token.grantRole(MINTER_ROLE, admin);
        token.grantRole(PAUSER_ROLE, admin);
        vm.stopPrank();

        // Admin can now mint and pause
        vm.startPrank(admin);
        token.mint(treasurer1, 1000 * 10 ** 18);
        token.pause();
        vm.stopPrank();

        // Verify paused state blocks transfers
        vm.prank(treasurer1);
        vm.expectRevert();
        token.transfer(user1, 100 * 10 ** 18);

        // Unpause and continue
        vm.prank(admin);
        token.unpause();

        vm.prank(treasurer1);
        token.transfer(user1, 100 * 10 ** 18);
        assertEq(token.balanceOf(user1), 100 * 10 ** 18);
    }
}
