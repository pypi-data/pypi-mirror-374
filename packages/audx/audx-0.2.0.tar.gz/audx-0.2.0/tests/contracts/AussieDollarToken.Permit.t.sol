// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {AussieDollarTokenBase} from "./AussieDollarTokenBase.t.sol";
import {AussieDollarToken} from "../../src/contracts/AussieDollarToken.sol";

contract AussieDollarTokenPermitTest is AussieDollarTokenBase {
    // ============ ERC20Permit Tests ============

    function test_Permit() public {
        uint256 privateKey = 0xBEEF;
        address owner = vm.addr(privateKey);

        // Setup tokens for owner
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);
        vm.prank(treasurer1);
        token.transfer(owner, 500 * 10 ** 18);

        // Create permit signature
        uint256 nonce = token.nonces(owner);
        uint256 deadline = block.timestamp + 1 hours;
        uint256 amount = 100 * 10 ** 18;

        bytes32 structHash = keccak256(
            abi.encode(
                keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"),
                owner,
                user1,
                amount,
                nonce,
                deadline
            )
        );

        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", token.DOMAIN_SEPARATOR(), structHash));

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(privateKey, digest);

        // Execute permit
        token.permit(owner, user1, amount, deadline, v, r, s);

        assertEq(token.allowance(owner, user1), amount);
        assertEq(token.nonces(owner), nonce + 1);
    }

    function test_PermitExpired() public {
        uint256 privateKey = 0xBEEF;
        address owner = vm.addr(privateKey);

        uint256 deadline = block.timestamp - 1; // Expired deadline

        bytes32 structHash = keccak256(
            abi.encode(
                keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"),
                owner,
                user1,
                100 * 10 ** 18,
                0,
                deadline
            )
        );

        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", token.DOMAIN_SEPARATOR(), structHash));

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(privateKey, digest);

        vm.expectRevert();
        token.permit(owner, user1, 100 * 10 ** 18, deadline, v, r, s);
    }

    function test_PermitInvalidSignature() public {
        uint256 privateKey = 0xBEEF;
        address owner = vm.addr(privateKey);
        uint256 wrongKey = 0xDEAD;

        uint256 deadline = block.timestamp + 1 hours;

        bytes32 structHash = keccak256(
            abi.encode(
                keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"),
                owner,
                user1,
                100 * 10 ** 18,
                0,
                deadline
            )
        );

        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", token.DOMAIN_SEPARATOR(), structHash));

        // Sign with wrong key
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(wrongKey, digest);

        vm.expectRevert();
        token.permit(owner, user1, 100 * 10 ** 18, deadline, v, r, s);
    }

    function test_PermitReplayProtection() public {
        uint256 privateKey = 0xBEEF;
        address owner = vm.addr(privateKey);

        // Setup tokens for owner
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);
        vm.prank(treasurer1);
        token.transfer(owner, 500 * 10 ** 18);

        // Create permit signature
        uint256 nonce = token.nonces(owner);
        uint256 deadline = block.timestamp + 1 hours;
        uint256 amount = 100 * 10 ** 18;

        bytes32 structHash = keccak256(
            abi.encode(
                keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"),
                owner,
                user1,
                amount,
                nonce,
                deadline
            )
        );

        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", token.DOMAIN_SEPARATOR(), structHash));

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(privateKey, digest);

        // Execute permit once
        token.permit(owner, user1, amount, deadline, v, r, s);

        // Try to replay the same permit
        vm.expectRevert();
        token.permit(owner, user1, amount, deadline, v, r, s);
    }

    // ============ Upgrade Tests ============

    function test_UpgradeToNewImplementation() public {
        // Deploy new implementation (same contract for testing)
        AussieDollarToken newImplementation = new AussieDollarToken();

        // Store state before upgrade
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);
        uint256 balanceBefore = token.balanceOf(treasurer1);

        // Upgrade
        vm.prank(upgrader);
        token.upgradeToAndCall(address(newImplementation), "");

        // Verify state preserved
        assertEq(token.balanceOf(treasurer1), balanceBefore);
        assertEq(token.name(), "Aussie Dollar Token");
        assertTrue(token.hasRole(MINTER_ROLE, minter));
    }

    function test_OnlyUpgraderCanUpgrade() public {
        AussieDollarToken newImplementation = new AussieDollarToken();

        vm.prank(user1);
        vm.expectRevert();
        token.upgradeToAndCall(address(newImplementation), "");
    }

    function test_UpgradeWithInitializationData() public {
        // Deploy new implementation
        AussieDollarToken newImplementation = new AussieDollarToken();

        // Store state before upgrade
        vm.prank(minter);
        token.mint(treasurer1, 1000 * 10 ** 18);

        // Prepare initialization data (empty in this case, but could be used for migrations)
        bytes memory initData = "";

        // Upgrade
        vm.prank(upgrader);
        token.upgradeToAndCall(address(newImplementation), initData);

        // Verify upgrade succeeded
        assertEq(token.balanceOf(treasurer1), 1000 * 10 ** 18);
    }

    function test_CannotUpgradeToZeroAddress() public {
        vm.prank(upgrader);
        vm.expectRevert();
        token.upgradeToAndCall(address(0), "");
    }

    function test_CannotUpgradeToNonContract() public {
        address nonContract = makeAddr("nonContract");

        vm.prank(upgrader);
        vm.expectRevert();
        token.upgradeToAndCall(nonContract, "");
    }
}
