#萤火虫算法
import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from operators import decode, init_mlp  # 复用解析函数和中文设置


# ================= 萤火虫个体类（单目标场景）=================
class Firefly:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（位置向量）
        self.fitness = None  # 适应度值（越大越好）
        self.brightness = None  # 亮度（与适应度正相关）

    def __str__(self) -> str:
        return f"fitness={self.fitness:.6f}, brightness={self.brightness:.6f}" if self.fitness is not None else "fitness=None"


# ================= 萤火虫优化算法（FA）类 =================
class FA:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回适应度
            pop_size: int = 30,
            max_gen: int = 100,
            alpha: float = 0.2,  # 随机扰动系数
            beta0: float = 1.0,  # 最大吸引力
            gamma: float = 1.0   # 光吸收系数
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.alpha = alpha  # 随机扰动系数（控制探索能力）
        self.beta0 = beta0  # 最大吸引力（当距离为0时的吸引力）
        self.gamma = gamma  # 光吸收系数（控制吸引力随距离的衰减）

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

    def init_firefly(self) -> Firefly:
        """初始化萤火虫个体（随机位置）"""
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
        return Firefly(np.array(chrom, dtype=float))

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

    def attractiveness(self, r: float) -> float:
        """计算吸引力（随距离r衰减）"""
        return self.beta0 * np.exp(-self.gamma * r**2)

    def run(self) -> Firefly:
        """运行萤火虫优化算法"""
        # 初始化萤火虫群
        population = [self.init_firefly() for _ in range(self.pop_size)]
        for firefly in population:
            decoded = decode(firefly.chrom, self.var_types)
            firefly.fitness = self.evaluate(decoded)
            firefly.brightness = firefly.fitness  # 亮度与适应度正相关

        # 记录初始状态
        self._record_fitness(population)

        # 迭代优化
        for gen in range(self.max_gen):
            # 对每只萤火虫，向更亮的萤火虫移动
            for i in range(self.pop_size):
                for j in range(self.pop_size):
                    if population[j].brightness > population[i].brightness:
                        # 计算距离
                        r = np.linalg.norm(population[i].chrom - population[j].chrom)
                        # 计算吸引力
                        beta = self.attractiveness(r)
                        # 计算随机扰动
                        rand = np.random.uniform(-1, 1, self.dim)
                        # 更新位置
                        new_chrom = population[i].chrom + beta * (population[j].chrom - population[i].chrom) + self.alpha * rand
                        new_chrom = self.bound_position(new_chrom)
                        # 评估新位置
                        new_firefly = Firefly(new_chrom)
                        decoded = decode(new_firefly.chrom, self.var_types)
                        new_firefly.fitness = self.evaluate(decoded)
                        new_firefly.brightness = new_firefly.fitness
                        # 贪婪选择：若新位置更优则替换
                        if new_firefly.fitness > population[i].fitness:
                            population[i] = new_firefly

            # 记录当前代信息
            self._record_fitness(population)

            # 打印进度
            if (gen + 1) % 10 == 0:
                best_fitness = self.best_fitness_history[-1]
                avg_fitness = self.avg_fitness_history[-1]
                print(f"第{gen+1}/{self.max_gen}代 | 最优适应度: {best_fitness:.6f} | 平均适应度: {avg_fitness:.6f}")

        # 返回最优个体
        return max(population, key=lambda x: x.fitness)

    def _record_fitness(self, population: List[Firefly]):
        """记录适应度统计信息"""
        fitness_values = [firefly.fitness for firefly in population]
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
        plt.title('萤火虫优化算法适应度变化曲线', fontsize=14)
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

    # 3. 初始化FA算法
    fa = FA(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=30,
        max_gen=300,
        alpha=0.2,
        beta0=1.0,
        gamma=1.0
    )

    # 4. 运行算法
    best_firefly = fa.run()

    # 5. 解析并输出结果
    best_decoded = decode(best_firefly.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]
    # 转换为原始函数的最小值
    min_value = -(best_firefly.fitness)

    print("\n========== 优化结果 ==========")
    print(f"最优变量值：x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"Rastrigin函数最小值：{min_value:.6f}")  # 理论最小值为0

    # 6. 绘制适应度曲线
    fa.plot_fitness_curve()