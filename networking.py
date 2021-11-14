import socket

LOST_CONNECTION_MSG = "LOST CONNECTION"

BUFFER_SIZE = 1024


def send_msg(udp_socket: socket.socket, client_addrs: (str, int), msg: str):
    """
    Sends a message to a client
    :param client_addrs: the address of the client
    :param msg: the message that needs to be sent
    """
    udp_socket.sendto(msg.encode(), client_addrs)


def send_tcp_msg(client_tcp_socket: socket.socket, msg: str):
    client_tcp_socket.send((msg + ";").encode())


def recv_data(udp_socket: socket.socket) -> (str, (str, int)):
    """
    receives data from a client.
    :param client_socket: the socket of the client that we want to receive from
    """
    m = udp_socket.recvfrom(BUFFER_SIZE)
    return m[0].decode(), m[1]
