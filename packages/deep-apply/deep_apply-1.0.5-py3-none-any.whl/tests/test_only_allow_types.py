from pydantic import BaseModel

from deep_apply import apply


def my_func(value: str, **_kwargs):
    return value.upper()


def test_only_allow_dict():
    data = {"first_name": "John", "last_name": "Doe"}
    data = apply(data=data, func=my_func, allowed_types=["dict"])

    assert data["first_name"] == "JOHN" and data["last_name"] == "DOE"


def test_only_allow_list():
    data = ["John Doe"]
    data = apply(data=data, func=my_func, allowed_types=["list"])

    assert data[0] == "JOHN DOE"


def test_only_allow_set():
    data = {"John Doe"}
    data = apply(data=data, func=my_func, allowed_types=["set"])

    assert data.pop() == "JOHN DOE"


def test_only_allow_tuple():
    data = ("John Doe", "Jane Doe")
    data = apply(data=data, func=my_func, allowed_types=["tuple"])

    assert data[0] == "JOHN DOE"


def test_only_allow_pydantic():
    class Person(BaseModel):
        first_name: str
        last_name: str

    data = Person(first_name="John", last_name="Doe")
    data = apply(data=data, func=my_func, allowed_types=["pydantic"])

    assert data.first_name == "JOHN" and data.last_name == "DOE"
