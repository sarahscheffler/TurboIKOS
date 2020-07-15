"""
Prepare views, commit to the views, and broadcasts shared information.
for now, merkle trees are used as an example. from merklelib https://pypi.org/project/merklelib/
"""

import string
import hashlib
from merklelib import MerkleTree
import Preprocessing.py
import Circuit.py


def hashfunc(value):
    return hashlib.sha256(value).hexdigest()


def commit(seed, triples, e_vals):
    # take the beaver triples and the lambda seed as input from preprocessing.py
    # here we only take the value of the c's because we do not need to waste space on a's and b's of the triple
    # take the "e" values from circuit.py
    # store the c values in an array c_vals
    data = (seed, c_vals)

    tree = MerkleTree(data, hashfunc)


def broadcast(seed, tree, e_vals):
    # todo: open a server that broadcasts the input vals
    return (seed, tree, e_vals)

# I should rename the all py files to not start with caps
