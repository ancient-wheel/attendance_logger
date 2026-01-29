from attendance_logger.services.contracts import generate_contract_number


def test_generate_contract_number() -> None:
    current_year = dt.date.today().year
    year, token = generate_contract_number().split("/")
    assert str(current_year) == year
    assert len(token) == 8


def test_generate_contract_number_user_defined() -> None:
    user_defined = "asdf298ijlnasdhfoe"
    contract = generate_contract_number(user_defined=user_defined)
    assert user_defined == contract
