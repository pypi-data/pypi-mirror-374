from pydantic import BaseModel

from deep_apply import apply


def my_func(value: str, **_kwargs):
    return value.upper()


list_test = ["John Doe"]


def test_list():
    data = list_test
    data = apply(
        data=data,
        func=my_func,
    )

    assert data[0] == "JOHN DOE"


##########


def test_list_in_pydantic():
    class Person(BaseModel):
        nicknames: list[str]

    person = Person(nicknames=["Johnnie", "Jo"])

    data = person
    data = apply(
        data=data,
        func=my_func,
    )

    assert data.nicknames[0] == "JOHNNIE" and data.nicknames[1] == "JO"


def test_list_in_dict():
    data = {"person": list_test}
    data = apply(
        data=data,
        func=my_func,
    )

    assert data["person"][0] == "JOHN DOE"


def test_list_in_list():
    data = [list_test]
    data = apply(
        data=data,
        func=my_func,
    )

    assert data[0][0] == "JOHN DOE"


def test_list_in_tuple():
    data = (list_test, "dummy_data")
    data = apply(
        data=data,
        func=my_func,
    )

    assert data[0][0] == "JOHN DOE"
