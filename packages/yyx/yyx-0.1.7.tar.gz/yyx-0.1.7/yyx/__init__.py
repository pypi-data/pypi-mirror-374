
from .corr import describe,jb_test,z_score_normalize,min_max_normalize,positivation,pearson
from .linearRegression import ols,gls,hetero_test,vif,backward_stepwise_regression
from .classification import (softmax_classifier, hierarchical_clustering, svm, decisiontree_classify,
                             random_forest_classify, DecisionTree, RandomForest, _replace_cluster_numbers_with_strings)
from .evaluation import (calculate_metrics, time_series_decomposition, grey_relation_analysis,
                         entropy_weight_method, ACF, clean_df_spaces, critic_method, topsis,vikor)
from .OptimizationAlgorithm.utils import init_mlp
from matplotlib import pyplot as plt
import matplotlib as mpl
from .plot import between_line,set_axis_num
mpl.rcParams.update({
    'font.family': ['Times New Roman','Simhei', 'SimSun'],
    'font.size': 12,  # 基础字体大小
    'axes.titlesize': 14,  # 标题字体大小
    'axes.labelsize': 12,  # 坐标轴标签字体大小
    'legend.fontsize': 10,  # 图例字体大小
    'xtick.labelsize': 10,  # x轴刻度字体大小
    'ytick.labelsize': 10,  # y轴刻度字体大小
    'lines.linewidth': 1.5,  # 线条宽度
    'lines.markersize': 4,  # 标记点大小（如需添加标记）
    'axes.linewidth': 2,  # 坐标轴边框宽度(默认0.8)

    # 刻度线粗细设置（新增）
    'xtick.major.width': 1.5,  # x轴主刻度线宽度
    'ytick.major.width': 1.5,  # y轴主刻度线宽度
    'xtick.minor.width': 1,  # x轴副刻度线宽度（若显示）
    'ytick.minor.width': 1,  # y轴副刻度线宽度（若显示）
    # 刻度线长度设置（可选，让刻度更明显）
    'xtick.major.size': 6,  # x轴主刻度线长度
    'ytick.major.size': 6,  # y轴主刻度线长度
    'xtick.minor.size': 3,  # x轴副刻度线长度

    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'legend.framealpha': 0.8,  # 图例透明度
    'figure.figsize':(8,5),
    'figure.dpi': 300
})
__all__=['describe','jb_test','positivation','pearson','gls','ols']