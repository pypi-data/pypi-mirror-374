import matplotlib.pyplot as plt
import numpy as np
from .OptimizationAlgorithm.utils import init_mlp
init_mlp()
def between_line(x, y1, y2):
    plt.axhline(y=y1, color='gray', linestyle='--', label=f'y1={y1}')
    plt.axhline(y=y2, color='gray', linestyle='--', label=f'y2={y2}')
    plt.fill_between(x,y1,y2,color='lightgray',alpha=0.8,label='置信区间')

def set_axis_num(x,y):
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(nbins=x,  integer=False ))#gca()是获取当前活跃的子图的轴
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(nbins=y, integer=False ))