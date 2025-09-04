from pydantic import BaseModel

from deep_apply import apply


def my_func(value: str, **_kwargs):
    return value.upper()


def test_not_allow_dict():
    data = {"first_name": "John", "last_name": "Doe"}
    data = apply(data=data, func=my_func, allowed_types=[])

    assert data["first_name"] == "John" and data["last_name"] == "Doe"


def test_not_allow_list():
    data = ["John Doe"]
    data = apply(data=data, func=my_func, allowed_types=[])

    assert data[0] == "John Doe"


def test_not_allow_set():
    data = {"John Doe"}
    data = apply(data=data, func=my_func, allowed_types=[])

    assert data.pop() == "John Doe"


def test_not_allow_tuple():
    data = ("John Doe", "Jane Doe")
    data = apply(data=data, func=my_func, allowed_types=[])

    assert data[0] == "John Doe"


def test_not_allow_pydantic():
    class Person(BaseModel):
        first_name: str
        last_name: str

    data = Person(first_name="John", last_name="Doe")
    data = apply(data=data, func=my_func, allowed_types=[])

    assert data.first_name == "John" and data.last_name == "Doe"
