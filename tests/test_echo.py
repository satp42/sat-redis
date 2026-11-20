"""Lesson 2 spec: an echo server. Run with:  uv run pytest -v

Every test starts your server on a free port in a background thread,
connects to it like nc would, and checks what comes back.
"""
import socket
import struct
import threading

import pytest

from sat_redis.server import make_server, serve_forever


@pytest.fixture
def port():
    server = make_server("127.0.0.1", 0)  # port 0 = "OS, pick any free port"
    threading.Thread(target=serve_forever, args=(server,), daemon=True).start()
    return server.getsockname()[1]


def connect(port):
    return socket.create_connection(("127.0.0.1", port), timeout=2)


def recv_exactly(sock, n):
    """recv() returns *up to* n bytes, so keep asking until we have all n."""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        assert chunk, f"server hung up after {len(buf)} of {n} bytes"
        buf += chunk
    return buf


def test_make_server_returns_a_listening_socket():
    server = make_server("127.0.0.1", 0)
    try:
        assert server.type == socket.SOCK_STREAM
        assert server.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
        socket.create_connection(server.getsockname(), timeout=2).close()
    finally:
        server.close()


def test_echoes_one_message(port):
    with connect(port) as c:
        c.sendall(b"hello")
        assert recv_exactly(c, 5) == b"hello"


def test_echoes_many_messages_on_one_connection(port):
    with connect(port) as c:
        for msg in [b"PING\r\n", b"SET k v\r\n", b"GET k\r\n"]:
            c.sendall(msg)
            assert recv_exactly(c, len(msg)) == msg


def test_bytes_come_back_untouched(port):
    data = b"\x00\r\n\xff caf\xc3\xa9 \r\n"
    with connect(port) as c:
        c.sendall(data)
        assert recv_exactly(c, len(data)) == data


def test_echoes_a_payload_bigger_than_one_recv(port):
    data = bytes(range(256)) * 4096  # 1 MiB, far more than one recv(1024)
    with connect(port) as c:
        # Send from a second thread while this one reads. If we sent all 1 MiB
        # first, both sides could block with full buffers: a deadlock.
        threading.Thread(target=c.sendall, args=(data,), daemon=True).start()
        assert recv_exactly(c, len(data)) == data


def test_serves_the_next_client_after_one_hangs_up(port):
    for name in [b"ada", b"bob", b"cy"]:
        with connect(port) as c:
            c.sendall(name)
            assert recv_exactly(c, len(name)) == name


def test_survives_a_client_that_vanishes_abruptly(port):
    rude = connect(port)
    rude.sendall(b"bye")
    # Linger with timeout 0 makes close() slam the door (a TCP "reset")
    # instead of hanging up politely. Real clients do this when they crash.
    rude.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
    rude.close()
    with connect(port) as c:
        c.sendall(b"still there?")
        assert recv_exactly(c, 12) == b"still there?"


@pytest.mark.xfail(strict=True, reason="Known limit until lesson 5: one client at a time")
def test_two_clients_at_the_same_time(port):
    with connect(port) as first, connect(port) as second:
        first.sendall(b"one")
        assert recv_exactly(first, 3) == b"one"
        second.sendall(b"two")
        assert recv_exactly(second, 3) == b"two"  # times out: still serving `first`
