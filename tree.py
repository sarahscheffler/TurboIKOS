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
        self.layer = None

    def make(self):
        #make tree and return list of seeds and number of layers
        self.data = getranbyte(16)
        h = unhexlify(hashlib.sha256(self.data).hexdigest())
        n = self.n_parties
        self.layer = find_layers(n) 
        seeds = []
        make_helper(self.layer, self, seeds)
        return seeds


    def get_path(self, omit):
        #given id of party to not open, return path
        path = []
        get_path_helper(self.layer,self,omit,path)
        return path

        

#verifier function
def recreate_seeds(path):
    l = len(path)
    seeds = [path[-1][0]]
    if l == 1:
        return seeds
    layer = 1
    for i in range(len(path)-1):
        root = tree(1)
        root.data = path[len(path)-i-2][0]
        #print(len(path)-i-1)
        temp = []
        make_helper(layer,root,temp)
        if path[len(path)-1-i][1] == "l":
            seeds = seeds +  temp
        else:
            seeds = temp + seeds
        layer += 1
    return seeds





#tree helper functions
def make_helper(l, root, seeds):
    #print(root.data)
    h = unhexlify(hashlib.sha256(root.data).hexdigest())
    print("h", h)
    if l == 1:
        root.left = tree(l-1)
        root.left.data = h[:16]
        #print("child: ", h[:16])
        seeds.append(root.left.data)
        root.right = tree(l-1)
        root.right.data = h[16:]
        #print("child: ", h[16:])
        seeds.append(root.right.data)
        return root
    else:
        root.left = tree(l-1)
        root.left.data = h[:16]
        #print("call left")
        root.left = make_helper(l-1, root.left, seeds)
        root.right = tree(l-1)
        root.right.data = h[16:]
        print("call right", root.right.data)
        root.right = make_helper(l-1,root.right, seeds)

def get_path_helper(l,root,omit,path):
    leaf = 2**(l)
    print(l)
    if l == 0:
        return path
    if omit < leaf/2:
        path.append([root.right.data, "r"])
        return get_path_helper(l-1, root.left, omit, path)
    else:
        path.append([root.left.data, "l"])
        return get_path_helper(l-1, root.right, omit-leaf, path)

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
    t = tree(5)
    seeds = t.make()
    print(seeds)
    print(t.right)
    path = t.get_path(2)
    print(path)
    recreated_seeds = recreate_seeds(path)
    print(recreated_seeds)
