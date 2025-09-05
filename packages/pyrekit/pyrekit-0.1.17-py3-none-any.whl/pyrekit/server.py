import inspect
import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask, jsonify
from flask_cors import CORS
from multiprocessing import Process, Value
import logging
from functools import wraps


class Signal:
    """
        Signal class used to control hot_reload
    """
    def __init__(self):
        self.updated = Value('b', False)
        self.reload = Value('b', False)

    def flip_updated(self) -> None:
        with self.updated.get_lock():
            self.updated.value = not self.updated.value

    def flip_reload(self) -> None:
        with self.reload.get_lock():
            self.reload.value = not self.reload.value

    def get_reload(self) -> bool:
        with self.reload.get_lock():
            if self.reload.value == 0:
                return False
            else:
                return True
    
    def get_updated(self) -> bool:
        with self.updated.get_lock():
            if self.updated.value == 0:
                return False
            else:
                return True

class UvicornLogFilter(logging.Filter):
    """
    A custom log filter to suppress /dev/reload logs route, since its a development route only
    """
    def filter(self, record: logging.LogRecord) -> bool:
        # Get the log message
        message = record.getMessage()
        # Check if the message is an access log for the /dev/reload endpoint
        if "/dev/reload" in message:
            return False
        return True

class AppMeta(type):
    """
    Metaclass to automatically discover and register Flask routes from class methods.

    This metaclass inspects the methods of a class it's applied to. If a method
    name follows a specific naming convention (e.g., starts with 'GET_', 'POST_'),
    it's automatically converted into a Flask URL rule.

    Features:
    - Naming Convention: Method names like `GET_user_profile` are mapped to a
      `GET` request at the URL `/user/profile`.
    - Automatic Parameter Handling: Method arguments are converted into URL
      parameters. For example, `def GET_user(self, user_id):` becomes a route
      at `/user/<user_id>`.
    - Typed Parameters: Python type hints are used to create typed URL converters.
      For example, `def GET_user(self, user_id: int):` becomes `/user/<int:user_id>`.
    - Special 'index' method: A method named `index` is automatically mapped to
      the root URL '/' for GET and POST requests.
    """
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        HTTP_PREFIX_MAP = {
            'GET_': 'GET',
            'POST_': 'POST',
            'PUT_': 'PUT',
            'DELETE_': 'DELETE',
        }
        
        TYPE_CONVERTER_MAP = {
            int: 'int',
            float: 'float',
            str: 'string',
        }

        routes_to_register = []

        for item_name, item_value in attrs.items():
            if not callable(item_value) or item_name.startswith('_'):
                continue

            # Handle index page
            if item_name == 'index':
                rule = '/'
                http_methods = ['GET', 'POST']
                view_name = 'index'
                routes_to_register.append((rule, view_name, {'methods': http_methods}))
                continue

            # Handle all other routes based on prefixes
            found_method = None
            path_prefix = None
            
            for prefix, method in HTTP_PREFIX_MAP.items():
                if item_name.startswith(prefix):
                    found_method = method
                    path_prefix = prefix
                    break

            if not found_method:
                continue

            path_name = item_name[len(path_prefix):]
            rule = f"/{path_name.replace('_', '/')}"

            sig = inspect.signature(item_value)
            
            for param in sig.parameters.values():
                if param.name == 'self':
                    continue
                
                converter = TYPE_CONVERTER_MAP.get(param.annotation, 'string')
                
                if converter == 'string':
                    rule += f"/<{param.name}>"
                else:
                    rule += f"/<{converter}:{param.name}>"

            options = {'methods': [found_method]}
            routes_to_register.append((rule, item_name, options))

        if not routes_to_register:
            return

        original_init = cls.__init__

        @wraps(original_init)
        def wrapped_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            
            for rule, view_name, options in routes_to_register:
                view_func = getattr(self, view_name)
                endpoint = options.pop('endpoint', view_name)
                
                self.add_url_rule(rule, endpoint=endpoint, view_func=view_func, **options)

        cls.__init__ = wrapped_init

class MetaclassServer(Flask, metaclass=AppMeta):
    """
    A base Flask application class that uses AppMeta to auto-register routes.
    Inherit from this class to create your application.
    """
    pass

class Server(MetaclassServer):
    """
    The backbone of the app, inherit from this one to make your server
    create any method with:
        index : special route, for the home "/"
        GET_ : will create a get route.
        POST_ : will create a post route.
        PUT_ : will create a put route.
        DELETE_ : will create a delete route.
    Any "_" will be interpreted as a "/"
    """
    def __init__(self, port=5000, host="0.0.0.0", DEV = False, **kwargs):
        super().__init__(import_name="pyreact internal server", **kwargs)
        CORS(self)
        self.port = port
        self.host = host
        self.signal: Signal = None
        self.DEV = DEV

    def set_Signal(self, signal: Signal):
        self.signal = signal
    
    async def GET_dev_reload(self):
        if self.signal != None:
            ret = self.signal.get_reload()
            if self.signal.get_reload() is True:
                self.signal.flip_reload()
            return jsonify({"reload": ret})
        else:
            return {"reload": False, "message": "Route used for development"}, 404

class ServerProcess(Process):
    """
    Just serve as server manager, it manages the server
    """
    def __init__(self, server: Server, signal: Signal = None, DEV = False):
        self.server: Server = server
        self.DEV = DEV
        if self.DEV:
            self.signal = signal
            if self.server.signal is None:
                self.server.set_Signal(self.signal)

        super().__init__(target=self.run)
        
    def run(self):
        """
        This method is executed when the process starts.
        It wraps the Flask WSGI app into an ASGI app and runs it with Uvicorn.
        """
        print(f"Starting server at http://{self.server.host}:{self.server.port}")

        # Apply the log filter
        log_filter = UvicornLogFilter()
        logging.getLogger("uvicorn").addFilter(log_filter)
        logging.getLogger("uvicorn.access").addFilter(log_filter)

        asgi_app = WsgiToAsgi(self.server)

        uvicorn.run(
            asgi_app,
            host=self.server.host,
            port=self.server.port,
            log_level="info"
        )

    def close(self):
        if self.is_alive():
            self.terminate()
        self.join()
