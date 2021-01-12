import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import math
from benchmarking import benchmarking


labels = [2, 3, 4, 5, 6]
p = [0.723,6.208,53.457,480.675,4624.506]
v = [1.255,10.205,94.364,868.456,10579.007]
s = [1.57,9.308,68.213,527.478,4153.666]
m = [55.235,73.748,207.831,1260.564,9610.92]

"""
num_parties = 10
tempP, tempV, tempS, tempM, rep = benchmarking(num_parties)
print(tempP)
print(tempV)
print(tempS/(10**6))
print(tempM/(10**6))
"""

# 2x2 x-y plot
def plotTable():
    fig, axs = plt.subplots(2, 2, constrained_layout=True)
    plotSize(axs[0, 0])
    plotMemory(axs[0, 1])
    plotPTime(axs[1, 0])
    plotVTime(axs[1, 1])
    fig.suptitle('Matmult Gates', fontsize=14)
    plt.savefig('graph/mm_circuit.jpg')
    #  plt.show()


def plotSize(ax):
    ax.plot(labels, s)
    ax.set_ylabel('proof size (in MB)', fontsize=12)


def plotMemory(ax):
    ax.plot(labels, m)
    ax.set_ylabel('memory (in MB)', fontsize=12)

    
def plotPTime(ax):
    ax.plot(labels, p)
    ax.set_ylabel('prover time (in s)', fontsize=12)


def plotVTime(ax):
    ax.plot(labels, v)
    ax.set_ylabel('verifier time (in s)', fontsize=12)

   
# other methods
def log2arr(arr):
    ret = []
    for i in arr:
        ret.append(math.log(i, 2))
    return ret


plotTable()


"""
# comparision table
def tableCompare(circuit_size, p_time, v_time, memory):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    row = ['Proof Size', 'Prover Time', 'Verifier Time', 'Memory Used']
    col = ['libSNARK','This work']
    values=[['0.13KB', circuit_size+'MB'],
            ['360s', p_time+'s'],
            ['0.002s', v_time+'s'],
            ['\u2265 10GB', memory+'MB']]
    table = plt.table(cellText = values,
                      rowLabels = row,
                      colLabels = col,
                      loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(0.5, 3)
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
    for pos in ['right','top','bottom','left']:
        plt.gca().spines[pos].set_visible(False)
    # plt.savefig('matplotlib-table.png', bbox_inches='tight', pad_inches=0.05)
    plt.show()
"""
    
# comparison histogram
def plotHist(ax, col, string):   
    labels = ['adder64', 'matmult16', 'matmult64']

    x = np.arange(len(labels))  # the label locations
    width = 0.5  # the width of the bars

    rects = ax.bar(x, col, width, label='prover time')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(string)
    # ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

