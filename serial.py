
import pickle
from Value import Value
# input value object n and output pickled binary representation of it
def serialize(n):
    return pickle.dumps(gmpy2.to_binary(n.value))

# input pickled onject n and ouput unpickled value object
def deserialize(n):
    return Value(gmpy2.from_binary(pickle.loads(n)))
