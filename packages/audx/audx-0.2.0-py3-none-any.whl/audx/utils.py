from eth_utils import keccak


def keccak_subtract(text: str, n: int = 1) -> str:
    return hex(int(keccak(text=text).hex(), 16) - n)
