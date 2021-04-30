import socket
from threading import Thread


def single_serve(listener, worker_id):
    logging_prefix = f'Worker {worker_id}: '
    while True:
        client, peer_address = listener.accept()
        print(logging_prefix + f'accepted connection from {peer_address}')
        client.shutdown(socket.SHUT_WR)
        received = b''
        while True:
            more = client.recv(1024)
            if not more:
                print(
                    logging_prefix
                    + f'End of message reached for {peer_address}'
                )
                client.close()
                break
            print(logging_prefix + f'Received "{more}" from {peer_address}')
            received += more
    listener.close()


def serve(address, workers=4):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(address)
    listener.listen(8)
    print(f'Listening at {address}')
    for worker_id in range(workers):
        Thread(target=single_serve, args=(listener, worker_id)).start()


if __name__ == '__main__':
    address = ('127.0.0.1', 1060)
    serve(address)
