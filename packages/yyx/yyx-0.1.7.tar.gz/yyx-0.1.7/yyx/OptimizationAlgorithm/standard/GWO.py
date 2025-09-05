#灰狼优化算法
import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from .operators import decode, init_mlp  # 复用解析函数和中文设置


# ================= 灰狼个体类（单目标场景）=================
class GreyWolf:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（位置向量）
        self.fitness = None  # 适应度值（越大越好）

    def __str__(self) -> str:
        return f"fitness={self.fitness:.6f}" if self.fitness is not None else "fitness=None"


# ================= 灰狼优化算法（GWO）类 =================
class GWO:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回适应度
            pop_size: int = 30,
            max_gen: int = 100,
            a_decrease: float = 2.0  # 系数a的初始值（随迭代线性下降到0）
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = pop_size if pop_size >= 3 else 3  # 确保至少有3只灰狼（α, β, δ）
        self.max_gen = max_gen
        self.a_decrease = a_decrease  # a从该值线性下降到0

        # 解析变量范围（用于位置约束）
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
        self.best_fitness_history = []  # 每代最优适应度（α狼的适应度）
        self.avg_fitness_history = []  # 每代平均适应度

    def init_wolf(self) -> GreyWolf:
        """初始化灰狼个体（随机位置）"""
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
        return GreyWolf(np.array(chrom, dtype=float))

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

    def run(self) -> GreyWolf:
        """运行灰狼优化算法"""
        # 初始化种群
        population = [self.init_wolf() for _ in range(self.pop_size)]
        for wolf in population:
            decoded = decode(wolf.chrom, self.var_types)
            wolf.fitness = self.evaluate(decoded)

        # 记录初始状态
        self._record_fitness(population)

        # 迭代优化
        for gen in range(self.max_gen):
            # 计算当前a值（线性下降）
            a = self.a_decrease - (self.a_decrease / self.max_gen) * gen

            # 排序种群，选出α(最优)、β(次优)、δ(第三优)
            sorted_pop = sorted(population, key=lambda x: x.fitness, reverse=True)
            alpha, beta, delta = sorted_pop[0], sorted_pop[1], sorted_pop[2]

            # 更新每只灰狼的位置
            for i in range(self.pop_size):
                # 对α、β、δ分别计算距离和位置向量
                r1, r2 = random.random(), random.random()
                A1 = 2 * a * r1 - a  # α的系数A
                C1 = 2 * r2  # α的系数C
                D_alpha = abs(C1 * alpha.chrom - population[i].chrom)
                X1 = alpha.chrom - A1 * D_alpha

                r1, r2 = random.random(), random.random()
                A2 = 2 * a * r1 - a  # β的系数A
                C2 = 2 * r2  # β的系数C
                D_beta = abs(C2 * beta.chrom - population[i].chrom)
                X2 = beta.chrom - A2 * D_beta

                r1, r2 = random.random(), random.random()
                A3 = 2 * a * r1 - a  # δ的系数A
                C3 = 2 * r2  # δ的系数C
                D_delta = abs(C3 * delta.chrom - population[i].chrom)
                X3 = delta.chrom - A3 * D_delta

                # 新位置 = (X1 + X2 + X3) / 3
                new_chrom = (X1 + X2 + X3) / 3
                new_chrom = self.bound_position(new_chrom)

                # 更新当前灰狼的位置和适应度
                population[i].chrom = new_chrom
                decoded = decode(population[i].chrom, self.var_types)
                population[i].fitness = self.evaluate(decoded)

            # 记录当前代信息
            self._record_fitness(population)

            # 打印进度
            if (gen + 1) % 10 == 0:
                best_fitness = self.best_fitness_history[-1]
                avg_fitness = self.avg_fitness_history[-1]
                print(
                    f"第{gen + 1}/{self.max_gen}代 | 最优适应度(α): {best_fitness:.6f} | 平均适应度: {avg_fitness:.6f}")

        # 返回最优个体（α狼）
        return max(population, key=lambda x: x.fitness)

    def _record_fitness(self, population: List[GreyWolf]):
        """记录适应度统计信息"""
        fitness_values = [wolf.fitness for wolf in population]
        self.best_fitness_history.append(max(fitness_values))
        self.avg_fitness_history.append(np.mean(fitness_values))

    def plot_fitness_curve(self):
        """绘制适应度变化曲线"""
        plt.figure(figsize=(10, 6))
        # 最优适应度曲线（α狼）
        plt.plot(
            range(1, len(self.best_fitness_history) + 1),
            self.best_fitness_history,
            c='red',
            linewidth=2,
            label='每代最优适应度(α)'
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
        plt.title('灰狼优化算法适应度变化曲线', fontsize=14)
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
        return -(20 + x ** 2 + y ** 2 - 10 * np.cos(2 * np.pi * x) - 10 * np.cos(2 * np.pi * y))


    # 3. 初始化GWO算法
    gwo = GWO(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=30,
        max_gen=100,
        a_decrease=2.0
    )

    # 4. 运行算法
    best_wolf = gwo.run()

    # 5. 解析并输出结果
    best_decoded = decode(best_wolf.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]
    # 转换为原始函数的最小值
    min_value = -(best_wolf.fitness)

    print("\n========== 优化结果 ==========")
    print(f"最优变量值：x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"Rastrigin函数最小值：{min_value:.6f}")  # 理论最小值为0

    # 6. 绘制适应度曲线
    gwo.plot_fitness_curve()
