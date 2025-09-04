from pydantic import BaseModel

from deep_apply import apply


def my_func(value: str, **_kwargs):
    return value.upper()


tuple_test: tuple[str, str] = ("John Doe", "Jane Doe")


def test_tuple():
    data = tuple_test
    data = apply(
        data=data,
        func=my_func,
    )

    assert data[0] == "JOHN DOE" and data[1] == "JANE DOE"


##########


def test_tuple_in_pydantic():
    class Person(BaseModel):
        nicknames: tuple[str, str]

    person = Person(nicknames=("Johnnie", "Jo"))

    data = person
    data = apply(
        data=data,
        func=my_func,
    )

    assert data.nicknames[0] == "JOHNNIE" and data.nicknames[1] == "JO"


def test_tuple_in_dict():
    data = {"person": tuple_test}
    data = apply(
        data=data,
        func=my_func,
    )

    assert data["person"][0] == "JOHN DOE" and data["person"][1] == "JANE DOE"


def test_tuple_in_list():
    data = [tuple_test]
    data = apply(
        data=data,
        func=my_func,
    )

    assert data[0][0] == "JOHN DOE" and data[0][1] == "JANE DOE"


def test_tuple_in_tuple():
    data = (tuple_test, "dummy_data")
    data = apply(
        data=data,
        func=my_func,
    )

    assert data[0][0] == "JOHN DOE" and data[0][1] == "JANE DOE"
