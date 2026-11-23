"""Lesson 3 spec: RESP, Redis's wire format, as two pure functions.

    parse(buf)    -> (value, bytes_used), or None if buf holds only part of a frame
    encode(value) -> bytes

RESP type        on the wire                 Python value
simple string    +OK\r\n                     "OK"            (str)
error            -ERR oops\r\n               Error("ERR oops")
integer          :42\r\n                     42              (int)
bulk string      $5\r\nhello\r\n             b"hello"        (bytes)
null             $-1\r\n  or  *-1\r\n        None
array            *2\r\n<frame><frame>        [ ... ]         (list)

No sockets here on purpose: the protocol is tested in microseconds, alone.
"""

import pytest

from sat_redis.resp import Error, ProtocolError, encode, parse

# What redis-cli actually sends when you type: ECHO hi
ECHO_HI = b"*2\r\n$4\r\nECHO\r\n$2\r\nhi\r\n"


# --- parse: one of each type -------------------------------------------------

def test_simple_string():
    assert parse(b"+OK\r\n") == ("OK", 5)


def test_error_is_its_own_type():
    value, used = parse(b"-ERR unknown command\r\n")
    assert isinstance(value, Error)
    assert value == "ERR unknown command"
    assert used == 22


def test_integers_positive_and_negative():
    assert parse(b":1000\r\n") == (1000, 7)
    assert parse(b":-7\r\n") == (-7, 5)


def test_bulk_string_is_bytes():
    assert parse(b"$5\r\nhello\r\n") == (b"hello", 11)


def test_empty_bulk_string_is_not_null():
    assert parse(b"$0\r\n\r\n") == (b"", 6)


def test_bulk_string_may_contain_crlf():
    # The length prefix is the whole point: the parser must not stop at the inner \r\n.
    assert parse(b"$4\r\na\r\nb\r\n") == (b"a\r\nb", 10)


def test_null_bulk_and_null_array():
    assert parse(b"$-1\r\n") == (None, 5)
    assert parse(b"*-1\r\n") == (None, 5)


def test_array_of_bulk_strings_is_a_command():
    assert parse(ECHO_HI) == ([b"ECHO", b"hi"], len(ECHO_HI))


def test_empty_array():
    assert parse(b"*0\r\n") == ([], 4)


def test_nested_array_with_mixed_types():
    buf = b"*3\r\n:1\r\n*2\r\n+a\r\n$-1\r\n$1\r\nz\r\n"
    assert parse(buf) == ([1, ["a", None], b"z"], len(buf))


# --- parse: the stream is a hose ---------------------------------------------

@pytest.mark.parametrize("frame", [
    b"+OK\r\n",
    b":-7\r\n",
    b"$4\r\na\r\nb\r\n",
    ECHO_HI,
    b"*3\r\n:1\r\n*2\r\n+a\r\n$-1\r\n$1\r\nz\r\n",
])
def test_every_partial_frame_means_wait_for_more(frame):
    # Cut the frame at every possible point, the way recv might.
    for cut in range(len(frame)):
        assert parse(frame[:cut]) is None, f"cut at {cut}: {frame[:cut]!r}"


def test_leaves_the_next_frame_alone():
    assert parse(b"+OK\r\n+PONG\r\n") == ("OK", 5)


def test_back_to_back_frames_come_out_in_a_loop():
    buf = ECHO_HI + b"*1\r\n$4\r\nPING\r\n" + b"*1\r\n$3\r\nSET"   # last one unfinished
    frames = []
    while (result := parse(buf)) is not None:
        value, used = result
        frames.append(value)
        buf = buf[used:]
    assert frames == [[b"ECHO", b"hi"], [b"PING"]]
    assert buf == b"*1\r\n$3\r\nSET"   # kept, waiting for the rest


# --- parse: garbage is an error, not "wait for more" -------------------------

def test_unknown_type_byte_is_a_protocol_error():
    with pytest.raises(ProtocolError):
        parse(b"?what\r\n")


def test_non_numeric_length_is_a_protocol_error():
    with pytest.raises(ProtocolError):
        parse(b"$abc\r\nhello\r\n")


def test_bulk_string_longer_than_promised_is_a_protocol_error():
    with pytest.raises(ProtocolError):
        parse(b"$3\r\nhello\r\n")


# --- encode ------------------------------------------------------------------

def test_encode_each_type():
    assert encode("OK") == b"+OK\r\n"
    assert encode(Error("ERR nope")) == b"-ERR nope\r\n"
    assert encode(42) == b":42\r\n"
    assert encode(b"hello") == b"$5\r\nhello\r\n"
    assert encode(b"") == b"$0\r\n\r\n"
    assert encode(None) == b"$-1\r\n"
    assert encode([b"ECHO", b"hi"]) == ECHO_HI


def test_encode_rejects_types_resp_cannot_carry():
    with pytest.raises(TypeError):
        encode(3.5)


def test_round_trip():
    value = [b"SET", b"k\r\nv", 7, "OK", None, [Error("ERR x"), []]]
    wire = encode(value)
    assert parse(wire) == (value, len(wire))
