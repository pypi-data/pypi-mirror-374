import abc

import socket


import urllib.request as urllib2

from ..utils import npz_bytes_to_weights, weights_to_npz_bytes
from ..utils.sockets import determine_master, recv_bytes, send_bytes


class BaseParameterClient(abc.ABC):
    """BaseParameterClient
    Parameter-server clients can do two things: retrieve the current parameters
    from the corresponding server, and send updates (`delta`) to the server.
    """

    client_type = "base"

    @classmethod
    def get_client(cls, client_type: str, port: int = 4000):
        try:
            return next(
                cl for cl in cls.__subclasses__() if cl.client_type == client_type
            )(port)
        except StopIteration:
            raise ValueError(
                "Parameter server mode has to be either `http` or `socket`, "
                "got {}".format(client_type)
            )

    @abc.abstractmethod
    def update_parameters(self, delta: list):
        """Update master parameters with deltas from training process"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_parameters(self):
        """Retrieve master weights from parameter server"""
        raise NotImplementedError


class HttpClient(BaseParameterClient):
    """HttpClient
    Uses HTTP protocol for communication with its corresponding parameter server,
    namely HttpServer. The HTTP server provides two endpoints, `/parameters` to
    get parameters and `/update` to update the server's parameters.
    """

    client_type = "http"

    def __init__(self, port: int = 4000):
        self.master_url = determine_master(port=port)
        self.headers = {"Content-Type": "application/elephas"}

    def get_parameters(self):
        request = urllib2.Request(
            f"http://{self.master_url}/parameters", headers=self.headers
        )
        blob = urllib2.urlopen(request).read()
        return npz_bytes_to_weights(blob)

    def update_parameters(self, delta: list):
        blob = weights_to_npz_bytes(delta)
        request = urllib2.Request(
            f"http://{self.master_url}/update", data=blob, headers=self.headers
        )
        return urllib2.urlopen(request).read()


class SocketClient(BaseParameterClient):
    """SocketClient
    Uses a socket connection to communicate with an instance of `SocketServer`.
    The socket server listens to two types of events. Those with a `g` prefix
    indicate a get-request, those with a `u` indicate a parameter update.
    """

    client_type = "socket"

    def __init__(self, port: int = 4000):
        self.port = port

    def get_parameters(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            host = determine_master(port=self.port).split(":")[0]
            sock.connect((host, self.port))
            sock.sendall(b"g")
            blob = recv_bytes(sock)
        return npz_bytes_to_weights(blob)

    def update_parameters(self, delta: list):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            host = determine_master(port=self.port).split(":")[0]
            sock.connect((host, self.port))
            sock.sendall(b"u")
            blob = weights_to_npz_bytes(delta)
            send_bytes(sock, blob)
