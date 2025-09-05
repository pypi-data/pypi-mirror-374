#鲸鱼优化算法
import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from operators import decode,init_mlp  # 复用解析函数
import matplotlib as mpl

# ================= 个体类（单目标场景）=================
class Whale:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（位置向量）
        self.fitness = None  # 适应度值（越大越好）

    def __str__(self) -> str:
        return f"fitness={self.fitness:.6f}" if self.fitness is not None else "fitness=None"


# ================= 鲸鱼优化算法（WOA）类 =================
class WOA:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回适应度
            pop_size: int = 30,
            max_gen: int = 100,
            a_decrease: float = 2.0,  # 系数a的初始值（随迭代线性下降到0）
            b: float = 1.0  # 螺旋形状参数（固定为1）
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.a_decrease = a_decrease  # a从该值线性下降到0
        self.b = b  # 螺旋参数

        # 解析变量范围（用于位置更新时约束）
        self.var_ranges = []  # 存储每个变量的范围：(类型, 下界, 上界)
        self.dim = 0  # 总变量数
        for vtype, info in var_types:
            if vtype == "binary":
                n = info
                self.dim += n
                self.var_ranges.extend([(vtype, 0, 1)] * n)  # 二进制变量范围[0,1]
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

    def init_whale(self) -> Whale:
        """初始化鲸鱼个体（随机位置）"""
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
        return Whale(np.array(chrom, dtype=float))

    def bound_position(self, chrom: np.ndarray) -> np.ndarray:
        """将位置约束在变量范围内（处理越界）"""
        bounded = chrom.copy()
        for i in range(self.dim):
            vtype, low, high = self.var_ranges[i]
            if bounded[i] < low:
                bounded[i] = low
            elif bounded[i] > high:
                bounded[i] = high
            # 对整数/二进制变量进行类型转换
            if vtype == "integer":
                bounded[i] = round(bounded[i])
            elif vtype == "binary":
                bounded[i] = 1 if bounded[i] >= 0.5 else 0
        return bounded

    def update_position(self, whale: Whale, best_whale: Whale, a: float) -> Whale:
        """
        更新鲸鱼位置（WOA核心操作）
        包含三种行为：包围猎物、气泡网攻击（收缩包围+螺旋更新）、搜索猎物
        """
        r1 = random.random()  # [0,1]随机数
        r2 = random.random()  # [0,1]随机数
        A = 2 * a * r1 - a    # 系数A（随a线性下降）
        C = 2 * r2            # 系数C

        p = random.random()   # 概率阈值（决定行为模式）
        l = random.uniform(-1, 1)  # 螺旋参数

        if p < 0.5:
            # 情况1：包围猎物或搜索猎物（|A| < 1 时包围，|A| ≥ 1 时搜索）
            if abs(A) < 1:
                # 包围猎物：向最优个体移动
                D = abs(C * best_whale.chrom - whale.chrom)
                new_chrom = best_whale.chrom - A * D
            else:
                # 搜索猎物：随机选择一个个体作为目标
                rand_whale = random.choice(self.population)
                D = abs(C * rand_whale.chrom - whale.chrom)
                new_chrom = rand_whale.chrom - A * D
        else:
            # 情况2：螺旋更新（模拟鲸鱼螺旋状包围）
            D = abs(best_whale.chrom - whale.chrom)
            new_chrom = D * np.exp(self.b * l) * np.cos(2 * np.pi * l) + best_whale.chrom

        # 约束位置并返回新个体
        bounded_chrom = self.bound_position(new_chrom)
        return Whale(bounded_chrom)

    def run(self) -> Whale:
        """运行鲸鱼优化算法"""
        # 初始化种群
        self.population = [self.init_whale() for _ in range(self.pop_size)]
        for whale in self.population:
            decoded = decode(whale.chrom, self.var_types)
            whale.fitness = self.evaluate(decoded)

        # 初始化最优个体
        best_whale = max(self.population, key=lambda x: x.fitness)

        # 记录初始状态
        self._record_fitness()

        # 迭代优化
        for gen in range(self.max_gen):
            # 计算当前a值（线性下降）
            a = self.a_decrease - (self.a_decrease / self.max_gen) * gen

            # 更新每个鲸鱼的位置
            for i in range(self.pop_size):
                new_whale = self.update_position(self.population[i], best_whale, a)
                # 计算新位置的适应度
                decoded = decode(new_whale.chrom, self.var_types)
                new_whale.fitness = self.evaluate(decoded)
                # 替换原个体
                self.population[i] = new_whale

            # 更新全局最优
            current_best = max(self.population, key=lambda x: x.fitness)
            if current_best.fitness > best_whale.fitness:
                best_whale = current_best

            # 记录当前代信息
            self._record_fitness()

            # 打印进度
            if (gen + 1) % 10 == 0:
                print(f"第{gen+1}/{self.max_gen}代 | 最优适应度: {best_whale.fitness:.6f} | 平均适应度: {self.avg_fitness_history[-1]:.6f}")

        return best_whale

    def _record_fitness(self):
        """记录当前代的适应度统计信息"""
        fitness_values = [whale.fitness for whale in self.population]
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
        plt.title('鲸鱼优化算法适应度变化曲线', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=10)
        plt.tight_layout()
        plt.show()


# ================= 使用示例 =================
if __name__ == "__main__":
    init_mlp()
    var_types = [("real", (2, -5.12, 5.12))]


    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return -(20 + x ** 2 + y ** 2 - 10 * np.cos(2 * np.pi * x) - 10 * np.cos(2 * np.pi * y))

    # 初始化WOA
    algorithm = WOA(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=30,
        max_gen=100,
        a_decrease=2.0,
        b=1.0
    )

    # 运行算法
    best_solution = algorithm.run()

    # 解析最优解
    best_decoded = decode(best_solution.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]
    # 计算原始函数的最小值（因为evaluate返回的是负数，所以取反）
    min_value = -(best_solution.fitness)

    # 输出结果
    print("========== 优化结果 ==========")
    print(f"最优变量值：x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"函数最小值：{min_value:.6f}")

    # 绘制适应度曲线
    algorithm.plot_fitness_curve()