"""refer to slide 5. This file will be used to handle data from wires"""

database = {}


def acceess_wire(index):
    return database[index]


def insert_wire(index, value):
    database[index] = value
    return 1
