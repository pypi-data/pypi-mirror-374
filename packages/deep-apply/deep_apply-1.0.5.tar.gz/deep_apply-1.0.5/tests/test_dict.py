from pydantic import BaseModel

from deep_apply import apply


def my_func(value: str, **_kwargs):
    return value.upper()


dict_test = {"first_name": "John", "last_name": "Doe"}


def test_dict():
    data = dict_test
    data = apply(
        data=data,
        func=my_func,
    )

    assert data["first_name"] == "JOHN" and data["last_name"] == "DOE"


##########


def test_dict_in_pydantic():
    class Person(BaseModel):
        nickname: dict[str, str]

    person = Person(nickname={"nickname": "Johnnie"})

    data = person
    data = apply(
        data=data,
        func=my_func,
    )

    assert data.nickname["nickname"] == "JOHNNIE"


def test_dict_in_dict():
    data = {"person": dict_test}
    data = apply(
        data=data,
        func=my_func,
    )

    assert (
        data["person"]["first_name"] == "JOHN" and data["person"]["last_name"] == "DOE"
    )


def test_dict_in_list():
    data = [dict_test]
    data = apply(
        data=data,
        func=my_func,
    )

    assert data[0]["first_name"] == "JOHN" and data[0]["last_name"] == "DOE"


def test_dict_in_tuple():
    data = (dict_test, "dummy_data")
    data = apply(
        data=data,
        func=my_func,
    )

    assert data[0]["first_name"] == "JOHN" and data[0]["last_name"] == "DOE"
