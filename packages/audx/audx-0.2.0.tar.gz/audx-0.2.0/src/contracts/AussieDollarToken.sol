// SPDX-License-Identifier: MIT
// Compatible with OpenZeppelin Contracts ^5.0.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20BurnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20PermitUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";

contract AussieDollarToken is
    Initializable,
    ERC20Upgradeable,
    ERC20BurnableUpgradeable,
    ERC20PausableUpgradeable,
    AccessControlUpgradeable,
    ERC20PermitUpgradeable,
    UUPSUpgradeable
{
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant UPGRADER_ROLE = keccak256("UPGRADER_ROLE");
    bytes32 public constant BLACKLISTER_ROLE = keccak256("BLACKLISTER_ROLE");
    bytes32 public constant SALVAGER_ROLE = keccak256("SALVAGER_ROLE");
    mapping(address => bool) private _treasurers;
    mapping(address => bool) private _blacklist;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(
        address defaultAdmin,
        address pauser,
        address minter,
        address upgrader,
        address blacklister,
        address salvager
    ) public initializer {
        __ERC20_init("Aussie Dollar Token", "AUDX");
        __ERC20Burnable_init();
        __ERC20Pausable_init();
        __AccessControl_init();
        __ERC20Permit_init("Aussie Dollar Token");
        __UUPSUpgradeable_init();

        _grantRole(DEFAULT_ADMIN_ROLE, defaultAdmin);
        _grantRole(PAUSER_ROLE, pauser);
        _grantRole(MINTER_ROLE, minter);
        _grantRole(UPGRADER_ROLE, upgrader);
        _grantRole(BLACKLISTER_ROLE, blacklister);
        _grantRole(SALVAGER_ROLE, salvager);
    }

    function pause() public onlyRole(PAUSER_ROLE) {
        _pause();
    }

    function unpause() public onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    function addTreasurer(address account) public onlyRole(DEFAULT_ADMIN_ROLE) {
        _treasurers[account] = true;
    }

    function removeTreasurer(address account) public onlyRole(DEFAULT_ADMIN_ROLE) {
        _treasurers[account] = false;
    }

    function isTreasurer(address account) public view returns (bool) {
        return _treasurers[account];
    }

    function mint(address to, uint256 amount) public onlyRole(MINTER_ROLE) {
        require(_treasurers[to], "Recipient not a treasurer");
        _mint(to, amount);
    }

    function addToBlacklist(address account) public onlyRole(BLACKLISTER_ROLE) {
        _blacklist[account] = true;
    }

    function removeFromBlacklist(address account) public onlyRole(BLACKLISTER_ROLE) {
        _blacklist[account] = false;
    }

    function isBlacklisted(address account) public view returns (bool) {
        return _blacklist[account];
    }

    function forceTransfer(address from, address to, uint256 amount) public onlyRole(SALVAGER_ROLE) {
        require(_blacklist[from], "Sender must be blacklisted");
        require(_treasurers[to], "Recipient not a treasurer");
        super._update(from, to, amount);
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyRole(UPGRADER_ROLE) {}

    // The following functions are overrides required by Solidity.

    function _update(address from, address to, uint256 value)
        internal
        override(ERC20Upgradeable, ERC20PausableUpgradeable)
    {
        require(!_blacklist[from], "Sender is blacklisted");
        require(!_blacklist[to], "Recipient is blacklisted");
        super._update(from, to, value);
    }
}
