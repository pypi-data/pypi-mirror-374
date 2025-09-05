#天牛须算法
import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from operators import decode, init_mlp  # 复用解析函数和中文设置


# ================= 天牛个体类（单目标场景）=================
class Beetle:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（位置向量）
        self.fitness = None  # 适应度值（越大越好）
        self.step = None     # 步长（动态调整）

    def __str__(self) -> str:
        return f"fitness={self.fitness:.6f}, step={self.step:.6f}" if self.fitness is not None else "fitness=None"


# ================= 天牛须算法（BAS）类 =================
class BAS:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回适应度
            pop_size: int = 1,  # BAS通常是单个体搜索，也可扩展为种群
            max_gen: int = 100,
            step_init: float = 1.0,  # 初始步长
            step_decay: float = 0.95,  # 步长衰减系数
            antenna_len: float = 0.5  # 触角长度（相对于步长的比例）
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = pop_size  # 可设置为1（标准BAS）或更大值（改进版）
        self.max_gen = max_gen
        self.step_init = step_init  # 初始步长
        self.step_decay = step_decay  # 步长衰减系数（每代乘以该值）
        self.antenna_len = antenna_len  # 触角长度 = antenna_len * 当前步长

        # 解析变量范围（用于位置更新和约束）
        self.var_ranges = []  # 存储每个变量的范围：(类型, 下界, 上界)
        self.dim = 0  # 总变量数
        for vtype, info in var_types:
            if vtype == "binary":
                n = info
                self.dim += n
                self.var_ranges.extend([(vtype, 0, 1)] * n)
            elif vtype == "integer":
                n, low, high = info
                self.dim += n
                self.var_ranges.extend([(vtype, low, high)] * n)
            elif vtype == "real":
                n, low, high = info
                self.dim += n
                self.var_ranges.extend([(vtype, low, high)] * n)

        # 记录迭代过程
        self.best_fitness_history = []  # 每代最优适应度
        self.avg_fitness_history = []   # 每代平均适应度

    def init_beetle(self) -> Beetle:
        """初始化天牛个体（随机位置）"""
        chrom = []
        for vtype, info in self.var_types:
            if vtype == "binary":
                n = info
                chrom.extend(np.random.randint(0, 2, size=n))
            elif vtype == "integer":
                n, low, high = info
                chrom.extend(np.random.randint(low, high + 1, size=n))
            elif vtype == "real":
                n, low, high = info
                chrom.extend(np.random.uniform(low, high, size=n))
        beetle = Beetle(np.array(chrom, dtype=float))
        beetle.step = self.step_init  # 初始化步长
        return beetle

    def bound_position(self, chrom: np.ndarray) -> np.ndarray:
        """将位置约束在变量范围内（处理越界）"""
        bounded = chrom.copy()
        for i in range(self.dim):
            vtype, low, high = self.var_ranges[i]
            if bounded[i] < low:
                bounded[i] = low
            elif bounded[i] > high:
                bounded[i] = high
            # 类型转换
            if vtype == "integer":
                bounded[i] = round(bounded[i])
            elif vtype == "binary":
                bounded[i] = 1 if bounded[i] >= 0.5 else 0
        return bounded

    def random_direction(self) -> np.ndarray:
        """生成随机单位方向向量（天牛搜索方向）"""
        dir_vec = np.random.randn(self.dim)  # 标准正态分布
        dir_vec = dir_vec / np.linalg.norm(dir_vec)  # 单位化
        return dir_vec

    def run(self) -> Beetle:
        """运行天牛须算法"""
        # 初始化天牛群（标准BAS为单个体，可扩展为多个）
        population = [self.init_beetle() for _ in range(self.pop_size)]
        for beetle in population:
            decoded = decode(beetle.chrom, self.var_types)
            beetle.fitness = self.evaluate(decoded)

        # 记录初始状态
        self._record_fitness(population)

        # 迭代优化
        for gen in range(self.max_gen):
            # 对每个天牛进行搜索
            for beetle in population:
                # 1. 生成随机方向向量
                dir_vec = self.random_direction()

                # 2. 计算左右触角位置
                len_antenna = self.antenna_len * beetle.step  # 触角长度与步长相关
                x_left = beetle.chrom + dir_vec * len_antenna / 2  # 左触角
                x_right = beetle.chrom - dir_vec * len_antenna / 2  # 右触角

                # 3. 评估左右触角的适应度
                x_left = self.bound_position(x_left)
                x_right = self.bound_position(x_right)
                decoded_left = decode(x_left, self.var_types)
                decoded_right = decode(x_right, self.var_types)
                fit_left = self.evaluate(decoded_left)
                fit_right = self.evaluate(decoded_right)

                # 4. 更新位置：向适应度更高的方向移动
                if fit_left > fit_right:
                    beetle.chrom += dir_vec * beetle.step
                else:
                    beetle.chrom -= dir_vec * beetle.step

                # 5. 边界处理与适应度更新
                beetle.chrom = self.bound_position(beetle.chrom)
                decoded = decode(beetle.chrom, self.var_types)
                beetle.fitness = self.evaluate(decoded)

                # 6. 步长衰减（每代减小）
                beetle.step *= self.step_decay

            # 记录当前代信息
            self._record_fitness(population)

            # 打印进度
            if (gen + 1) % 10 == 0:
                best_fitness = self.best_fitness_history[-1]
                avg_fitness = self.avg_fitness_history[-1]
                print(f"第{gen+1}/{self.max_gen}代 | 最优适应度: {best_fitness:.6f} | 平均适应度: {avg_fitness:.6f}")

        # 返回最优个体
        return max(population, key=lambda x: x.fitness)

    def _record_fitness(self, population: List[Beetle]):
        """记录适应度统计信息"""
        fitness_values = [beetle.fitness for beetle in population]
        self.best_fitness_history.append(max(fitness_values))
        self.avg_fitness_history.append(np.mean(fitness_values))

    def plot_fitness_curve(self):
        """绘制适应度变化曲线"""
        plt.figure(figsize=(10, 6))
        # 最优适应度曲线
        plt.plot(
            range(1, len(self.best_fitness_history) + 1),
            self.best_fitness_history,
            c='red',
            linewidth=2,
            label='每代最优适应度'
        )
        # 平均适应度曲线
        plt.plot(
            range(1, len(self.avg_fitness_history) + 1),
            self.avg_fitness_history,
            c='blue',
            linewidth=2,
            linestyle='--',
            label='每代平均适应度'
        )
        # 图表设置
        plt.xlabel('迭代次数', fontsize=12, color='black')
        plt.ylabel('适应度值', fontsize=12, color='black')
        plt.title('天牛须算法适应度变化曲线', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=10)
        plt.tight_layout()
        plt.show()


# ================= 统一问题测试 =================
if __name__ == "__main__":
    # 初始化中文显示（已封装）
    init_mlp()

    # 1. 变量定义（统一问题：2个实数变量，范围[-5.12, 5.12]）
    var_types = [("real", (2, -5.12, 5.12))]

    # 2. 目标函数（Rastrigin函数，求最小值，转为适应度越大越好）
    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]
        # 原始函数：20 + x² + y² - 10cos(2πx) - 10cos(2πy)，最小值0
        return -(20 + x**2 + y**2 - 10 * np.cos(2 * np.pi * x) - 10 * np.cos(2 * np.pi * y))

    # 3. 初始化BAS算法（可设置pop_size=1为标准BAS，或更大值增强搜索）
    bas = BAS(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=5,  # 采用5个个体的改进版BAS，增强搜索多样性
        max_gen=100,
        step_init=2.0,    # 初始步长（可适当增大）
        step_decay=0.95,  # 步长衰减系数
        antenna_len=0.5   # 触角长度比例
    )

    # 4. 运行算法
    best_beetle = bas.run()

    # 5. 解析并输出结果
    best_decoded = decode(best_beetle.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]
    # 转换为原始函数的最小值
    min_value = -(best_beetle.fitness)

    print("\n========== 优化结果 ==========")
    print(f"最优变量值：x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"Rastrigin函数最小值：{min_value:.6f}")  # 理论最小值为0

    # 6. 绘制适应度曲线
    bas.plot_fitness_curve()
