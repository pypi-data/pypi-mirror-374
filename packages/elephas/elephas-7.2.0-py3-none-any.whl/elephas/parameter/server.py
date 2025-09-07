import abc
import socket
from functools import wraps
from threading import Thread
from flask import Flask, request, Response
from multiprocessing import Process
from tensorflow.keras.models import Model

from elephas.enums.modes import Mode
from elephas.utils.sockets import determine_master
from elephas.utils.sockets import recv_bytes, send_bytes
from elephas.utils.serialization import (
    dict_to_model,
    weights_to_npz_bytes,
    npz_bytes_to_weights,
)
from elephas.utils.rwlock import RWLock as Lock
from elephas.utils.notebook_utils import is_running_in_notebook
from elephas.utils import subtract_params


class BaseParameterServer(abc.ABC):
    """BaseParameterServer

    Parameter servers can be started and stopped. Server implementations have
    to cater to the needs of their respective BaseParameterClient instances.
    """

    def __init__(self, model: Model, port: int, mode: str, **kwargs):
        self.port = port
        self.mode = mode
        self.master_network = dict_to_model(model, kwargs.get("custom_objects"))
        self.lock = Lock()

    @abc.abstractmethod
    def start(self):
        """Start the parameter server instance."""

    @abc.abstractmethod
    def stop(self):
        """Terminate the parameter server instance."""

    def make_read_threadsafe_if_necessary(self, func):
        return self.make_threadsafe_if_necessary(func, self.lock.acquire_read)

    def make_write_threadsafe_if_necessary(self, func):
        return self.make_threadsafe_if_necessary(func, self.lock.acquire_write)

    def make_threadsafe_if_necessary(self, func, lock_aquire_callable):
        if self.mode == Mode.ASYNCHRONOUS:

            @wraps(func)
            def wrapper(*args, **kwargs):
                lock_aquire_callable()
                result = func(*args, **kwargs)
                self.lock.release()
                return result

            return wrapper
        else:
            return func


class HttpServer(BaseParameterServer):
    """HttpServer

    Flask HTTP server. Defines two routes, `/parameters` to GET current
    parameters held by this server, and `/update` which can be used to
    POST updates.
    """

    def __init__(self, model: Model, port: int, mode: str, **kwargs):
        """Initializes and HTTP server from a serialized Keras model
        a parallelisation mode and a port to run the Flask application on. In
        hogwild mode no read- or write-locks will be acquired, in asynchronous
        mode this is the case.

        :param model: Serialized Keras model
        :param mode: parallelization mode, either `asynchronous` or `hogwild`
        :param port: int, port to run the application on
        :param debug: boolean, Flask debug mode
        :param threaded: boolean, Flask threaded application mode
        :param use_reloader: boolean, Flask `use_reloader` argument
        """

        super().__init__(model, port, mode, **kwargs)
        self.master_url = None

        if is_running_in_notebook():
            self.threaded = False
            self.use_reloader = False
            self.debug = False
        else:
            self.debug = kwargs.get("debug", True)
            self.threaded = kwargs.get("threaded", True)
            self.use_reloader = kwargs.get("use_reloader", False)

        self.weights = self.master_network.get_weights()

        self.server = Process(target=self.start_flask_service)

    def start(self):
        self.server.start()
        self.master_url = determine_master(self.port)

    def stop(self):
        self.server.terminate()
        self.server.join()
        self.server.close()

    def start_flask_service(self):
        """Define Flask parameter server service.

        This HTTP server can do two things: get the current model
        parameters and update model parameters. After registering
        the `parameters` and `update` routes, the service will
        get started.

        """
        app = Flask(__name__)
        self.app = app

        @app.route("/")
        def home():
            return "Elephas"

        @app.route("/parameters", methods=["GET"])
        @self.make_read_threadsafe_if_necessary
        def handle_get_parameters():
            payload = weights_to_npz_bytes(self.weights)
            return Response(payload, mimetype="application/octet-stream")

        @app.route("/update", methods=["POST"])
        @self.make_write_threadsafe_if_necessary
        def handle_update_parameters():
            delta = npz_bytes_to_weights(request.data)
            if not self.master_network.built:
                self.master_network.build()
            weights_before = self.weights
            self.weights = subtract_params(weights_before, delta)
            return "Update done"

        master_url = determine_master(self.port)
        host = master_url.split(":")[0]
        self.app.run(
            host=host,
            debug=self.debug,
            port=self.port,
            threaded=self.threaded,
            use_reloader=self.use_reloader,
        )


class SocketServer(BaseParameterServer):
    """SocketServer

    A basic Python socket server

    """

    def __init__(self, model: Model, port: int, mode: str, **kwargs):
        """Initializes a Socket server instance from a serializer Keras model
        and a port to listen to.

        :param model: Serialized Keras model
        :param port: int, port to run the socket on
        """

        super().__init__(model, port, mode, **kwargs)
        self.socket = None
        self.runs = False
        self.connections = []
        self.lock = Lock()
        self.thread = None
        self.update_parameters = self.make_write_threadsafe_if_necessary(
            self.update_parameters
        )
        self.get_parameters = self.make_read_threadsafe_if_necessary(
            self.get_parameters
        )

    def start(self):
        if self.thread is not None:
            self.stop()
        self.thread = Thread(target=self.start_server)
        self.thread.start()

    def stop(self):
        self.stop_server()
        self.thread.join()
        self.thread = None

    def start_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        master_url = determine_master(port=self.port).split(":")[0]
        host = master_url.split(":")[0]
        sock.bind((host, self.port))
        sock.listen(5)
        self.socket = sock
        self.runs = True
        self.run()

    def stop_server(self):
        self.runs = False
        if self.socket:
            for thread in self.connections:
                thread.join()
                del thread
            self.socket.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                host = determine_master(port=self.port).split(":")[0]
                sock.connect((host, self.port))
                sock.close()
            except Exception:
                pass
        self.socket = None
        self.connections = []

    def update_parameters(self, conn):
        blob = recv_bytes(conn)
        delta = npz_bytes_to_weights(blob)
        weights = self.master_network.get_weights()
        self.master_network.set_weights(subtract_params(weights, delta))

    def get_parameters(self, conn):
        weights = self.master_network.get_weights()
        blob = weights_to_npz_bytes(weights)
        send_bytes(conn, blob)

    def action_listener(self, conn):
        while self.runs:
            get_or_update = conn.recv(1).decode()
            if get_or_update == "u":
                self.update_parameters(conn)
            elif get_or_update == "g":
                self.get_parameters(conn)

    def run(self):
        while self.runs:
            conn, addr = self.socket.accept()
            thread = Thread(target=self.action_listener, args=(conn,))
            thread.start()
            self.connections.append(thread)
