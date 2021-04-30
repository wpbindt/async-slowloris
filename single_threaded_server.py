import socket


def serve(address):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(address)
    print(f'Listening at {address}')
    listener.listen(8)
    while True:
        client, peer_address = listener.accept()
        print(f'Connection accepted from {peer_address}')
        client.shutdown(socket.SHUT_WR)
        received = b''
        while True:
            more = client.recv(1024)
            if not more:
                print(f'End of message reached for {peer_address}')
                client.close()
                break
            print(f'Received "{more}" from {peer_address}')
            received += more
    listener.close()


if __name__ == '__main__':
    address = ('127.0.0.1', 1060)
    serve(address)
