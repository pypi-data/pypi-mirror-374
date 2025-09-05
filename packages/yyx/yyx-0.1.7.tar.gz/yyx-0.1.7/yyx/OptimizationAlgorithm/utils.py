import numpy as np
import random
from typing import List, Tuple,Optional
import matplotlib as mpl
import torch
import time
# ================= 交叉算子 =================
def binary_crossover(p1: np.ndarray, p2: np.ndarray, pc: float = 0.9) -> Tuple[np.ndarray, np.ndarray]:
    """二进制变量专用交叉：单点交叉"""
    if random.random() > pc or len(p1) != len(p2):
        return p1.copy(), p2.copy()

    c1, c2 = p1.copy(), p2.copy()
    # 随机选择交叉点（至少保留1位不交叉）
    cross_point = random.randint(1, len(p1) - 1)
    c1[cross_point:], c2[cross_point:] = p2[cross_point:].copy(), p1[cross_point:].copy()
    return c1, c2


def integer_crossover(p1: np.ndarray, p2: np.ndarray, low: int, high: int, pc: float = 0.9) -> Tuple[
    np.ndarray, np.ndarray]:
    """整数变量专用交叉：均匀交叉"""
    if random.random() > pc or len(p1) != len(p2):
        return p1.copy(), p2.copy()

    c1, c2 = p1.copy(), p2.copy()
    for i in range(len(p1)):
        if random.random() < 0.5:
            c1[i], c2[i] = p2[i], p1[i]
    # 确保在边界内
    return np.clip(c1, low, high), np.clip(c2, low, high)


def real_crossover(p1: np.ndarray, p2: np.ndarray, low: float, high: float, eta: int = 15, pc: float = 0.9) -> Tuple[
    np.ndarray, np.ndarray]:
    """实数变量专用交叉：SBX交叉"""
    if random.random() > pc or len(p1) != len(p2):
        return p1.copy(), p2.copy()

    c1, c2 = p1.copy(), p2.copy()
    for i in range(len(p1)):
        x1, x2 = p1[i], p2[i]
        if abs(x1 - x2) < 1e-14:
            continue
        if x1 > x2:
            x1, x2 = x2, x1

        beta = 1.0 + (2.0 * (x1 - low) / (x2 - x1 + 1e-14))
        alpha = 2.0 - pow(beta, -(eta + 1))
        rand = random.random()

        if rand <= 1.0 / alpha:
            betaq = pow(rand * alpha, 1.0 / (eta + 1))
        else:
            betaq = pow(1.0 / (2.0 - rand * alpha), 1.0 / (eta + 1))

        c1_val = 0.5 * ((x1 + x2) - betaq * (x2 - x1))
        c2_val = 0.5 * ((x1 + x2) + betaq * (x2 - x1))
        c1[i] = np.clip(c1_val, low, high)
        c2[i] = np.clip(c2_val, low, high)
    return c1, c2


def universal_crossover(p1: np.ndarray, p2: np.ndarray, var_types: List[Tuple[str, Tuple]],
                        eta: int = 15, pc: float = 0.9) -> Tuple[np.ndarray, np.ndarray]:
    """通用交叉入口：自动根据变量类型选择对应交叉算子"""
    c1, c2 = p1.copy(), p2.copy()
    idx = 0

    for vtype, info in var_types:
        if vtype == "binary":
            n = info
            seg1, seg2 = binary_crossover(p1[idx:idx + n], p2[idx:idx + n], pc)
            c1[idx:idx + n], c2[idx:idx + n] = seg1, seg2
            idx += n

        elif vtype == "integer":
            n, low, high = info
            seg1, seg2 = integer_crossover(p1[idx:idx + n], p2[idx:idx + n], low, high, pc)
            c1[idx:idx + n], c2[idx:idx + n] = seg1, seg2
            idx += n

        elif vtype == "real":
            n, low, high = info
            seg1, seg2 = real_crossover(p1[idx:idx + n], p2[idx:idx + n], low, high, eta, pc)
            c1[idx:idx + n], c2[idx:idx + n] = seg1, seg2
            idx += n

    return c1, c2


# ================= 变异算子 =================
def binary_mutate(chrom: np.ndarray, pm: float = 0.05) -> np.ndarray:
    """二进制变量专用变异：位翻转"""
    mutated = chrom.copy()
    for i in range(len(mutated)):
        if random.random() < pm:
            mutated[i] = 1 - mutated[i]
    return mutated


def integer_mutate(chrom: np.ndarray, low: int, high: int, pm: float = 0.05) -> np.ndarray:
    """整数变量专用变异：随机重置"""
    mutated = chrom.copy()
    for i in range(len(mutated)):
        if random.random() < pm:
            mutated[i] = np.random.randint(low, high + 1)
    return mutated


def real_mutate(chrom: np.ndarray, low: float, high: float, pm: float = 0.05) -> np.ndarray:
    """实数变量专用变异：多项式变异"""
    mutated = chrom.copy()
    for i in range(len(mutated)):
        if random.random() < pm:
            x = chrom[i]
            delta1 = (x - low) / (high - low + 1e-14)
            delta2 = (high - x) / (high - low + 1e-14)
            rand = random.random()

            if rand <= 0.5:
                val = 1.0 - delta1
                alpha = 2.0 * rand + (1.0 - 2.0 * rand) * (val ** 5.0)
                delta_q = alpha ** (1.0 / 6.0) - 1.0
            else:
                val = 1.0 - delta2
                alpha = 2.0 * (1.0 - rand) + 2.0 * (rand - 0.5) * (val ** 5.0)
                delta_q = 1.0 - alpha ** (1.0 / 6.0)

            x_new = x + delta_q * (high - low)
            mutated[i] = np.clip(x_new, low, high)
    return mutated


def universal_mutate(chrom: np.ndarray, var_types: List[Tuple[str, Tuple]], pm: float = 0.05) -> np.ndarray:
    """通用变异入口：自动根据变量类型选择对应变异算子"""
    mutated = chrom.copy()
    idx = 0

    for vtype, info in var_types:
        if vtype == "binary":
            n = info
            mutated[idx:idx + n] = binary_mutate(mutated[idx:idx + n], pm)
            idx += n

        elif vtype == "integer":
            n, low, high = info
            mutated[idx:idx + n] = integer_mutate(mutated[idx:idx + n], low, high, pm)
            idx += n

        elif vtype == "real":
            n, low, high = info
            mutated[idx:idx + n] = real_mutate(mutated[idx:idx + n], low, high, pm)
            idx += n

    return mutated

def decode(chrom: np.ndarray, var_types: List[Tuple[str, Tuple]]):
    """解码不同类型变量，支持多组实数/整数/二进制变量"""
    idx = 0
    decoded = {}
    type_counter = {"binary": 0, "integer": 0, "real": 0}

    for var_type, info in var_types:
        key = f"{var_type}_{type_counter[var_type]}"
        type_counter[var_type] += 1

        if var_type == "binary":
            n = info
            decoded[key] = chrom[idx:idx+n].astype(int)
            idx += n
        elif var_type == "integer":
            n, low, high = info
            val = np.rint(chrom[idx:idx+n]).astype(int)
            decoded[key] = np.clip(val, low, high)
            idx += n
        elif var_type == "real":
            n, low, high = info
            decoded[key] = chrom[idx:idx+n]
            idx += n
    return decoded
def init_mlp():
    mpl.rcParams.update({
        'font.family': ['Times New Roman', 'Simhei'],
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
    import os
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
def fix_random_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cuda.matmul.allow_tf32 = False
def repair_solution(self,decoded: dict, max_time: float = 1.0, step: float = 0.01) -> dict:
    """
    将一个解拉回可行域，返回改后的解。
    参数:
        decoded: dict, 原始解
        max_time: float, 最大修复时间（秒）
        step: float, 实数变量每次调整步长
    返回:
        dict, 修复后的解
    """
    start_time = time.time()
    repaired = {k: v.copy() for k, v in decoded.items()}

    # 变量类型索引
    var_info = {}
    idx = 0
    for vtype, info in self.var_types:
        if vtype == "binary":
            var_info.update({i: ("binary", None) for i in range(idx, idx + info)})
            idx += info
        elif vtype == "integer":
            n, low, high = info
            var_info.update({i: ("integer", (low, high)) for i in range(idx, idx + n)})
            idx += n
        elif vtype == "real":
            n, low, high = info
            var_info.update({i: ("real", (low, high)) for i in range(idx, idx + n)})
            idx += n

    while time.time() - start_time < max_time:
        violation_total = 0.0

        # 检查不等式约束
        for h in self.ineq_constraints:
            h_val = h(repaired)
            if h_val > 0:
                violation_total += h_val
                for k, arr in repaired.items():
                    for i in range(len(arr)):
                        vtype, bounds = var_info[i]
                        if vtype == "real":
                            arr[i] -= np.sign(h_val) * step
                            # 保证变量边界
                            arr[i] = np.clip(arr[i], bounds[0], bounds[1])
                        elif vtype == "integer":
                            arr[i] -= int(np.sign(h_val))
                            arr[i] = int(np.clip(arr[i], bounds[0], bounds[1]))
                        # binary 也可处理
                        elif vtype == "binary":
                            arr[i] = 1 - arr[i]

        # 检查等式约束
        for g in self.eq_constraints:
            g_val = g(repaired)
            if abs(g_val) > 1e-6:
                violation_total += abs(g_val)
                for k, arr in repaired.items():
                    for i in range(len(arr)):
                        vtype, bounds = var_info[i]
                        if vtype == "real":
                            arr[i] -= np.sign(g_val) * step
                            arr[i] = np.clip(arr[i], bounds[0], bounds[1])
                        elif vtype == "integer":
                            arr[i] -= int(np.sign(g_val))
                            arr[i] = int(np.clip(arr[i], bounds[0], bounds[1]))
                        elif vtype == "binary":
                            arr[i] = 1 - arr[i]

        if violation_total == 0:
            break

    return repaired
def is_decoded_feasible(self,decoded: dict, tol: float = 1e-6) -> bool:
    """
    检查给定解是否满足约束条件。
    参数:
        decoded: dict, 解的字典形式
        tol: float, 等式约束容忍误差
    返回:
        bool, True 表示可行，False 表示不可行
    """
    # 检查不等式约束 h(x) <= 0
    for h in self.ineq_constraints:
        if h(decoded) > tol:
            return False

    # 检查等式约束 g(x) = 0
    for g in self.eq_constraints:
        if abs(g(decoded)) > tol:
            return False

    return True
def penalty_fun(gen,penalty_coeff, max_gen) -> dict:
    return penalty_coeff * (1 + gen / max_gen) ** 2