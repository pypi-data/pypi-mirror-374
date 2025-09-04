from web3 import Web3
from web3.exceptions import ContractCustomError

from audx.constants import ROLES_MAP


class AUDXError(Exception):
    """Base exception for AUDX SDK errors."""


class InvalidAddressError(AUDXError):
    """Raised when an invalid Ethereum address is provided."""


class InvalidAmountError(AUDXError):
    """Raised when an invalid amount is provided."""


class NoPrivateKeyError(AUDXError):
    """Raised when a transaction method is called without a private key."""


class BlacklistError(AUDXError):
    """Raised when a blacklisted address attempts a transaction."""


class TreasurerError(AUDXError):
    """Raised when treasurer requirements are not met."""


class AccessControlError(AUDXError):
    """Raised when role requirements are not met."""


class ContractPausedError(AUDXError):
    """Raised when contract is paused."""


def build_error_map(abi):
    error_map = {}
    for item in abi:
        if item["type"] == "error":
            # Calculate selector for this error
            params = ",".join([p["type"] for p in item.get("inputs", [])])
            signature = f"{item['name']}({params})"
            calc_selector = "0x" + Web3.keccak(text=signature).hex()[:8]
            error_map[calc_selector] = (item["name"], item.get("inputs", []))
    return error_map


def decode_custom_error(err: ContractCustomError, errors_map):
    """Decode custom errors with enhanced formatting"""
    error_data = err.message
    selector = error_data[:10]

    if selector in errors_map:
        error_name, inputs = errors_map[selector]

        if error_name == "AccessControlUnauthorizedAccount":
            # Special handling for access control errors
            encoded_params = error_data[10:]
            account = "0x" + encoded_params[24:64]  # Extract address
            role_bytes = "0x" + encoded_params[64:128]  # Extract role

            role_name = ROLES_MAP.get(
                role_bytes, f"Unknown Role ({role_bytes[:10]}...)"
            )
            return f"Access Denied: Account {account} lacks required role: {role_name}"

        # Generic parameter decoding for other errors
        if inputs:
            encoded_params = error_data[10:]
            params = {}
            for i, param in enumerate(inputs):
                start = i * 64
                end = start + 64
                param_hex = encoded_params[start:end]

                if param["type"] == "address":
                    value = "0x" + param_hex[-40:]
                elif param["type"] == "bytes32":
                    value = "0x" + param_hex
                    # Check if it's a known role
                    if param["name"] == "neededRole" and value in ROLES_MAP:
                        value = ROLES_MAP[value]
                else:
                    value = int(param_hex, 16)

                params[param["name"]] = value

            # Format parameters nicely
            param_str = ", ".join([f"{k}={v}" for k, v in params.items()])
            return f"{error_name}({param_str})"

        return error_name

    return f"Unknown error: {selector}"
