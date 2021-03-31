from Value import Value
import gmpy2

ex = Value()
ex.getRand()
print("RAW VALUE:", ex)
print("EX.VALUE:", ex.value)
ex_to_binary = gmpy2.to_binary(ex.value)
print("TO BINARY:", ex_to_binary)
ex_from_binary = gmpy2.from_binary(ex_to_binary)
print("FROM BINARY:", ex_from_binary)

