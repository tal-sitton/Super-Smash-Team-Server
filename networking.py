import socket

LOST_CONNECTION_MSG = "LOST CONNECTION"


def send_msg(client_socket: socket.socket, msg: str, name: str = "lo!"):
    """
    formats a the message the server wants to send and sends it.
    :param client_socket: the socket the server needs to send to
    :param msg: the message that needs to be formatted and sent
    """

    try:
        client_socket.send((str(len(msg)).zfill(2) + msg).encode())
    except Exception as e:
        print(e)


def recv_data(client_socket: socket.socket):
    """
    receives data from a client.
    :param client_socket: the socket of the client that we want to receive from
    """
    try:
        j = client_socket.recv(2)
        j = int(j.decode())
        data = client_socket.recv(j).decode()
    except ConnectionResetError:
        data = LOST_CONNECTION_MSG
    return data
