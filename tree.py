from Value import Value
import Value as v
import hashlib
from binascii import hexlify, unhexlify
import os

class Tree:
    def __init__(self): # recieve from circuit.py
        self.n_seeds = None
        self.right = None
        self.left = None
        self.data = None
        self.layer = None

    def make(self):
        #make tree and return list of seeds and number of layers
        self.data = self.getranbyte(16)
        h = unhexlify(hashlib.sha256(self.data).hexdigest())
        self.layer = self.find_layers(self.n_seeds)
        #print(self.layer)
        seeds = []
        make_helper(self.layer, self, seeds)
        return seeds


    def get_path(self, omit):
        #given id of party to not open, return path
        path = []
        self.get_path_helper(self.layer,self,omit,path)
        return path

    #tree helper functions
    def get_path_helper(self,l,root,omit,path):
        leaf = 2**(l)
        #print(leaf)
        if l == 0:
            return path
        if omit < leaf/2:
            path.append([root.right.data, "r"])
            return self.get_path_helper(l-1, root.left, omit, path)
        else:
            path.append([root.left.data, "l"])
            return self.get_path_helper(l-1, root.right, omit-(leaf/2), path)

    def getranbyte(self,num_bytes): 
        x = (os.urandom(num_bytes))
        return x
        
    def find_max_power_two(self, l):
        power_two = 2
        i = 1
        while (power_two*2) <= l:
            power_two = power_two*2
            i = i+1
        return power_two, i

    def find_layers(self,l):
        n = self.find_max_power_two(l)
        if l > n[0]:
            return n[1]+1
        else:
            return n[1]

def make_helper(l, root, seeds):
    h = unhexlify(hashlib.sha256(root.data).hexdigest())
    if l == 1:
        root.left = Tree()
        root.left.data = h[:16]
        seeds.append(root.left.data)
        root.right = Tree()
        root.right.data = h[16:]
        seeds.append(root.right.data)
        return root
    else:
        root.right = Tree()
        root.left = Tree()
        root.left.data = h[:16]
        root.right.data = h[16:]
        make_helper(l-1, root.left, seeds)
        make_helper(l-1,root.right, seeds)

def make_tree(n_seeds):
    t = Tree()
    t.n_seeds = n_seeds
    seeds = t.make()
    return seeds, t

def get_path(omit, root):
    return root.get_path(omit)

#verifier function
def recreate_seeds(path):
    l = len(path)
    seeds = [path[-1][0]]
    #print(seeds)
    if l == 1:
        return seeds
    layer = 1
    for i in range(len(path)-1):
        #print(layer)
        root = Tree()
        root.data = path[len(path)-i-2][0]
        temp = []
        make_helper(layer,root,temp)

        if path[len(path)-2-i][1] == "l":
    
            seeds = temp +  seeds
            #print("l ",seeds, layer)
        else:
            seeds = seeds + temp
            #print("r ",seeds, layer)
        layer += 1
    return seeds

if __name__ == "__main__":
    (seeds, root) = make_tree(5)
    path = get_path(3, root)
    recreated_seeds = recreate_seeds(path)