pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import {AussieDollarToken} from "src/contracts/AussieDollarToken.sol";
import {ERC1967Proxy} from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

/**
 * @title DeployDeterministic
 * @notice Deploys AUDX contracts deterministically using CREATE2
 * @dev Addresses will be the same across all EVM chains when using the same deployer and salt
 */
contract DeployDeterministic is Script {
    // Salt for deterministic deployment (change this to get different addresses)
    bytes32 public constant SALT = keccak256("AUDX_V1_2025");

    // Separate salts for implementation and proxy
    bytes32 public constant IMPLEMENTATION_SALT = keccak256(abi.encodePacked(SALT, "implementation"));
    bytes32 public constant PROXY_SALT = keccak256(abi.encodePacked(SALT, "proxy"));

    struct DeploymentAddresses {
        address implementation;
        address proxy;
        address admin;
        address deployer;
    }

    function run() external returns (DeploymentAddresses memory) {
        // Get admin from environment
        uint256 deployerPrivateKey = vm.envUint("FORGE_DEPLOY_PRIVATE_KEY");
        address admin = vm.addr(deployerPrivateKey);

        console.log("=== Starting AUDX Deterministic Deployment ===");
        console.log("Admin/Deployer:", admin);
        console.log("Salt:", uint256(SALT));

        // Predict addresses before deployment
        DeploymentAddresses memory predicted = predictAddresses(admin);
        console.log("\n=== Predicted Addresses ===");
        console.log("Implementation:", predicted.implementation);
        console.log("Proxy:", predicted.proxy);

        vm.startBroadcast(deployerPrivateKey);

        // Deploy implementation using CREATE2
        AussieDollarToken implementation = new AussieDollarToken{salt: IMPLEMENTATION_SALT}();
        console.log("Implementation deployed at:", address(implementation));
        require(address(implementation) == predicted.implementation, "Implementation address mismatch");

        // Prepare initialization data
        bytes memory initData = abi.encodeCall(AussieDollarToken.initialize, (admin, admin, admin, admin, admin, admin));

        // Deploy proxy using CREATE2
        ERC1967Proxy proxy = new ERC1967Proxy{salt: PROXY_SALT}(address(implementation), initData);
        console.log("Proxy deployed at:", address(proxy));
        require(address(proxy) == predicted.proxy, "Proxy address mismatch");

        vm.stopBroadcast();

        // Verify deployment
        DeploymentAddresses memory deployed = DeploymentAddresses({
            implementation: address(implementation),
            proxy: address(proxy),
            admin: admin,
            deployer: admin
        });

        console.log("\n=== Deployment Complete ===");
        console.log("Implementation:", deployed.implementation);
        console.log("Proxy:", deployed.proxy);
        console.log("Admin:", deployed.admin);

        // Verify the proxy is initialized correctly
        AussieDollarToken audx = AussieDollarToken(address(proxy));
        console.log("Token Name:", audx.name());
        console.log("Token Symbol:", audx.symbol());

        return deployed;
    }

    /**
     * @notice Predicts the deployment addresses without deploying
     * @param deployer The address that will deploy the contracts
     */
    function predictAddresses(address deployer) public pure returns (DeploymentAddresses memory) {
        // Predict implementation address
        bytes memory implBytecode = type(AussieDollarToken).creationCode;
        address predictedImpl = computeCreate2Address(deployer, IMPLEMENTATION_SALT, keccak256(implBytecode));

        // For proxy, we need to include constructor args in the bytecode
        // Note: This prediction assumes we know the implementation address
        bytes memory initData =
            abi.encodeCall(AussieDollarToken.initialize, (deployer, deployer, deployer, deployer, deployer, deployer));

        bytes memory proxyBytecode =
            abi.encodePacked(type(ERC1967Proxy).creationCode, abi.encode(predictedImpl, initData));

        address predictedProxy = computeCreate2Address(deployer, PROXY_SALT, keccak256(proxyBytecode));

        return DeploymentAddresses({
            implementation: predictedImpl,
            proxy: predictedProxy,
            admin: deployer,
            deployer: deployer
        });
    }

    /**
     * @notice Computes CREATE2 address using Foundry's Create2Deployer
     * @param deployer The address deploying the contract (not used in Foundry's case)
     * @param salt The salt to use
     * @param bytecodeHash The keccak256 hash of the creation bytecode
     * @dev Foundry uses its own Create2Deployer at 0x4e59b44847b379578588920cA78FbF26c0B4956C
     */
    function computeCreate2Address(address deployer, bytes32 salt, bytes32 bytecodeHash)
        internal
        pure
        returns (address)
    {
        // When using forge script with CREATE2, it uses the canonical Create2Deployer
        address create2Deployer = 0x4e59b44847b379578588920cA78FbF26c0B4956C;

        return address(uint160(uint256(keccak256(abi.encodePacked(bytes1(0xff), create2Deployer, salt, bytecodeHash)))));
    }

    /**
     * @notice Dry run to show what addresses will be deployed
     * @dev Run with: forge script scripts/contracts/DeployDeterministic.s.sol:DeployDeterministic --sig "dryRun()"
     */
    function dryRun() external view {
        uint256 deployerPrivateKey = vm.envOr("FORGE_DEPLOY_PRIVATE_KEY", uint256(1));
        address deployer = vm.addr(deployerPrivateKey);

        DeploymentAddresses memory addresses = predictAddresses(deployer);

        console.log("=== DRY RUN - Predicted Addresses ===");
        console.log("Deployer:", addresses.deployer);
        console.log("Salt:", uint256(SALT));
        console.log("Implementation Salt:", uint256(IMPLEMENTATION_SALT));
        console.log("Proxy Salt:", uint256(PROXY_SALT));
        console.log("Admin:", addresses.admin);
        console.log("Implementation:", addresses.implementation);
        console.log("Proxy:", addresses.proxy);
        console.log("\nThese addresses will be the same on all EVM chains");
        console.log("when deployed from the same account with the same salt");
    }
}
