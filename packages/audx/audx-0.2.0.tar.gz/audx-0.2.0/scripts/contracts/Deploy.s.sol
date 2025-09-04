pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import {AussieDollarToken} from "src/contracts/AussieDollarToken.sol";
import {ERC1967Proxy} from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

contract Deploy is Script {
    function run() external {
        address admin = vm.addr(vm.envUint("FORGE_DEPLOY_PRIVATE_KEY"));

        vm.startBroadcast();

        // Deploy implementation
        AussieDollarToken implementation = new AussieDollarToken();

        // Deploy proxy with initialization
        bytes memory initData = abi.encodeCall(AussieDollarToken.initialize, (admin, admin, admin, admin, admin, admin));

        ERC1967Proxy proxy = new ERC1967Proxy(address(implementation), initData);

        console.log("Proxy:", address(proxy));
        console.log("Implementation:", address(implementation));

        vm.stopBroadcast();
    }
}
