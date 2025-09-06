from hashlib import sha256
from typing import Final, Literal


ALGO_SHA256: Final = "sha256"  # only sensible way to make mypy happy
ALGO_LIST: Final[list[Literal["sha256"]]] = [ALGO_SHA256]


def get_checksum(
        data: bytes,
        *,
        algo: Literal["sha256"] = ALGO_SHA256,
        ) -> str:
    """
    Calculates the hash of a byte string and returns it (with an algorithm id).
    
    Currently only sha256 is supported.
    """
    return f"sha256:{sha256(data).hexdigest()}"


def verify_checksum(
        data: bytes,
        hash: str,
        ) -> bool:
    """
    Verifies that the hash of a byte string agrees with a given value.
    
    The hash is always prefixed with an algorith id.
    Currently only sha256 is supported.
    """
    for algo in ALGO_LIST:
        if hash.startswith(f"{algo}:"):
            ref = get_checksum(data, algo=algo)
            return hash == ref
    return False
