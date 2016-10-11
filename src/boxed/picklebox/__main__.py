from boxed.core import set_protocol, END_POINT
from boxed.errors import SerializationError
from boxed.core import load_data, validate_target, lower_privileges, execute_target


# Read data and check handshake
set_protocol(input())
data = load_data()
target = validate_target(data, handshake='picklebox::0.1')


# Sets the UID to the low privilege user in order to prevent harm...
lower_privileges(data.get('user', 'nobody'))


# Execute target function
out_data = execute_target(target, data['args'], data['kwargs'],
                          send_exception=True)


# Serialize and return
try:
    END_POINT(out_data)
except SerializationError as ex:
    END_POINT({
        'status': 'serialization-error',
        'output': repr(out_data['output']),
        'exception': ex.args[0],
    })
