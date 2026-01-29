import secrets
import datetime as dt


def generate_contract_number(user_defined: str = "") -> str:
    """Generate a contract number

    The results start always with a year followed by slash and a unique combination
    of 8 ASCII digits.

    Keyword arguments:
    user_defined: str - user defined contract_number

    Return: str - unique contract number
    """
    if len(user_defined) > 0:
        return user_defined
    year = dt.datetime.today().year
    token = secrets.token_hex(4)
    return f"{year}/{token}"
