# Deep Apply

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/deep-apply?color=blue)](https://pypi.python.org/pypi/deep-apply)
[![PyPI](https://img.shields.io/pypi/v/deep-apply?color=blue)](https://pypi.python.org/pypi/deep-apply)
[![PyPI - License](https://img.shields.io/pypi/l/deep-apply)](https://pypi.python.org/pypi/deep-apply)

[![tests](https://github.com/zaironjacobs/deep-apply/actions/workflows/test.yml/badge.svg)](https://github.com/zaironjacobs/deep-apply/actions/workflows/test.yml)

Deep traverse through an object and apply a function on its values.

Supports the following object types:

* Dictionaries
* Lists
* Sets
* Tuples
* Pydantic models

### Install

```bash
pip install deep-apply
```

### Usage

#### Apply upper() on values

```python
import deep_apply


# 1. Create your callback function.
def to_upper(value, **kwargs):
    """
    To uppercase.
    """

    # Other arguments passed to the callback function:
    # key: str = kwargs["key"]
    # depth_level: int = kwargs["depth_level"]
    # depth_key: str = kwargs["depth_key"]

    # Apply upper() and return the value
    if isinstance(value, str):
        return value.upper()
    
    # Always return the unedited value
    return value


# 2. Your data.
data = [
    {
        "id": "pZnZMffPCpJx",
        "name": "John Doe",
        "hobbies": {
            "sport": ["football", "tennis"],
            "music": ["singing", "guitar", "piano"],
        },
    }
]

# 3. Run apply().
data = deep_apply.apply(data=data, func=to_upper)
```

```console
[
    {
        'id': 'PZNZMFFPCPJX',
        'name': 'JOHN DOE',
        'hobbies': {
            'sport': ['FOOTBALL', 'TENNIS'],
            'music': ['SINGING', 'GUITAR', 'PIANO']
        }
    }
]
```
