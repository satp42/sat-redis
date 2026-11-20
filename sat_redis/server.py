import socket

def make_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    return server

def handle(conn):
    while data := conn.recv(1024):
        conn.sendall(data)

def server_forever(server):
    while True:
        conn, addr = server.accept()
        try:
            with conn:
                handle(conn)
        except ConnectionError:
            continue

if __name__ == "__main__":
    server = make_server("127.0.0.1", 6380)
    server_forever(server)