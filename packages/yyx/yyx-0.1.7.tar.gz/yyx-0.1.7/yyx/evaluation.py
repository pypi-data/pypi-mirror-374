from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import math
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from matplotlib.dates import DateFormatter, MonthLocator,DayLocator
from statsmodels.graphics.tsaplots import plot_acf
import matplotlib as mpl
from matplotlib.ticker import MultipleLocator
import numpy as np
from . import corr
from .corr import positivation,z_score_normalize,min_max_normalize

mpl.rcParams.update({
    'font.family': ['Times New Roman','SimSun'],
    'font.size': 12,  # 基础字体大小
    'axes.titlesize': 14,  # 标题字体大小
    'axes.labelsize': 12,  # 坐标轴标签字体大小
    'legend.fontsize': 10,  # 图例字体大小
    'xtick.labelsize': 10,  # x轴刻度字体大小
    'ytick.labelsize': 10,  # y轴刻度字体大小
    'lines.linewidth': 1.5,  # 线条宽度
    'lines.markersize': 4,  # 标记点大小（如需添加标记）
    'axes.linewidth': 0.8,  # 坐标轴边框宽度
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'legend.framealpha': 0.8,  # 图例透明度
})

def clean_df_spaces(df):
    # 创建原数据框的副本，避免修改原始数据
    cleaned_df = df.copy(deep=True)

    # 定义处理单个单元格的函数：只去除前后空格
    def trim_single_cell(cell_value):
        if pd.isna(cell_value):  # 空值直接返回
            return cell_value
        # 转换为字符串后去除前后空格
        trimmed_str = str(cell_value).strip()
        # 尝试还原为原始数据类型（数字保持数字类型）
        try:
            return int(trimmed_str) if trimmed_str.isdigit() else float(trimmed_str)
        except (ValueError, TypeError):
            return trimmed_str  # 无法转换则保留字符串

    # 对所有单元格应用处理函数
    cleaned_df = cleaned_df.map(trim_single_cell)

    return cleaned_df


def calculate_metrics(df, actual_col, pred_col, file_name='指标结果.xlsx'):
    """
    计算两列数据（实际值列和预测值列）之间的评估指标，输出指标表格并支持导出Excel
    参数:
        df: pandas.DataFrame，包含实际值和预测值的数据框
        actual_col: str，实际值列的列名（如'实际销量'）
        pred_col: str，预测值列的列名（如'预测销量'）
        output_excel: str，输出Excel文件路径
    返回:
        result_df: pandas.DataFrame，包含评估指标的结果表格
    """
    # 检查输入列是否存在
    if actual_col not in df.columns:
        raise ValueError(f"数据中不存在实际值列：{actual_col}")
    if pred_col not in df.columns:
        raise ValueError(f"数据中不存在预测值列：{pred_col}")

    # 剔除含有缺失值的行
    df_clean = df.dropna(subset=[actual_col, pred_col]).copy()

    # 提取实际值和预测值
    y_actual = df_clean[actual_col]
    y_pred = df_clean[pred_col]

    # 计算评估指标
    # 处理特殊情况：避免实际值和预测值完全相同时的计算警告
    if y_actual.nunique() == 1 and y_pred.nunique() == 1:
        r2 = 1.0 if y_actual.iloc[0] == y_pred.iloc[0] else 0.0
    else:
        r2 = r2_score(y_actual, y_pred)

    mse = mean_squared_error(y_actual, y_pred)
    rmse = math.sqrt(mse)
    mae = mean_absolute_error(y_actual, y_pred)
    mape = (abs((y_actual - y_pred) / y_actual).mean() * 100) if (y_actual != 0).all() else None  # 避免除以0

    # 整理结果
    results = [
        ['R²', round(r2, 4)],
        ['MSE', round(mse, 4)],
        ['RMSE', round(rmse, 4)],
        ['MAE', round(mae, 4)]
    ]
    if mape is not None:
        results.append(['MAPE(%)', round(mape, 2)])  # 增加MAPE指标（百分比）

    # 转换为DataFrame
    result_df = pd.DataFrame(results, columns=['指标', '值'])

    # 打印指标
    print(f"===== {actual_col} 与 {pred_col} 的评估指标 =====")
    print(result_df.to_string(index=False))  # 不显示行索引

    # 导出到Excel
    if file_name:
        try:
            result_df.to_excel(file_name, index=False)
            print(f"\n指标已保存至：{file_name}")
        except Exception as e:
            print(f"\n导出Excel失败：{str(e)}")

    return result_df
def time_series_decomposition(df, index_col: str = None, period=365, model='additive', split=False):
    """
    时间序列分解
    对 DataFrame 中的每列时间序列数据进行分解并绘图
    参数:
        df: pandas.DataFrame，索引或第一列为 datetime 类型，列为待分析的时间序列
        period: int，时间序列的周期
        model: str，分解模型，'additive'（加法）或 'multiplicative'（乘法），默认 'additive'
        split: bool，是否将四个子图分开展显示，默认False（合并显示）
    返回:
        dict: 包含各列的趋势项、季节项和残差项的字典
    """
    # 创建一个字典存储分解结果
    decomposition_results = {}

    if index_col is None:
        index_col = df.columns[0]
        df = df.set_index(df.columns[0])  # 使用非原地修改，避免改变原数据
    else:
        df = df.set_index(index_col)  # 使用非原地修改，避免改变原数据

    df.index = pd.to_datetime(df.index)

    # 遍历每列数据进行分解
    for col in df.columns:
        # 提取单列数据并去除缺失值
        ts_data = df[col].dropna()

        # 时间序列分解
        decomposition = seasonal_decompose(ts_data, model=model, period=period)

        # 存储当前列的分解结果
        decomposition_results[col] = {
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid,
            'original': ts_data  # 也可以选择包含原始数据
        }

        # 以下是绘图部分，保持不变
        color_original = (169 / 255, 214 / 255, 220 / 255)  # 浅蓝色
        color_trend = (246 / 255, 199 / 255, 206 / 255)  # 浅粉色
        color_seasonal = (245 / 255, 209 / 255, 202 / 255)  # 浅橙色
        color_residual = (215 / 255, 194 / 255, 217 / 255)  # 浅紫色

        plots = [
            {
                'data': (ts_data.index, ts_data),
                'color': color_original,
                'label': 'Original',
                'title': f'{col}时间序列分解'
            },
            {
                'data': (decomposition.trend.index, decomposition.trend),
                'color': color_trend,
                'label': 'Trend',
                'title': ''
            },
            {
                'data': (decomposition.seasonal.index, decomposition.seasonal),
                'color': color_seasonal,
                'label': 'Seasonal',
                'title': ''
            },
            {
                'data': (decomposition.resid.index, decomposition.resid),
                'color': color_residual,
                'label': 'Residual',
                'title': ''
            }
        ]

        if not split:
            fig, axes = plt.subplots(4, 1, figsize=(16, 12), dpi=300, sharex=True)
            fig.suptitle(f'{col}销量时间序列分解', fontsize=16)

            for i, plot in enumerate(plots):
                x, y = plot['data']
                axes[i].plot(x, y, color=plot['color'], label=plot['label'])
                axes[i].grid(axis='x', linestyle='--', alpha=0.7)
                axes[i].grid(axis='y', linestyle='--', alpha=0.3)
                axes[i].legend()

                if i == 3:
                    axes[i].axhline(y=0, color='black', linestyle='-', alpha=0.3)

            axes[-1].xaxis.set_major_locator(DayLocator(interval=60))
            axes[-1].xaxis.set_major_formatter(DateFormatter('%Y-%m'))
            plt.xticks(rotation=45)

            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.show()
        else:
            for plot in plots:
                x, y = plot['data']
                fig, ax = plt.subplots(figsize=(16, 4), dpi=300)
                ax.plot(x, y, color=plot['color'], label=plot['label'])

                if plot['label'] == 'Original':
                    ax.set_title(plot['title'], fontsize=14)

                ax.grid(axis='x', linestyle='--', alpha=0.7)
                ax.grid(axis='y', linestyle='--', alpha=0.3)
                ax.legend()

                if plot['label'] == 'Residual':
                    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)

                ax.xaxis.set_major_locator(DayLocator(interval=60))
                ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
                plt.xticks(rotation=45)

                plt.tight_layout()
                plt.show()
    return decomposition_results
def ACF(df, index_col: str = None, lags: int = 30, alpha: float = 0.05, unit: str = '天',
        zero_line_color: str or tuple = 'red'):
    """
    为DataFrame中所有列绘制ACF图，支持用RGB值设置中间y=0轴线的颜色
    参数说明：
        zero_line_color: 中间水平线颜色，可接受：
            - 颜色名称（如'red'、'blue'）
            - 十六进制字符串（如'#FF5733'）
            - RGB元组（如(0.8, 0.2, 0.3)，每个值0-1）
    """
    # 处理日期索引
    if index_col is None:
        index_col = df.columns[0]
    df = df.copy()
    df[index_col] = pd.to_datetime(df[index_col])
    df.set_index(index_col, inplace=True)

    for col in df.columns:
        ts_data = df[col].dropna()
        if len(ts_data) < lags + 1:
            print(f"警告：{col}的数据量不足，无法绘制{lags}阶ACF图，已跳过。")
            continue

        # 创建画布和子图
        fig, ax = plt.subplots(figsize=(12, 6), dpi=300)

        # 绘制ACF图
        plot_acf(ts_data, lags=lags, alpha=alpha, zero=True, ax=ax)

        # 寻找并修改y=0水平线的颜色
        for line in ax.lines:
            if all(y == 0 for y in line.get_ydata()):  # 定位y=0的线
                line.set_color(zero_line_color)  # 直接传递RGB元组或颜色字符串
                line.set_linewidth(1.5)  # 增强线条可见性
                break

        # 设置图表信息
        ax.set_title(f'{col}ACF自相关函数图', fontsize=14)
        ax.set_xlabel(f'滞后阶数({unit})', fontsize=12)
        ax.set_ylabel('自相关系数', fontsize=12)
        ax.grid(linestyle='--', alpha=0.6)

        plt.tight_layout()
        plt.show()
def grey_relation_analysis(df, target_col, output_excel='灰色关联度表格'):
    """
    灰色关联分析
    对df中的目标列对其他列计算关联度
    输入:df和目标列名
    输出:灰色关联度表格
    """
    # 数据预处理
    if target_col not in df.columns:
        raise ValueError(f"数据中不存在目标列：{target_col}")

    # 提取数值型列并处理缺失值
    numeric_df = df.select_dtypes(include=[np.number]).dropna()
    if numeric_df.empty:
        raise ValueError("数据中没有有效的数值型列（可能全为缺失值或非数值）")

    if target_col not in numeric_df.columns:
        raise ValueError(f"目标列 {target_col} 不是数值型列或已被过滤（可能含缺失值）")

    # 分离参考序列和比较序列
    reference = numeric_df[target_col].values.reshape(-1, 1)
    compare_cols = [col for col in numeric_df.columns if col != target_col]
    if not compare_cols:
        raise ValueError("除目标列外，没有其他可分析的指标列")

    compare_matrix = numeric_df[compare_cols].values

    # 归一化（优化：增加防除零处理）
    def normalize(data):
        min_val = np.min(data, axis=0)
        max_val = np.max(data, axis=0)
        # 处理最大值等于最小值的情况（避免除零）
        range_val = np.where(max_val == min_val, 1, max_val - min_val)
        return (data - min_val) / range_val

    ref_norm = normalize(reference)
    comp_norm = normalize(compare_matrix)

    # 计算关联系数（优化：处理异常值）
    abs_diff = np.abs(comp_norm - ref_norm)
    min_min = np.nanmin(abs_diff)  # 使用nanmin忽略可能的NaN
    max_max = np.nanmax(abs_diff)
    rho = 0.5

    # 避免分母为零
    denominator = abs_diff + rho * max_max
    denominator = np.where(denominator == 0, 1e-10, denominator)
    correlation_coeff = (min_min + rho * max_max) / denominator

    # 计算关联度（优化：过滤NaN值）
    relation_degree = np.nanmean(correlation_coeff, axis=0)

    # 处理可能的异常关联度值
    relation_degree = np.clip(relation_degree, 0, 1)  # 关联度限制在[0,1]范围
    relation_degree = np.nan_to_num(relation_degree, nan=0.0)  # 将NaN替换为0

    # 整理结果
    result = pd.DataFrame({
        '指标名称': compare_cols,
        '关联度': relation_degree.round(4)
    })

    # 修复排名计算（处理可能的NaN值）
    result['排名'] = result['关联度'].rank(
        ascending=False,
        method='min',
        na_option='bottom'  # 将NaN值排在最后
    ).astype(int)

    # 排序并重置索引
    result = result.sort_values(by='关联度', ascending=False).reset_index(drop=True)

    # 打印结果
    print(f"===== 与 '{target_col}' 的灰色关联度分析结果 =====")
    print(result.to_string(index=False))

    # 导出到Excel
    if output_excel:
        try:
            result.to_excel(output_excel+'.xlsx', index=False)
            print(f"\n结果已保存至：{output_excel}")
        except Exception as e:
            print(f"\n导出Excel失败：{str(e)}")

    return result
def entropy_weight(normalized_array:np.ndarray):
    normalized_array = np.where(normalized_array == 0, 1e-10, normalized_array)
    p = normalized_array / np.sum(normalized_array, axis=0)  # 按列求和
    n_samples = normalized_array.shape[0]
    e = - (1 / np.log(n_samples)) * np.sum(p * np.log(p), axis=0)  # 按列求和
    weights = (1 - e) / np.sum(1 - e)
    return weights
def entropy_weight_method(df:pd.DataFrame,file_name:str='熵权法权重'):
    '''
    熵权法，输入带有索引的df文件
    '''
    print("原始数据：")
    print(df.head())
    indicators = df.iloc[:, 1:].values
    indicator_names = df.iloc[:, 1:].columns.tolist()
    posited_data = positivation(indicators)
    normalized_data = z_score_normalize(posited_data)
    weights = entropy_weight(normalized_data)
    print("\n各指标的权重：")
    res = dict(zip(indicator_names, weights))
    print(res)
    df_result = pd.DataFrame(res, index=['权重'])
    df_result.to_excel(file_name+'.xlsx')


def critic_method(df: pd.DataFrame, file_name: str = 'CRITIC法权重') -> dict:
    """
    CRITIC法计算指标权重
    :param df: 带有索引的DataFrame，第一列为评价对象，其余为评价指标
    :param file_name: 结果保存的文件名
    :return: 各指标权重字典
    """
    print("===== CRITIC法权重计算 =====")
    print("原始数据预览：")
    print(df.head())

    # 提取指标数据
    indicators = df.iloc[:, 1:].values
    indicator_names = df.iloc[:, 1:].columns.tolist()
    n_samples, n_indicators = indicators.shape

    # 1. 数据正向化（调用已提供的正向化函数）
    print("\n===== 数据正向化 =====")
    posited_data = positivation(indicators)

    # 2. 数据归一化
    print("\n===== 数据归一化 =====")
    normalized_data = min_max_normalize(posited_data)
    print("归一化后数据预览：")
    print(normalized_data[:5, :])

    # 3. 计算指标变异性（标准差）
    std_dev = np.std(normalized_data, axis=0)
    print("\n各指标标准差（反映变异性）：")
    for name, std in zip(indicator_names, std_dev):
        print(f"{name}: {std:.4f}")

    # 4. 计算指标间冲突性（相关系数）
    print("\n===== 计算指标冲突性 =====")
    corr_matrix = np.corrcoef(normalized_data, rowvar=False)
    conflict = 1 - corr_matrix  # 冲突性 = 1 - 相关系数

    # 5. 计算信息量
    information = std_dev * np.sum(conflict, axis=0)

    # 6. 计算权重
    weights = information / np.sum(information)

    # 输出结果
    print("\n===== 权重计算结果 =====")
    weight_dict = dict(zip(indicator_names, weights))
    for name, weight in weight_dict.items():
        print(f"{name}: {weight:.6f}")

    # 保存结果
    df_result = pd.DataFrame(weight_dict, index=['权重'])
    df_result.to_excel(f"{file_name}.xlsx")
    print(f"\n结果已保存至 {file_name}.xlsx")

    return weight_dict

def topsis(df: pd.DataFrame, weights=None, file_name: str = 'TOPSIS评价结果') -> pd.DataFrame:
    """
    TOPSIS法综合评价（调用已有工具函数）
    :param df: 输入DataFrame，第一列为评价对象，其余为评价指标
    :param weights: 可选参数，若不提供则使用熵权法计算权重
    :param file_name: 结果保存文件名
    :return: 包含评分和排名的DataFrame
    """
    print("===== TOPSIS法综合评价 =====")
    print("原始数据预览：")
    print(df.head())

    # 提取数据
    objects = df.iloc[:, 0].values  # 评价对象
    indicators = df.iloc[:, 1:].values  # 指标数据
    indicator_names = df.iloc[:, 1:].columns.tolist()
    n_samples, n_indicators = indicators.shape

    # 1. 数据正向化（调用已有正向化函数）
    print("\n===== 数据正向化 =====")
    posited_data = positivation(indicators)

    # 2. 数据标准化（调用已有归一化函数）
    print("\n===== 数据标准化 =====")
    normalized_data = min_max_normalize(posited_data)
    print("标准化后数据预览：")
    print(normalized_data[:5, :])

    # 3. 确定权重（调用已有熵权函数或使用用户提供的权重）
    print("\n===== 确定指标权重 =====")
    if weights is None:
        print("未提供权重，将使用熵权法计算...")
        weights = entropy_weight(normalized_data)
    else:
        # 验证权重有效性并归一化
        weights = np.array(weights)
        if len(weights) != n_indicators:
            raise ValueError(f"权重数量与指标数量不匹配：需要{n_indicators}个，实际提供{len(weights)}个")
        if not np.isclose(np.sum(weights), 1):
            print("警告：提供的权重之和不为1，将自动归一化")
            weights = weights / np.sum(weights)

    # 打印权重
    weight_dict = dict(zip(indicator_names, weights))
    for name, weight in weight_dict.items():
        print(f"{name}: {weight:.6f}")

    # 4. 计算加权标准化矩阵
    weighted_matrix = normalized_data * weights

    # 5. 确定正理想解和负理想解
    positive_ideal = np.max(weighted_matrix, axis=0)  # 正理想解（各指标最大值）
    negative_ideal = np.min(weighted_matrix, axis=0)  # 负理想解（各指标最小值）
    print("\n正理想解（最佳方案）：", positive_ideal)
    print("负理想解（最差方案）：", negative_ideal)

    # 6. 计算各方案到正/负理想解的距离
    d_positive = np.sqrt(np.sum((weighted_matrix - positive_ideal) ** 2, axis=1))  # 到正理想解的距离
    d_negative = np.sqrt(np.sum((weighted_matrix - negative_ideal) ** 2, axis=1))  # 到负理想解的距离

    # 7. 计算综合评价得分（贴近度）
    scores = d_negative / (d_positive + d_negative)

    # 8. 排名（得分越高越好）
    rankings = np.argsort(-scores) + 1  # 降序排列生成排名

    # 整理结果
    result_df = pd.DataFrame({
        '评价对象': objects,
        '综合得分': scores,
        '排名': rankings
    }).sort_values(by='排名').reset_index(drop=True)

    # 输出结果
    print("\n===== TOPSIS评价结果 =====")
    print(result_df)

    # 保存结果
    result_df.to_excel(f"{file_name}.xlsx", index=False)
    print(f"\n结果已保存至 {file_name}.xlsx")

    return result_df
def vikor(
    df: pd.DataFrame,
    weights=None,
    normalization_method: str = "min_max",  # 选择标准化方法：min_max 或 z_score
    v: float = 0.5,  # 决策系数（0→最大化群体效用，1→最小化个体遗憾，0.5为折中）
    file_name: str = "VIKOR评价结果"
) -> pd.DataFrame:
    """
    VIKOR法（多准则折中排序法）核心函数，复用已有工具函数
    :param df: 输入DataFrame，第一列为评价对象（如单品名称），其余列为评价指标
    :param weights: 可选参数，自定义指标权重（需与指标数量一致）；未提供则自动用熵权法计算
    :param normalization_method: 标准化方法，支持"min_max"（默认）或"z_score"
    :param v: 决策机制系数，范围[0,1]，控制群体效用与个体遗憾的权重
    :param file_name: 结果保存的Excel文件名
    :return: 包含VIKOR关键指标（S、R、Q值）及最终排名的DataFrame
    """
    print("===== VIKOR法综合评价 =====")
    print(f"当前参数配置：标准化方法={normalization_method}，决策系数v={v}")
    print("\n1. 原始数据预览：")
    print(df.head())

    # -------------------------- 步骤1：数据拆分 --------------------------
    objects = df.iloc[:, 0].values  # 提取评价对象（如单品名称）
    indicators = df.iloc[:, 1:].values  # 提取指标数值矩阵
    indicator_names = df.iloc[:, 1:].columns.tolist()  # 提取指标名称
    n_samples, n_indicators = indicators.shape  # 样本数（评价对象数）、指标数
    print(f"\n数据维度：{n_samples}个评价对象，{n_indicators}个评价指标")

    # -------------------------- 步骤2：调用正向化函数 --------------------------
    print("\n===== 步骤2：数据正向化（调用positivation函数） =====")
    posited_data = positivation(indicators)  # 复用您的正向化函数
    print("正向化后数据预览（前5行）：")
    print(posited_data[:5, :])

    # -------------------------- 步骤3：调用标准化函数 --------------------------
    print(f"\n===== 步骤3：数据标准化（调用{normalization_method}_normalize函数） =====")
    if normalization_method == "min_max":
        normalized_data = min_max_normalize(posited_data)  # 复用Min-Max标准化
    elif normalization_method == "z_score":
        normalized_data = z_score_normalize(posited_data)  # 复用Z-score标准化
    else:
        raise ValueError("标准化方法仅支持 'min_max' 或 'z_score'，请重新指定")
    print("标准化后数据预览（前5行）：")
    print(normalized_data[:5, :])

    # -------------------------- 步骤4：调用熵权函数（或使用自定义权重） --------------------------
    print("\n===== 步骤4：确定指标权重 =====")
    if weights is None:
        print("未提供自定义权重，调用entropy_weight函数计算熵权...")
        weights = entropy_weight(normalized_data)  # 复用您的熵权计算函数
    else:
        # 权重有效性校验：数量匹配 + 归一化处理
        weights = np.array(weights, dtype=np.float64)
        if len(weights) != n_indicators:
            raise ValueError(f"权重数量与指标数量不匹配：需{ n_indicators }个，实际输入{ len(weights) }个")
        if not np.isclose(np.sum(weights), 1):
            print("警告：自定义权重之和不为1，将自动归一化")
            weights = weights / np.sum(weights)  # 自动归一化

    # 打印最终权重
    weight_dict = dict(zip(indicator_names, weights))
    print("最终指标权重：")
    for name, w in weight_dict.items():
        print(f"  {name}: {w:.6f}")

    # -------------------------- 步骤5：VIKOR核心计算（S、R、Q值） --------------------------
    print("\n===== 步骤5：VIKOR核心计算（S、R、Q值） =====")
    # 1. 计算各指标的正理想解(f_star)和负理想解(f_minus)（极大型指标：f_star=最大值，f_minus=最小值）
    f_star = np.max(normalized_data, axis=0)  # 正理想解（各指标最优值）
    f_minus = np.min(normalized_data, axis=0)  # 负理想解（各指标最劣值）
    print(f"正理想解（各指标最优值）：{f_star.round(6)}")
    print(f"负理想解（各指标最劣值）：{f_minus.round(6)}")

    # 2. 计算每个评价对象的"群体效用值(S)"和"个体遗憾值(R)"
    # S_i：加权标准化距离之和（反映群体效用，越小越好）
    S = np.sum(weights * (f_star - normalized_data) / (f_star - f_minus + 1e-10), axis=1)
    # R_i：加权标准化距离的最大值（反映个体遗憾，越小越好）
    R = np.max(weights * (f_star - normalized_data) / (f_star - f_minus + 1e-10), axis=1)
    # 注：+1e-10是避免f_star=f_minus时除以0

    # 3. 计算"折中值(Q)"（综合S和R，越小排名越靠前）
    S_star = np.min(S)  # S的最小值（最优S）
    S_minus = np.max(S)  # S的最大值（最劣S）
    R_star = np.min(R)  # R的最小值（最优R）
    R_minus = np.max(R)  # R的最大值（最劣R）

    # Q值计算公式（避免S_star=S_minus或R_star=R_minus时除以0）
    Q = v * (S - S_star) / (S_minus - S_star + 1e-10) + (1 - v) * (R - R_star) / (R_minus - R_star + 1e-10)

    # -------------------------- 步骤6：结果整理与排名 --------------------------
    print("\n===== 步骤6：结果整理与排名 =====")
    # 整理S、R、Q值及排名（Q越小排名越前，S/R辅助验证）
    result_df = pd.DataFrame({
        "评价对象": objects,
        "群体效用值(S)": S.round(6),
        "个体遗憾值(R)": R.round(6),
        "折中值(Q)": Q.round(6),
        "Q值排名": np.argsort(Q) + 1  # 按Q值升序排名（1为最优）
    })
    # 按Q值排名重新排序结果
    result_df = result_df.sort_values(by="Q值排名").reset_index(drop=True)

    # 打印最终结果
    print("VIKOR法评价结果（按Q值排名）：")
    print(result_df)

    # -------------------------- 步骤7：保存结果 --------------------------
    result_df.to_excel(f"{file_name}.xlsx", index=False)
    print(f"\n结果已保存至：{file_name}.xlsx")

    return result_df