"""
ABI loader for AUDX smart contracts.

Supports loading ABI from:
1. Local JSON files
2. Etherscan API (using implementation address from proxy)
"""

import json
from pathlib import Path
from typing import Protocol

from eth_typing import ABI

DEFAULT_ABI_PATH = Path(__file__).parent / "abi.json"


class ABILoader(Protocol):
    """Protocol for ABI loading implementations."""

    def load(self) -> ABI:
        """Load the contract ABI"""
        ...


class LocalABILoader(ABILoader):
    """Load ABI from local JSON files."""

    def __init__(self, abi_file: Path = DEFAULT_ABI_PATH):
        """Initialize local ABI loader.

        Args:
            abi_file: Path to the abi json file.
        """
        self.abi_file = abi_file

    def load(
        self,
    ) -> ABI:
        """Load ABI from local file."""
        return json.load(self.abi_file.open("r"))
