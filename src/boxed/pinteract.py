import time
import psutil
import pexpect
inf = float('inf')


class Pinteract:
    """
    A class for conveniently interacting with a child process.
    """

    def __init__(self, command, timeout=None, encoding='utf8', cwd=None, env=None):
        if timeout == inf:
            timeout = None
        self.__burnt = False
        self._remaining_time = timeout or float('inf')
        self._process = pexpect.spawn(command[0], command[1:], cwd=cwd, env=env)
        self._process.setecho(False)
        self._psdata = psutil.Process(self._process.pid)
        self.encoding = encoding
        self.timeout = timeout
        self.cwd = cwd
        self.env = env
        self.pid = self._process.pid
        
    def burn(self, duration):
        """
        Burn at most the given time (in seconds) waiting for the process to
        leave the "running" status.
        """
        
        t0 = time.time()
        duration = min(duration, self._remaining_time)
        duration = max(duration, 0)
        for _ in range(int(duration * 100)):
            status = self.status()
            if status in ['running', 'disk-sleep']:
                time.sleep(0.005)
            elif status in ['sleeping', 'zombie', 'dead']:
                break
            else:
                raise RuntimeError('status: %s' % status)
        self._remaining_time -= time.time() - t0
        
    def __burn_once(self):
        """
        Burn at most timeout at the first call to receive().
        """
        
        if not self.__burnt:
            if self.timeout is None:
                self.burn(1)
            else:
                self.burn(self.timeout)
        
    def status(self):
        """
        Return a string with the status code for the process.
        """

        try:
            return self._psdata.status()
        except psutil.NoSuchProcess:
            return 'dead'
    
    def is_running(self):
        """
        Return True if child process is still running.
        """
        
        return self.status() == 'running'
                    
    def is_dead(self):
        """
        Return True if child process is dead.
        """
        
        return self.status() in ['zombie', 'dead']

    def is_sleeping(self):
        """
        Return True if child process is sleeping.
        """
        
        return self.status() == 'sleeping'

    def receive(self):
        """
        Read the output of the child process.
        """

        self.__burn_once()
        t0 = time.time()
        data = []
        last = 'non empty'
        while last:
            try:
                last = self._process.read_nonblocking(1, timeout=0.05)
            except pexpect.EOF:
                break
            except pexpect.TIMEOUT:
                if self.status() == 'sleeping':
                    break
                elif self.status() == 'running':
                    tf = time.time()
                    self._remaining_time -= tf - t0
                    t0 = tf
                    if self._remaining_time <= 0:
                        raise TimeoutError
                    break
                else:
                    raise TimeoutError('timeout with unhandled status: %s' %
                                       self.status())
            data.append(last)

        self._remaining_time -= time.time() - t0        
        data = b''.join(data)
        if self.encoding is not None:
            data = data.decode(self.encoding)
        return data.replace('\r\n', '\n')

    def receive_non_empty(self):
        """
        Tries to execute the ".receive()" command several times until a
        non-empty response is given.
        """

        data = ''
        while not data:
            data = self.receive()
        return data
    
    def send(self, data, end=None):
        """
        Write some input string of data to the child process.
        """
        
        t0 = time.time()
        if self.is_dead():
            raise RuntimeError('trying to send message to a closed process')
        
        if end is None:
            self._process.sendline(data)
        else:
            self._process.send(data + end)
        self._remaining_time -= time.time() - t0

    def finish(self):
        """
        Finish process execution. Return a tuple with any unread
        (stdout, stderr) messages.
        """

        out = self.receive()
        self._process.kill(9)
        return out