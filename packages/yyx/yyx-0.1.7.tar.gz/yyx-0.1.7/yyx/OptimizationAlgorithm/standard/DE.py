#差分进化算法
import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from operators import decode,init_mlp  # 复用解析函数


# ================= 个体类（单目标场景）=================
class DESolution:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（解向量）
        self.fitness = None  # 适应度值（越大越好）

    def __str__(self) -> str:
        return f"fitness={self.fitness:.6f}" if self.fitness is not None else "fitness=None"


# ================= 差分进化算法（DE）类 =================
class DE:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回适应度
            pop_size: int = 50,
            max_gen: int = 100,
            f: float = 0.5,  # 缩放因子（差分权重）
            cr: float = 0.9,  # 交叉概率
            strategy: str = "rand/1/bin"  # 变异策略
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.f = f  # 缩放因子（通常0.4-1.0）
        self.cr = cr  # 交叉概率（通常0.1-1.0）
        self.strategy = strategy  # 变异策略

        # 解析变量范围（用于边界处理）
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
        self.avg_fitness_history = []  # 每代平均适应度

    def init_solution(self) -> DESolution:
        """初始化个体（随机解）"""
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
        return DESolution(np.array(chrom, dtype=float))

    def bound_handler(self, chrom: np.ndarray) -> np.ndarray:
        """边界处理（将越界变量拉回范围内）"""
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

    def mutate(self, target: DESolution, population: List[DESolution]) -> np.ndarray:
        """变异操作（生成变异向量）"""
        # 选择3个不同的随机个体
        while True:
            r1, r2, r3 = random.sample(range(self.pop_size), 3)
            if r1 != target and r2 != target and r3 != target:
                break

        x1 = population[r1].chrom
        x2 = population[r2].chrom
        x3 = population[r3].chrom

        # 基本变异策略：rand/1
        return x1 + self.f * (x2 - x3)

    def crossover(self, target: np.ndarray, mutant: np.ndarray) -> np.ndarray:
        """交叉操作（生成试验向量）"""
        trial = target.copy()
        # 随机选择一个维度确保至少有一个维度来自变异向量
        j_rand = random.randint(0, self.dim - 1)

        for j in range(self.dim):
            if random.random() < self.cr or j == j_rand:
                trial[j] = mutant[j]
        return trial

    def select(self, target: DESolution, trial: DESolution) -> DESolution:
        """选择操作（贪婪选择）"""
        return trial if trial.fitness > target.fitness else target

    def run(self) -> DESolution:
        """运行差分进化算法"""
        # 初始化种群
        population = [self.init_solution() for _ in range(self.pop_size)]
        for sol in population:
            decoded = decode(sol.chrom, self.var_types)
            sol.fitness = self.evaluate(decoded)

        # 记录初始状态
        self._record_fitness(population)

        # 迭代优化
        for gen in range(self.max_gen):
            # 生成新种群
            new_population = []
            for i in range(self.pop_size):
                target = population[i]

                # 1. 变异
                mutant = self.mutate(i, population)

                # 2. 交叉
                trial_chrom = self.crossover(target.chrom, mutant)
                trial_chrom = self.bound_handler(trial_chrom)
                trial = DESolution(trial_chrom)

                # 计算试验向量适应度
                decoded = decode(trial.chrom, self.var_types)
                trial.fitness = self.evaluate(decoded)

                # 3. 选择
                new_population.append(self.select(target, trial))

            # 更新种群
            population = new_population

            # 记录当前代信息
            self._record_fitness(population)

            # 打印进度
            if (gen + 1) % 10 == 0:
                best_fitness = self.best_fitness_history[-1]
                avg_fitness = self.avg_fitness_history[-1]
                print(f"第{gen + 1}/{self.max_gen}代 | 最优适应度: {best_fitness:.6f} | 平均适应度: {avg_fitness:.6f}")

        # 返回最优个体
        return max(population, key=lambda x: x.fitness)

    def _record_fitness(self, population: List[DESolution]):
        """记录适应度统计信息"""
        fitness_values = [sol.fitness for sol in population]
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
        plt.title('差分进化算法适应度变化曲线', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=10)
        plt.tight_layout()
        plt.show()


# ================= 统一问题测试 =================
if __name__ == "__main__":
    init_mlp()

    # 1. 变量定义（统一问题：2个实数变量，范围[-5.12, 5.12]）
    var_types = [("real", (2, -5.12, 5.12))]


    # 2. 目标函数（Rastrigin函数，求最小值，转为适应度越大越好）
    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]
        # 原始函数：20 + x² + y² - 10cos(2πx) - 10cos(2πy)，最小值0
        return -(20 + x ** 2 + y ** 2 - 10 * np.cos(2 * np.pi * x) - 10 * np.cos(2 * np.pi * y))


    # 3. 初始化DE算法
    de = DE(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=50,
        max_gen=100,
        f=0.5,  # 缩放因子
        cr=0.9  # 交叉概率
    )

    # 4. 运行算法
    best_solution = de.run()

    # 5. 解析并输出结果
    best_decoded = decode(best_solution.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]
    # 转换为原始函数的最小值
    min_value = -(best_solution.fitness)

    print("\n========== 优化结果 ==========")
    print(f"最优变量值：x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"Rastrigin函数最小值：{min_value:.6f}")  # 理论最小值为0

    # 6. 绘制适应度曲线
    de.plot_fitness_curve()
