from eth_typing import ABI
from eth_typing import ChecksumAddress
from eth_typing import HexAddress
from web3 import Web3
from web3.exceptions import ContractCustomError
from web3.exceptions import ContractLogicError

from audx.abi import ABILoader
from audx.errors import AUDXError
from audx.errors import build_error_map
from audx.errors import decode_custom_error


class AUDX:
    def __init__(
        self,
        abi_loader: ABILoader,
        w3: Web3,
        address: ChecksumAddress,
    ):
        self.abi_loader = abi_loader
        self.w3 = w3
        self.address = address
        self._abi = None
        self._contract = None
        self._error_map = None

        self.treasurer = AUDXTreasurer(self)
        self.pauser = AUDXPauser(self)
        self.salvager = AUDXSalvager(self)
        self.minter = AUDXMinter(self)
        self.blacklister = AUDXBlacklister(self)
        self.access_control = AUDXAccessControl(self)
        self.erc20 = AUDXERC20(self)

    @property
    def abi(self) -> ABI:
        if self._abi is None:
            self._abi = self.abi_loader.load()
        return self._abi

    @property
    def contract(self):
        if self._contract is None:
            self._contract = self.w3.eth.contract(address=self.address, abi=self.abi)
        return self._contract

    @property
    def error_map(self):
        if self._error_map is None:
            self._error_map = build_error_map(self.abi)
        return self._error_map

    def call(self, func_name: str, transact: bool, *args):
        func = getattr(self.contract.functions, func_name)
        try:
            if transact:
                return func(*args).transact()

            return func(*args).call()
        except ContractCustomError as e:
            # Decode custom error from ABI
            error_msg = decode_custom_error(e, self.error_map)
            # TODO: Specific AUDX errors
            raise AUDXError(error_msg) from e

        except ContractLogicError as e:
            raise AUDXError(e) from e

        except Exception as e:
            # Catch any other exceptions and wrap them
            raise AUDXError(f"Unexpected error calling {func_name}: {e}") from e


class AUDXTreasurer:
    def __init__(self, client: AUDX):
        self.client = client

    def is_treasurer(self, account: str):
        return self.client.call("isTreasurer", False, account)

    def add_treasurer(self, account: str):
        return self.client.call("addTreasurer", True, account)

    def remove_treasurer(self, account: str):
        return self.client.call("removeTreasurer", True, account)


class AUDXPauser:
    def __init__(self, client: AUDX):
        self.client = client

    def pause(self):
        return self.client.call("pause", True)

    def unpause(self):
        return self.client.call("unpause", True)


class AUDXSalvager:
    def __init__(self, client: AUDX):
        self.client = client

    def force_transfer(self, from_: HexAddress, to_: HexAddress, amount: int):
        return self.client.call("forceTransfer", True, from_, to_, amount)


class AUDXMinter:
    def __init__(self, client: AUDX):
        self.client = client

    def mint(self, amount: int):
        return self.client.call("mint", True, amount)


class AUDXBlacklister:
    def __init__(self, client: AUDX):
        self.client = client

    def is_blacklisted(self, account: str):
        return self.client.call("isBlacklisted", False, account)

    def add_to_blacklist(self, account: str):
        return self.client.call("addToBlacklist", True, account)

    def remove_from_blacklist(self, account: str):
        return self.client.call("removeFromBlacklist", True, account)


class AUDXAccessControl:
    def __init__(self, client: AUDX):
        self.client = client

    def has_role(self, role: str, account: ChecksumAddress):
        return self.client.call("hasRole", False, role, account)

    def grant_role(self, role: str, account: ChecksumAddress):
        return self.client.call("grantRole", True, role, account)

    def revoke_role(self, role: str, account: ChecksumAddress):
        return self.client.call("revokeRole", True, role, account)


class AUDXERC20:
    def __init__(self, client: AUDX):
        self.client = client

    def has_role(self, role: str, account: ChecksumAddress):
        return self.client.call("hasRole", False, role, account)

    def grant_role(self, role: str, account: ChecksumAddress):
        return self.client.call("grantRole", True, role, account)

    def revoke_role(self, role: str, account: ChecksumAddress):
        return self.client.call("revokeRole", True, role, account)
