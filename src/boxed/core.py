import sys
import builtins
import importlib


def _sendpickle_factory(pickler):
    def sendpickle(self, data):
        lib = importlib.import_module(pickler)
        data = lib.dumps(data)
        self.sendsafe(data)
    sendpickle.__name__ = 'send' + pickler

    return sendpickle


def _recvpickle_factory(pickler):
    def recvpickle(self):
        try:
            lib = self.picklers[pickler]
        except KeyError:
            lib = self.picklers[pickler] = importlib.import_module(pickler)
        data = self.recvsafe()
        return lib.loads(data)
    recvpickle.__name__ = 'recv' + pickler

    return recvpickle

# We store these here in case someone messes with the system's builtins
# This happens with the ejudge engine since it messes with these functions in
# order to capture inputs and outputs from a program.
_python_input_function = input
_python_print_function = print


class CommunicationPipe:
    """A simple communication link between two programs based on sending and
    receiveing messages in the stdin and stdout streams."""

    def __init__(self, stdout=None, stdin=None, serializer='pickle', encoding='utf8'):
        self.serializer = serializer
        self.stdout = stdout
        self.stdin = stdin
        self.encoding = encoding
        self.picklers = {}

    @property
    def serializer(self):
        return self._default

    @serializer.setter
    def serializer(self, value):
        try:
            self._default_sender = getattr(self, 'send%s' % value)
            self._default_receiver = getattr(self, 'recv%s' % value)
            self._default = value
        except AttributeError:
            raise ValueError('invalid method')

    def senderror(self, ex):
        """Sends an exception"""

        if self.serializer == 'json':
            self.send({
                '@error': type(ex).__name__,
                '@message': str(ex),
            })
        else:
            self.send(ex)

    def recvcheck(self):
        """Receive and check if some error were raised."""

        data = self.recv()
        if self.serializer == 'json' and data and isinstance(data, dict):
            if '@error' in data:
                exception = getattr(builtins, data['@error'])
                if (isinstance(exception, type) and
                        issubclass(exception, Exception)):
                    raise exception(data['@message'])
        else:
            if isinstance(data, Exception):
                raise data
        return data

    def sendraw(self, st):
        """Send a raw string of text. The other end must read it using
        the recvraw() function."""

        st = self.as_str(st)

        if '\n' in st or '\r\f' in st:
            raise ValueError('cannot send strings with newline characters')
        _python_print_function(st, file=self.stdout or sys.stdout)

    def recvraw(self):
        """Receives a raw stream sent by sendraw()."""

        if self.stdin is None:
            return _python_input_function()
        else:
            return self.stdin.readline().rstrip('\n')

    def sendnumber(self, number):
        """Sends numeric data. The other end must read it with recvnumber()"""

        import numbers

        if not isinstance(number, numbers.Number):
            raise ValueError('not a number: %r' % number)

        self.sendraw(str(number))

    def recvnumber(self):
        """Receives a number sent by sendnumber()"""

        data = self.recvraw()
        try:
            return int(data)
        except ValueError:
            try:
                return float(data)
            except ValueError:
                return complex(data)

    def sendjson(self, data):
        """Sends data by converting it to JSON stream."""

        import json

        self.sendraw(json.dumps(data))

    def recvjson(self):
        """Receive data sent by sendjson."""

        import json

        data = self.recvraw()
        return json.loads(data)

    def sendsafe(self, data):
        """Encode an arbitrary string into a safe form to pass to print()"""

        import base64

        data = base64.b85encode(self.as_bytes(data))
        return self.sendraw(data)

    def recvsafe(self):
        """Receive stream from sendsafe()"""

        import base64

        data = self.as_bytes(self.recvraw())
        return base64.b85decode(data)

    # Pickle support
    sendpickle = _sendpickle_factory('pickle')
    sendcloudpickle = _sendpickle_factory('cloudpickle')
    senddill = _sendpickle_factory('dill')
    recvpickle = _recvpickle_factory('pickle')
    recvcloudpickle = _recvpickle_factory('cloudpickle')
    recvdill = _recvpickle_factory('dill')

    def as_bytes(self, x):
        if isinstance(x, bytes):
            return x
        else:
            return x.encode(self.encoding)

    def as_str(self, x):
        if isinstance(x, str):
            return x
        else:
            return x.decode(self.encoding)

    def send(self, data):
        """Sends an arbitrary python data over the default stream."""

        self._default_sender(data)

    def recv(self):
        """Receives data sent by ty send(data) function."""

        return self._default_receiver()

    def prepare(self, data):
        """Prepare some data with the default send method that can later be
        sent using sendraw(). The other side of the connection should receive
        data using the recv() method normally"""

        buffer = []
        try:
            self.sendraw = buffer.append
            self.send(data)
        finally:
            del self.sendraw
        return buffer[0]


#
# Specialized error classes
#
class SerializationError(ValueError):
    """Triggered when pickle or other serializer fails."""
