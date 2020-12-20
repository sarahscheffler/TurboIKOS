import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import math

# Comparision table to other protocols
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


def plotTable(p, v, s, m):
    fig, axs = plt.subplots(2, 2, constrained_layout=True)
    plotSize(axs[0, 0],range(1, 81),s)
    plotPTime(axs[0, 1],range(1, 81),p)
    plotVTime(axs[1, 0],range(1, 81),v)
    plotMemory(axs[1, 1],range(1, 81),m)
    plt.show()


def plotSize(ax, x, y):
    ax.plot(log2arr(x), y)
    ax.set_xlabel('log2 # repetitions', fontsize=12)
    ax.set_ylabel('proof size (in MB)', fontsize=12)
    ax.set_title('Proof Size', fontsize=14)


def plotMemory(ax, x, y):
    ax.plot(log2arr(x), y)
    ax.set_xlabel('log2 # repetitions', fontsize=12)
    ax.set_ylabel('memory usage (in MB)', fontsize=12)
    ax.set_title('Memory Usage', fontsize=14)

    
def plotPTime(ax, x, y):
    ax.plot(log2arr(x), y)
    ax.set_xlabel('log2 # repetitions', fontsize=12)
    ax.set_ylabel('prover time (in s)', fontsize=12)
    ax.set_title('Prover Time', fontsize=14)


def plotVTime(ax, x, y):
    ax.plot(log2arr(x), y)
    ax.set_xlabel('log2 # repetitions', fontsize=12)
    ax.set_ylabel('verifier time (in s)', fontsize=12)
    ax.set_title('Verifier Time', fontsize=14)
    

def log2arr(arr):
    ret = []
    for i in arr:
        ret.append(math.log(i, 2))
    return ret
