class CalledProcessError(Exception):
    """
    Exception raised when exception raised in child process cannot be recovered
    """


class SerializationError(ValueError):
    """
    Triggered when pickle or other serializer fails.
    """

    def __getstate__(self):
        return self.args

    def __setstate__(self, state):
        self.args = state

