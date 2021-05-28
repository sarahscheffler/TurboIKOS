# MPC-in-the-head

A Python implementation on "MPC-in-the-head".

## Running Protocol

The protocol has the following dependencies.

### Dependencies:  
- [GMP](https://gmplib.org)
- [MPFR](https://www.mpfr.org)
- [MPC](http://www.multiprecision.org/mpc/)
- [gmpy2](https://gmpy2.readthedocs.io/en/latest/mpz.html#examples) 
- [PyCryptodome](https://pycryptodome.readthedocs.io/en/latest/src/installation.html) 
- ([matplotlib](https://matplotlib.org/3.3.3/contents.html))
- ([objsize](https://pypi.org/project/objsize/))

Setup on a fresh Ubuntu instance:
```sh
$ sudo apt update
$ sudo apt install python3-pip
$ sudo apt install libgmp-dev libmpfr-dev libmpc-dev
$ pip3 install gmpy2 pycryptodomex (numpy matplotlib pycryptodome psutil)
```

## Test Files 
Test files are either Bristol format files or PWS files. 

**Bristol Format**

Bristol files were found from ['Bristol Fashion' MPC Circuits](https://homes.esat.kuleuven.be/~nsmart/MPC/). 
Files must be modified so that the second line has the total number of input wires and a 1 for every occurance of input wire. See circuits/adder64_mod.txt for an example. 

**PWS File**

circuits/matmult.py file gained from [PWS Prover Workseet](https://github.com/hyraxZK/pws/tree/2ee3106fbafcd4ca07f752a6a423ccb6cd4e73c0). 


### Instruction to run test:
**Run TurboIKOS**
```sh
$ python3 "python file" circuits/"circuit file"

eg.
$ python3 TurboIKOS.py circuits/matmult_16.pws
```

**Run \tilde{TurboIKOS}**
```sh
$ python3 tilde_TurboIKOS.py circuits/matmult_16.pws
```
