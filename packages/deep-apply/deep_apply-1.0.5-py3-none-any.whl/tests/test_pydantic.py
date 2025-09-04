from pydantic import BaseModel

from deep_apply import apply


def my_func(value: str, **_kwargs):
    return value.upper()


class Person(BaseModel):
    first_name: str
    last_name: str


class Child(Person):
    pass


class Parent(Person):
    child: Child = Child(first_name="Jane", last_name="Doe")


parent = Parent(first_name="John", last_name="Doe")


def test_pydantic():
    data = parent
    data = apply(
        data=data,
        func=my_func,
    )

    assert data.first_name == "JOHN" and data.last_name == "DOE"


##########


def test_pydantic_in_pydantic():
    data = parent
    data = apply(
        data=data,
        func=my_func,
    )

    assert data.child.first_name == "JANE" and data.child.last_name == "DOE"


def test_pydantic_in_dict():
    data = {"person": parent}
    data = apply(
        data=data,
        func=my_func,
    )

    assert data["person"].first_name == "JOHN" and data["person"].last_name == "DOE"


def test_pydantic_in_list():
    data = [parent]
    data = apply(
        data=data,
        func=my_func,
    )

    assert data[0].first_name == "JOHN" and data[0].last_name == "DOE"


def test_pydantic_in_tuple():
    data = (parent, "dummy_data")
    data = apply(
        data=data,
        func=my_func,
    )

    assert data[0].first_name == "JOHN" and data[0].last_name == "DOE"
