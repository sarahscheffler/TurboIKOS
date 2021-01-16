import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
import math
from benchmarking import benchmarking
import csv
import sys

with open(sys.argv[1], newline='') as f:
    reader = csv.reader(f)
    data = list(reader)

p = data[0]
v = data[1]
s = data[2]
m = data[3] 

num_parties = range(3, 101)
formatter = ticker.FuncFormatter(lambda x_val, tick_pos: "{:.1f}".format(2**x_val))
formatter_time = ticker.FuncFormatter(lambda x_val, tick_pos: "$2^{{{:.0f}}}$".format(x_val))

# 2x2 x-y plot
def plotTable():
    fig, axs = plt.subplots(2, 2, constrained_layout=True)
    plotSize(axs[0, 0],num_parties,log2arr(s))
    plotMemory(axs[1, 0],num_parties,log2arr(m))
    plotPTime(axs[0, 1],num_parties,log2arr(p))
    plotVTime(axs[1, 1],num_parties,log2arr(v))
    plt.savefig('graph/drawP3to100.jpg')
    #  plt.show()


def plotSize(ax, x, y):
    #ax.plot(x, y, label = 'proof size')
    #ax.plot(x, r, label = '# repetitions')
    ax.plot(x, y)
    ax.yaxis.set_major_formatter(formatter)
    # ax.yaxis.set_major_locator(ticker.MultipleLocator(20))
    # ax.set_ylim(0,100)
    ax.set_xlabel('number of parties', fontsize=12)
    ax.set_ylabel('proof size (in MB)', fontsize=12)
    ax.set_title('Proof Size', fontsize=14)
    #ax.legend()


def plotMemory(ax, x, y):
    ax.plot(x, y)
    ax.yaxis.set_major_formatter(formatter)
    ax.set_xlabel('number of parties', fontsize=12)
    ax.set_ylabel('memory usage (in MB)', fontsize=12)
    ax.set_title('Memory Usage', fontsize=14)

    
def plotPTime(ax, x, y):
    ax.plot(x, y)
    ax.yaxis.set_major_formatter(formatter)
    ax.set_xlabel('number of parties', fontsize=12)
    ax.set_ylabel('prover time (in s)', fontsize=12)
    ax.set_title('Prover Time', fontsize=14)


def plotVTime(ax, x, y):
    ax.plot(x, y)
    ax.yaxis.set_major_formatter(formatter)
    ax.set_xlabel('number of parties', fontsize=12)
    ax.set_ylabel('verifier time (in s)', fontsize=12)
    ax.set_title('Verifier Time', fontsize=14)

   
# other methods
def log2arr(arr):
    ret = []
    for i in arr:
        ret.append(math.log(float(i), 2))
    return ret

def log10arr(arr):
    ret = []
    for i in arr:
        ret.append(math.log(float(i), 10))
    return ret

plotTable()

