// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console} from "forge-std/Test.sol";
import {AussieDollarToken} from "../../src/contracts/AussieDollarToken.sol";
import {ERC1967Proxy} from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

abstract contract AussieDollarTokenBase is Test {
    AussieDollarToken public implementation;
    AussieDollarToken public token;
    ERC1967Proxy public proxy;

    // Test accounts
    address public admin = makeAddr("admin");
    address public pauser = makeAddr("pauser");
    address public minter = makeAddr("minter");
    address public upgrader = makeAddr("upgrader");
    address public blacklister = makeAddr("blacklister");
    address public salvager = makeAddr("salvager");
    address public treasurer1 = makeAddr("treasurer1");
    address public treasurer2 = makeAddr("treasurer2");
    address public user1 = makeAddr("user1");
    address public user2 = makeAddr("user2");
    address public blacklistedUser = makeAddr("blacklistedUser");

    // Role constants (cached to avoid proxy call issues with vm.prank)
    bytes32 public DEFAULT_ADMIN_ROLE;
    bytes32 public PAUSER_ROLE;
    bytes32 public MINTER_ROLE;
    bytes32 public UPGRADER_ROLE;
    bytes32 public BLACKLISTER_ROLE;
    bytes32 public SALVAGER_ROLE;

    // Events
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event RoleGranted(bytes32 indexed role, address indexed account, address indexed sender);
    event RoleRevoked(bytes32 indexed role, address indexed account, address indexed sender);
    event Paused(address account);
    event Unpaused(address account);

    function setUp() public virtual {
        // Deploy implementation
        implementation = new AussieDollarToken();

        // Deploy proxy with initialization
        bytes memory initData =
            abi.encodeCall(AussieDollarToken.initialize, (admin, pauser, minter, upgrader, blacklister, salvager));

        proxy = new ERC1967Proxy(address(implementation), initData);

        // Cast proxy to AussieDollarToken interface
        token = AussieDollarToken(address(proxy));

        // Cache role constants to avoid proxy call issues with vm.prank
        DEFAULT_ADMIN_ROLE = token.DEFAULT_ADMIN_ROLE();
        PAUSER_ROLE = token.PAUSER_ROLE();
        MINTER_ROLE = token.MINTER_ROLE();
        UPGRADER_ROLE = token.UPGRADER_ROLE();
        BLACKLISTER_ROLE = token.BLACKLISTER_ROLE();
        SALVAGER_ROLE = token.SALVAGER_ROLE();

        // Setup initial state
        vm.startPrank(admin);
        token.addTreasurer(treasurer1);
        token.addTreasurer(treasurer2);
        vm.stopPrank();

        // Fund test accounts with ETH for gas
        vm.deal(admin, 100 ether);
        vm.deal(minter, 100 ether);
        vm.deal(user1, 100 ether);
        vm.deal(user2, 100 ether);
    }
}
