from safeserialize import dump, load, dumps, loads, dump_base64, load_base64
from safeserialize.core import num_bytes_signed_int

import tempfile

def test_num_bytes_signed_int():
    assert num_bytes_signed_int(1) == 1
    assert num_bytes_signed_int(-1) == 1
    assert num_bytes_signed_int(127) == 1
    assert num_bytes_signed_int(-128) == 1
    assert num_bytes_signed_int(128) == 2
    assert num_bytes_signed_int(-129) == 2
    assert num_bytes_signed_int(32767) == 2
    assert num_bytes_signed_int(32768) == 3
    assert num_bytes_signed_int(-32768) == 2
    assert num_bytes_signed_int(-32769) == 3
    assert num_bytes_signed_int(2147483647) == 4
    assert num_bytes_signed_int(-2147483648) == 4

def test_builtins():
    for x in range(-300, 300):
        data = dumps(x)
        y = loads(data)

        assert x == y, f"{x} != {y}"

    data = {
        1: [1, 2.0, 3, float("inf"), float("-inf")],
        3: [4, 5, 6],
        (1, 2): 3,
        frozenset([7, "foo", 9]): 4,
        123456789: 1 << 256,
        b"key": bytearray(b"value"),
        "float": 3.14159265358979323846,
        "true": True,
        "None": None,
        "list": [[], [[[]], []], [], [[], [[[]]]]],
        "set": {True, False, None, 1, 2, 3},
        "complex": 1 + 2j,
        "range": range(2, 10, -1),
        "slice": slice(None, 0.5, 123),
        "ellipsis": Ellipsis,
        "NotImplemented": NotImplemented,
    }

    serialized = dumps(data)

    deserialized = loads(serialized)

    assert data == deserialized, f"{data} != {deserialized}"

    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        dump(data, temp_file)
        temp_file.seek(0)
        deserialized = load(temp_file)

    assert data == deserialized, f"{data} != {deserialized}"

    assert data == load_base64(dump_base64(data))

def test_headerless():
    data = 1

    serialized = dumps(data, header=False)

    assert len(serialized) == 1

    deserialized = loads(serialized, header=False)

    assert data == deserialized

def test_constants():
    assert loads(dumps(True)) is True
    assert loads(dumps(False)) is False
    assert loads(dumps(None)) is None
    assert loads(dumps(...)) is ...
    assert loads(dumps(NotImplemented)) is NotImplemented
