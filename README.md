# MPC-in-the-head

A Python implementation on "MPC-in-the-head".

### Dependencies:  
- [GMP](https://gmplib.org)
- [MPFR](https://www.mpfr.org)
- [MPC](http://www.multiprecision.org/mpc/)
- [gmpy2](https://gmpy2.readthedocs.io/en/latest/mpz.html#examples) 
- [PyCryptodome](https://pycryptodome.readthedocs.io/en/latest/src/installation.html) 
(- [matplotlib](https://matplotlib.org/3.3.3/contents.html))
(- [objsize](https://pypi.org/project/objsize/))

Setup on a fresh Ubuntu instance:
```sh
$ sudo apt update
$ sudo apt install python3-pip
($ sudo apt install gcc)
$ sudo apt install libgmp-dev libmpfr-dev libmpc-dev
$ pip3 install numpy gmpy2 matplotlib pycryptodomex (pycryptodome objsize)
```

### Instruction:
```sh
$ python3 "python file" "circuit file"

eg.
$ python3 benchmarking.py circuit/matmult_16.pws
```