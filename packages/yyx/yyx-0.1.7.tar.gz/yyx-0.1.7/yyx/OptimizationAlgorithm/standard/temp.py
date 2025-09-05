import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from utils import universal_crossover, universal_mutate, decode  # 导入通用算子


# ================= 个体类 =================
class Solution:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体
        self.fitness = None  # 单目标适应度值
        self.violation = 0.0  # 约束违反量（默认0）

    def __eq__(self, other):
        return np.array_equal(self.chrom, other.chrom)

    def __str__(self) -> str:
        return f"fitness={self.fitness:.6f}, violation={self.violation:.6f}" if self.fitness is not None else "fitness=None"


# ================= 单目标遗传算法（GA）类 =================
class GA:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数
            pop_size: int = 50,
            max_gen: int = 100,
            crossover_prob: float = 0.9,
            mutation_prob: float = 0.05,
            sbx_eta: int = 15,
            elitism_ratio: float = 0.1,
            maximize: bool = True,
            eq_constraints: List[Callable[[dict], float]] = None,  # 等式约束
            ineq_constraints: List[Callable[[dict], float]] = None,  # 不等式约束
            penalty_coeff: float = 1e4  # 罚函数系数
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.sbx_eta = sbx_eta
        self.elitism_ratio = elitism_ratio
        self.elitism_size = max(1, int(pop_size * elitism_ratio))
        self.maximize = maximize
        self.eq_constraints = eq_constraints or []
        self.ineq_constraints = ineq_constraints or []
        self.penalty_coeff = penalty_coeff

        # 计算染色体长度
        self.chrom_length = 0
        for vtype, info in var_types:
            if vtype == "binary":
                self.chrom_length += info
            else:
                self.chrom_length += info[0]

        # 历史记录
        self.best_fitness_history = []   # 每代最优适应度
        self.avg_fitness_history = []    # 每代平均适应度
        self.avg_violation_history = []  # 每代平均约束违反量

    def init_solution(self) -> Solution:
        chrom = []
        for vtype, info in self.var_types:
            if vtype == "binary":
                chrom.extend(np.random.randint(0, 2, size=info))
            elif vtype == "integer":
                n, low, high = info
                chrom.extend(np.random.randint(low, high + 1, size=n))
            elif vtype == "real":
                n, low, high = info
                chrom.extend(np.random.uniform(low, high, size=n))
        return Solution(np.array(chrom, dtype=float))

    def _penalized_fitness(self, decoded: dict) -> Tuple[float, float]:
        """计算带罚项的适应度和违反量"""
        f_val = self.evaluate(decoded)
        violation = 0.0

        # 等式约束 |g(x)| <= 1e-6
        for g in self.eq_constraints:
            violation += abs(g(decoded))

        # 不等式约束 h(x) <= 0
        for h in self.ineq_constraints:
            violation += max(0.0, h(decoded))

        penalized = f_val - self.penalty_coeff * violation
        return penalized, violation

    def select(self, population: List[Solution]) -> List[Solution]:
        fitness_values = np.array([sol.fitness for sol in population])
        if not self.maximize:
            adjusted_fitness = np.max(fitness_values) - fitness_values
        else:
            adjusted_fitness = fitness_values
        min_adj = np.min(adjusted_fitness)
        if min_adj < 0:
            adjusted_fitness += -min_adj
        total_fitness = np.sum(adjusted_fitness)
        if total_fitness == 0:
            return random.choices(population, k=self.pop_size - self.elitism_size)

        selected = []
        while len(selected) < self.pop_size - self.elitism_size:
            r = random.uniform(0, total_fitness)
            cumulative = 0
            for i, sol in enumerate(population):
                cumulative += adjusted_fitness[i]
                if cumulative >= r:
                    selected.append(sol)
                    break
        return selected

    def run(self) -> Solution:
        population = [self.init_solution() for _ in range(self.pop_size)]

        # 初始适应度
        for sol in population:
            decoded = decode(sol.chrom, self.var_types)
            sol.fitness, sol.violation = self._penalized_fitness(decoded)

        self._record(population)

        for gen in range(self.max_gen):
            # 精英保留
            if self.maximize:
                elites = sorted(population, key=lambda x: x.fitness, reverse=True)[:self.elitism_size]
            else:
                elites = sorted(population, key=lambda x: x.fitness)[:self.elitism_size]

            # 选择
            parents = self.select(population)

            # 交叉变异
            offspring = []
            while len(offspring) < self.pop_size - self.elitism_size:
                p1, p2 = random.sample(parents, 2)
                c1, c2 = universal_crossover(
                    p1.chrom, p2.chrom,
                    self.var_types,
                    self.sbx_eta,
                    self.crossover_prob
                )
                offspring.append(Solution(universal_mutate(c1, self.var_types, self.mutation_prob)))
                if len(offspring) < self.pop_size - self.elitism_size:
                    offspring.append(Solution(universal_mutate(c2, self.var_types, self.mutation_prob)))

            # 更新适应度
            for sol in offspring:
                decoded = decode(sol.chrom, self.var_types)
                sol.fitness, sol.violation = self._penalized_fitness(decoded)

            population = elites + offspring
            self._record(population)

            # ✅ 保留原有打印 + 增加约束违反量
            print(f'第{gen + 1}/{self.max_gen}代 | '
                  f'最优适应度: {self.best_fitness_history[-1]:.6f} | '
                  f'平均适应度: {self.avg_fitness_history[-1]:.6f} | '
                  f'平均违反量: {self.avg_violation_history[-1]:.6f}')

        return max(population, key=lambda x: x.fitness) if self.maximize else min(population, key=lambda x: x.fitness)

    def _record(self, population: List[Solution]):
        fitness_values = [sol.fitness for sol in population]
        violations = [sol.violation for sol in population]
        if self.maximize:
            self.best_fitness_history.append(np.max(fitness_values))
        else:
            self.best_fitness_history.append(np.min(fitness_values))
        self.avg_fitness_history.append(np.mean(fitness_values))
        self.avg_violation_history.append(np.mean(violations))

    def plot_fitness_curve(self):
        """绘制适应度和约束违反量曲线"""
        plt.figure(figsize=(12, 6))

        # 适应度
        plt.subplot(1, 2, 1)
        plt.plot(self.best_fitness_history, c='red', label='每代最优适应度')
        plt.plot(self.avg_fitness_history, c='blue', linestyle='--', label='每代平均适应度')
        plt.xlabel('迭代次数')
        plt.ylabel('适应度值')
        plt.title('适应度变化曲线')
        plt.grid(True, alpha=0.3)
        plt.legend()

        # 约束违反量
        plt.subplot(1, 2, 2)
        plt.plot(self.avg_violation_history, c='purple', linewidth=2, label='平均违反量')
        plt.xlabel('迭代次数')
        plt.ylabel('平均约束违反量')
        plt.title('约束违反量变化曲线')
        plt.grid(True, alpha=0.3)
        plt.legend()

        plt.tight_layout()
        plt.show()



# ================= 使用示例 =================
if __name__ == "__main__":
    # 设置中文字体
    plt.rcParams["font.family"] = ["SimHei", "sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

    # 1. 定义变量类型（2个实数变量，范围[-2, 2]）
    var_types = [("real", (2, -2, 2))]

    # 2. 定义适应度函数（Rosenbrock函数，最大化问题）
    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]
        # 原函数是最小化问题，这里取负数转为最大化（最优解在(1,1)附近）
        return -((1 - x) ** 2 + 100 * (y - x ** 2) ** 2)

    # 3. 定义约束条件
    def ineq1(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return x**2 + y**2 - 1  # <= 0

    def ineq2(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return 1 - (x + y)  # <= 0  <=>  x+y >= 1

    # 4. 初始化GA
    ga = GA(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=80,
        max_gen=100,
        crossover_prob=0.9,
        mutation_prob=0.05,
        elitism_ratio=0.1,
        eq_constraints=[],           # 无等式约束
        ineq_constraints=[ineq1, ineq2],  # 添加两个强不等式约束
        penalty_coeff=1e3            # 惩罚系数大一点，约束更明显
    )

    # 5. 运行算法
    best_solution = ga.run()

    # 6. 输出结果
    best_decoded = decode(best_solution.chrom, var_types)
    print("\n最优解：")
    print(f"x = {best_decoded['real_0'][0]:.6f}, y = {best_decoded['real_0'][1]:.6f}")
    print(f"最优适应度：{best_solution.fitness:.6f}")
    print(f"违反量：{best_solution.violation:.6f}")

    # 7. 绘制适应度变化曲线 & 约束违反量
    ga.plot_fitness_curve()
