from pydantic import BaseModel

from deep_apply import apply


def my_func(value: str, **_kwargs):
    return value.upper()


set_test: set[str] = {"John Doe"}


def test_set():
    data = set_test
    data = apply(
        data=data,
        func=my_func,
    )

    assert data.pop() == "JOHN DOE"


##########


def test_set_in_pydantic():
    class Person(BaseModel):
        nicknames: set[str]

    pydantic = Person(nicknames={"Johnnie"})

    data = pydantic
    data = apply(
        data=data,
        func=my_func,
    )

    assert data.nicknames.pop() == "JOHNNIE"


def test_set_in_dict():
    data = {"person": set_test}
    data = apply(
        data=data,
        func=my_func,
    )

    assert data["person"].pop() == "JOHN DOE"


def test_set_in_list():
    data = [set_test]
    data = apply(
        data=data,
        func=my_func,
    )

    assert data[0].pop() == "JOHN DOE"


def test_set_in_tuple():
    data = (set_test, "dummy_data")
    data = apply(
        data=data,
        func=my_func,
    )

    assert data[0].pop() == "JOHN DOE"
