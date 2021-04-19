from Value import Value
import Value as v
import hashlib
from binascii import hexlify, unhexlify
import os

class tree:
    def __init__(self, n_parties): # recieve from circuit.py
        self.n_parties = n_parties
        self.right = None
        self.left = None
        self.data = None

    def make(self):
        #make tree
        self.data = getranbyte(16)
        h = unhexlify(hashlib.sha256(self.data).hexdigest())
        n = self.n_parties
        l = find_layers(n) 
        make_helper(l, self)


    def get_path(self, omit):
        #given id of party to not open, return path
        
    

def make_helper(l, root):
    h = unhexlify(hashlib.sha256(root.data).hexdigest())
    if l == 1:
        root.left = tree(1)
        root.left.data = h[:16]
        #print("child: ", h[:16])
        root.right = tree(1)
        root.right.data = h[16:]
        #print("child: ", h[16:])
        return root
    else:
        root.left = tree(1)
        root.left.data = h[:16]
        #print("call left")
        root.left = make_helper(l-1, root.left)
        root.right = tree(1)
        root.right.data = h[16:]
        #print("call right")
        root.right = make_helper(l-1,root.right)


#helper functions
def getranbyte(num_bytes): 
    x = (os.urandom(num_bytes))
    return x
        
def find_max_power_two(l):
    #given integer, return maximum power of two and power
    power_two = 2
    i = 1
    while (power_two*2) <= l:
        power_two = power_two*2
        i = i+1
    return power_two, i

def find_layers(l):
    #given number of parties, return how many layers in tree 
    n = find_max_power_two(l)
    if l > n[0]:
        return n[1]+1
    else:
        return n[1]
if __name__ == "__main__":
    t = tree(9)
    t.make()
