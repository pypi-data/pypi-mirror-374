import asyncio
from pathlib import Path
from typing import cast

from eth_typing import ChecksumAddress
from web3 import AsyncWeb3
from web3 import Web3

from audx import AUDX
from audx.abi import LocalABILoader
from audx.asyncio import AUDX as AsyncAUDX

REPO_ROOT = Path(__file__).parent.parent

PROXY_ADDRESS: ChecksumAddress = cast(
    "ChecksumAddress", "0x15bb7be7EBFd940b2A967cd3E746d9f088dD0fc2"
)

DEMO_ACCOUNTS = {
    "0": {
        "address": "0x36b802dA36c793521FB97Dc3a6b2F02456F6184C",
        "private_key": "0xfb483faf3693ba0270f7f7f77dc25204ee6eca2fc619144b716d270ec35c45d2",
    },
    "1": {
        "address": "0x7417B50b0Ca1E127a2D3078D319A9c5aF1a1438d",
        "private_key": "0x7bad1633a889d0d9dc869b7c01f9d800c4ca9bb28901a395512fa8f111ac6f75",
    },
    "2": {
        "address": "0x2c0c83948515Abcbf22D8Dd371c6B2bdd27Bb149",
        "private_key": "0xbcbfd89b606ec825cb042f8a1dabe822697f11cd65f104b47c9e0972dcac5c73",
    },
    "3": {
        "address": "0x461D5dF7b354DBd55abFDB62cD36B17A7A712da2",
        "private_key": "0x2e65ba99e5fa3802b9763f2ad80a899c54c34a20eb818d5c625ff5e82d343737",
    },
}


def main():
    w3 = Web3(provider=Web3.HTTPProvider())
    w3.eth.default_account = DEMO_ACCOUNTS["1"]["address"]
    audx = AUDX(abi_loader=LocalABILoader(), w3=w3, address=PROXY_ADDRESS)

    # print(audx.abi)
    print(audx.treasurer.add_treasurer(DEMO_ACCOUNTS["2"]["address"]))
    print(audx.treasurer.is_treasurer(DEMO_ACCOUNTS["3"]["address"]))


async def async_demo():
    w3 = AsyncWeb3(provider=AsyncWeb3.AsyncHTTPProvider())
    w3.eth.default_account = DEMO_ACCOUNTS["1"]["address"]
    audx = AsyncAUDX(abi_loader=LocalABILoader(), w3=w3, address=PROXY_ADDRESS)

    result = await audx.treasurer.add_treasurer(DEMO_ACCOUNTS["2"]["address"])
    print(result)


if __name__ == "__main__":
    asyncio.run(async_demo())

    # main()
