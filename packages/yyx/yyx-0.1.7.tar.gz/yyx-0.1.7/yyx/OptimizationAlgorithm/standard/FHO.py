#火鹰优化算法
import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from operators import decode, init_mlp  # 复用解析函数和中文设置


# ================= 火鹰个体类（单目标场景）=================
class FireHawk:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（位置向量）
        self.fitness = None  # 适应度值（越大越好）
        self.intensity = None  # 火焰强度（与适应度相关，影响群体交互）

    def __str__(self) -> str:
        return f"fitness={self.fitness:.6f}, intensity={self.intensity:.6f}" if self.fitness is not None else "fitness=None"


# ================= 火鹰算法（FHO）类 =================
class FHO:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回适应度
            pop_size: int = 30,
            max_gen: int = 100,
            alpha: float = 0.5,  # 火焰扩散系数
            beta: float = 0.3,  # 热气流影响系数
            gamma: float = 0.2  # 随机扰动系数
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.alpha = alpha  # 控制火焰扩散范围
        self.beta = beta  # 控制热气流对位置的影响
        self.gamma = gamma  # 控制随机探索的强度

        # 解析变量范围（用于位置更新和约束）
        self.var_ranges = []  # 存储每个变量的范围：(类型, 下界, 上界)
        self.dim = 0  # 总变量数
        self.low = []  # 所有变量的下界
        self.high = []  # 所有变量的上界
        for vtype, info in var_types:
            if vtype == "binary":
                n = info
                self.dim += n
                self.var_ranges.extend([(vtype, 0, 1)] * n)
                self.low.extend([0] * n)
                self.high.extend([1] * n)
            elif vtype == "integer":
                n, low, high = info
                self.dim += n
                self.var_ranges.extend([(vtype, low, high)] * n)
                self.low.extend([low] * n)
                self.high.extend([high] * n)
            elif vtype == "real":
                n, low, high = info
                self.dim += n
                self.var_ranges.extend([(vtype, low, high)] * n)
                self.low.extend([low] * n)
                self.high.extend([high] * n)
        self.low = np.array(self.low)
        self.high = np.array(self.high)

        # 记录迭代过程
        self.best_fitness_history = []  # 每代最优适应度
        self.avg_fitness_history = []  # 每代平均适应度

    def init_firehawk(self) -> FireHawk:
        """初始化火鹰个体（随机位置）"""
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
        firehawk = FireHawk(np.array(chrom, dtype=float))
        # 初始化火焰强度（后续会根据适应度更新）
        firehawk.intensity = random.random()
        return firehawk

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

    def update_intensity(self, population: List[FireHawk]):
        """根据适应度更新火焰强度（适应度越高，强度越大）"""
        fitness_values = np.array([hawk.fitness for hawk in population])
        min_fit, max_fit = np.min(fitness_values), np.max(fitness_values)
        if max_fit == min_fit:
            for hawk in population:
                hawk.intensity = 0.5
        else:
            for hawk in population:
                # 归一化到[0.1, 0.9]范围，避免强度为0
                hawk.intensity = 0.1 + 0.8 * (hawk.fitness - min_fit) / (max_fit - min_fit)

    def run(self) -> FireHawk:
        """运行火鹰优化算法"""
        # 初始化火鹰种群
        population = [self.init_firehawk() for _ in range(self.pop_size)]
        for hawk in population:
            decoded = decode(hawk.chrom, self.var_types)
            hawk.fitness = self.evaluate(decoded)
        self.update_intensity(population)

        # 记录初始状态
        self._record_fitness(population)

        # 迭代优化
        for gen in range(self.max_gen):
            # 1. 确定当前最优个体（火焰源）
            best_hawk = max(population, key=lambda x: x.fitness)
            best_chrom = best_hawk.chrom.copy()

            # 2. 模拟热气流和火焰扩散，更新每个火鹰的位置
            for i in range(self.pop_size):
                current = population[i]

                # a. 火焰扩散：向最优个体靠近，受自身强度影响
                flame_diffusion = self.alpha * current.intensity * (best_chrom - current.chrom)

                # b. 热气流影响：基于变量范围的随机扰动
                thermal_current = self.beta * (self.high - self.low) * np.random.randn(self.dim)

                # c. 随机探索：模拟火鹰的随机搜索行为
                random_explore = self.gamma * (np.random.rand(self.dim) - 0.5) * (self.high - self.low)

                # d. 综合更新位置
                new_chrom = current.chrom + flame_diffusion + thermal_current + random_explore
                new_chrom = self.bound_position(new_chrom)

                # 3. 贪婪选择：若新位置更优则更新
                new_hawk = FireHawk(new_chrom)
                decoded = decode(new_hawk.chrom, self.var_types)
                new_hawk.fitness = self.evaluate(decoded)

                if new_hawk.fitness > current.fitness:
                    population[i] = new_hawk

            # 4. 更新火焰强度
            self.update_intensity(population)

            # 5. 记录当前代信息
            self._record_fitness(population)

            # 6. 打印进度
            if (gen + 1) % 10 == 0:
                best_fitness = self.best_fitness_history[-1]
                avg_fitness = self.avg_fitness_history[-1]
                print(f"第{gen + 1}/{self.max_gen}代 | 最优适应度: {best_fitness:.6f} | 平均适应度: {avg_fitness:.6f}")

        # 返回最优个体
        return max(population, key=lambda x: x.fitness)

    def _record_fitness(self, population: List[FireHawk]):
        """记录适应度统计信息"""
        fitness_values = [hawk.fitness for hawk in population]
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
        plt.title('火鹰算法适应度变化曲线', fontsize=14)
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


    # 3. 初始化FHO算法
    fho = FHO(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=30,
        max_gen=100,
        alpha=0.5,
        beta=0.3,
        gamma=0.2
    )

    # 4. 运行算法
    best_hawk = fho.run()

    # 5. 解析并输出结果
    best_decoded = decode(best_hawk.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]
    # 转换为原始函数的最小值
    min_value = -(best_hawk.fitness)

    print("\n========== 优化结果 ==========")
    print(f"最优变量值：x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"Rastrigin函数最小值：{min_value:.6f}")  # 理论最小值为0

    # 6. 绘制适应度曲线
    fho.plot_fitness_curve()