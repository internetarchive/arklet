import secrets


def generate_noid(length: int) -> str:
    betanumeric = "0123456789bcdfghjkmnpqrstvwxz"
    return "".join(secrets.choice(betanumeric) for _ in range(length))


def parse_ark(ark: str) -> (str, int, str):
    parts = ark.split("ark:/")
    if len(parts) != 2:
        raise ValueError("Not a valid ARK")
    nma, ark = parts
    parts = ark.split("/")
    if len(parts) < 2:
        raise ValueError("Not a valid ARK")
    naan, assigned_name = parts[:2]
    try:
        naan = int(naan)
    except ValueError:
        raise ValueError("ARK NAAN must be an integer")

    return nma, naan, assigned_name
