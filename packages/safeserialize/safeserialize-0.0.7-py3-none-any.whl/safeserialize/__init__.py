from .core import (
    dump, load,
    dumps, loads,
    dump_base64, load_base64,
    Serializer, Deserializer,
    write, read,
)

from . import types

# Import all type modules to register their readers and writers
from .types import (
    numpy,
    scipy,
    pandas,
    torch,
    pytz,
)
from .types.stdlib import (
    datetime,
    decimal,
    fractions,
    uuid,
    pathlib,
    collections,
)
