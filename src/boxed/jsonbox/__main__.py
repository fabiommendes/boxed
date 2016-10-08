#
# JSON-based sandbox.
#
# The implementation is very similar to the more generic picklebox. We have it
# separate for in the future we expect that the implementation could be hardened
# in a C implementation that is not as vulnerable as the Python one.
#
# Python is a very fragile sandbox target since the user code can mess with
# stack frames and globals and with some ingenuity can make this script return
# anything it wants. This is not so problematic security-wise when using JSON
# since the execution takes place at a lower privilege. In some scenarios
# (e.g.: an online judge, this open some opportunities to forgery.
#
from boxed.core import set_protocol, END_POINT, SerializationError, comment, \
    send_data
from boxed.core import load_data, validate_target, lower_privileges, execute_target


# Read data and check handshake
set_protocol('json')
data = load_data()
target = validate_target(data, handshake='jsonbox::0.1')


# Sets the UID to the low privilege user in order to prevent harm...
lower_privileges(data.get('user', 'nobody'))


# Execute target function
out_data = execute_target(target, data['args'], data['kwargs'])

# Convert result to JSON and return
try:
    END_POINT(out_data)
except SerializationError:
    END_POINT({
        'status': 'serialization-error',
        'output': repr(out_data['output']),
    })
