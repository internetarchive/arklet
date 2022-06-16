from typing import Tuple

import secrets

BETANUMERIC = "0123456789bcdfghjkmnpqrstvwxz"


def noid_check_digit(noid: str) -> str:
    """Calculate the check digit for an ARK.

    See: https://metacpan.org/dist/Noid/view/noid#NOID-CHECK-DIGIT-ALGORITHM
    """
    total = 0
    for pos, char in enumerate(noid, start=1):
        score = BETANUMERIC.find(char)
        if score > 0:
            total += pos * score
    remainder = total % 29  # 29 == len(BETANUMERIC)
    return BETANUMERIC[remainder]  # IndexError may be long ARK


def generate_noid(length: int) -> str:
    return "".join(secrets.choice(BETANUMERIC) for _ in range(length))


def parse_ark(ark: str) -> Tuple[str, int, str]:
    parts = ark.split("ark:")
    if len(parts) != 2:
        raise ValueError("Not a valid ARK")
    nma, ark = parts
    ark = ark.lstrip("/")
    parts = ark.split("/")
    if len(parts) < 2:
        raise ValueError("Not a valid ARK")
    # TODO: assigned_name definition here conflicts with models.Ark.assigned_name
    # parse_ark here doesn't attempt to parse out the shoulder of the ARK.
    naan, assigned_name = parts[:2]
    try:
        naan_int = int(naan)
    except ValueError:
        raise ValueError("ARK NAAN must be an integer")

    return nma, naan_int, assigned_name
