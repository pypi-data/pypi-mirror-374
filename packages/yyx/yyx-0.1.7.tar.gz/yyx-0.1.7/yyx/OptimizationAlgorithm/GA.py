import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from utils import universal_crossover, universal_mutate, decode, init_mlp, fix_random_seed, repair_solution, \
    is_decoded_feasible, penalty_fun
import time


# ================= 个体类 =================
class Solution:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom
        self.fitness = None  # 惩罚后的适应度
        self.raw_fitness = None  # 原始目标值
        self.violation = 0.0  # 约束违反量

    def __eq__(self, other):
        return np.array_equal(self.chrom, other.chrom)

    def __str__(self) -> str:
        return (f"raw={self.raw_fitness:.6f}, fitness={self.fitness:.6f}, "
                f"violation={self.violation:.6f}" if self.fitness is not None else "fitness=None")


# ================= 单目标遗传算法（GA）类 =================
class GA:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],
            pop_size: int = 50,
            max_gen: int = 100,
            crossover_prob: float = 0.9,
            mutation_prob: float = 0.05,
            sbx_eta: int = 15,
            elitism_ratio: float = 0.1,
            maximize: bool = True,
            eq_constraints: List[Callable[[dict], float]] = None,
            ineq_constraints: List[Callable[[dict], float]] = None,
            penalty_coeff: float = 1e3
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

        # 染色体长度
        self.chrom_length = 0
        for vtype, info in var_types:
            if vtype == "binary":
                self.chrom_length += info
            else:
                self.chrom_length += info[0]

        # 历史记录：保留原有适应度记录（最优记录仅用于打印，不影响绘图）
        self.best_fitness_history = []  # 最优惩罚适应度（用于打印）
        self.avg_fitness_history = []  # 平均惩罚适应度（用于绘图）
        self.best_raw_fitness_history = []  # 最优原始目标值（用于打印）
        self.avg_raw_fitness_history = []  # 平均原始目标值（用于绘图）
        self.avg_violation_history = []  # 平均约束违反量（用于绘图）

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

    def _penalized_fitness(self, decoded: dict, gen: int) -> Tuple[float, float, float]:
        """返回 (惩罚后适应度, 原始目标值, 违反量)"""
        raw_val = self.evaluate(decoded)
        violation = 0.0

        # 等式约束
        for g in self.eq_constraints:
            violation += abs(g(decoded))

        # 不等式约束
        for h in self.ineq_constraints:
            violation += max(0.0, h(decoded))
        # 自适应罚函数
        adaptive_coeff = penalty_fun(gen, self.penalty_coeff, self.max_gen)
        penalized = raw_val - adaptive_coeff * violation

        if gen % 10 == 0:
            print(f"调试: raw_val={raw_val:.4f}, violation={violation:.4f}, coeff={adaptive_coeff:.4f}")

        return penalized, raw_val, violation

    def select(self, population: List[Solution]) -> List[Solution]:
        fitness_values = np.array([sol.fitness for sol in population])
        if not self.maximize:
            adjusted = np.max(fitness_values) - fitness_values
        else:
            adjusted = fitness_values.copy()
        min_adj = np.min(adjusted)
        if min_adj < 0:
            adjusted += -min_adj
        total = np.sum(adjusted)
        if total == 0:
            return random.choices(population, k=self.pop_size - self.elitism_size)

        selected = []
        while len(selected) < self.pop_size - self.elitism_size:
            r = random.uniform(0, total)
            cum = 0
            for i, sol in enumerate(population):
                cum += adjusted[i]
                if cum >= r:
                    selected.append(sol)
                    break
        return selected

    def run(self) -> Solution:
        population = [self.init_solution() for _ in range(self.pop_size)]

        # 初始适应度计算
        for sol in population:
            decoded = decode(sol.chrom, self.var_types)
            penalized, raw_val, violation = self._penalized_fitness(decoded, gen=0)
            sol.fitness = penalized
            sol.raw_fitness = raw_val
            sol.violation = violation

        self._record(population)

        for gen in range(1, self.max_gen + 1):
            # 精英保留
            if self.maximize:
                elites = sorted(population, key=lambda x: x.fitness, reverse=True)[:self.elitism_size]
            else:
                elites = sorted(population, key=lambda x: x.fitness)[:self.elitism_size]

            # 选择、交叉、变异
            parents = self.select(population)
            offspring = []
            while len(offspring) < self.pop_size - self.elitism_size:
                p1, p2 = random.sample(parents, 2)
                c1, c2 = universal_crossover(p1.chrom, p2.chrom, self.var_types, self.sbx_eta, self.crossover_prob)
                offspring.append(Solution(universal_mutate(c1, self.var_types, self.mutation_prob)))
                if len(offspring) < self.pop_size - self.elitism_size:
                    offspring.append(Solution(universal_mutate(c2, self.var_types, self.mutation_prob)))

            # 更新适应度
            for sol in offspring:
                decoded = decode(sol.chrom, self.var_types)
                penalized, raw_val, violation = self._penalized_fitness(decoded, gen)
                sol.fitness = penalized
                sol.raw_fitness = raw_val
                sol.violation = violation

            population = elites + offspring
            self._record(population)

            # 打印信息：保留最优+平均（不影响绘图，仅用于观察）
            print(f'第{gen}/{self.max_gen}代 | '
                  f'最优惩罚适应度: {self.best_fitness_history[-1]:.6f} | '
                  f'最优原始目标值: {self.best_raw_fitness_history[-1]:.6f} | '
                  f'平均适应度: {self.avg_fitness_history[-1]:.6f} | '
                  f'平均违反量: {self.avg_violation_history[-1]:.6f}')

        return max(population, key=lambda x: x.fitness) if self.maximize else min(population, key=lambda x: x.fitness)

    def _record(self, population: List[Solution]):
        fitness_values = [sol.fitness for sol in population]
        raw_fitness_values = [sol.raw_fitness for sol in population]
        violations = [sol.violation for sol in population]

        # 记录最优值（用于打印，不影响绘图）
        if self.maximize:
            self.best_fitness_history.append(np.max(fitness_values))
            self.best_raw_fitness_history.append(np.max(raw_fitness_values))
        else:
            self.best_fitness_history.append(np.min(fitness_values))
            self.best_raw_fitness_history.append(np.min(raw_fitness_values))

        # 记录平均值（用于绘图）
        self.avg_fitness_history.append(np.mean(fitness_values))
        self.avg_raw_fitness_history.append(np.mean(raw_fitness_values))
        self.avg_violation_history.append(np.mean(violations))

    # -------------------------- 核心修改：绘图函数 --------------------------
    def plot_fitness_curve(self):
        plt.figure(figsize=(12, 6))
        # 适应度与原始目标值曲线：仅保留平均线，且改为实线
        plt.subplot(1, 2, 1)
        # 1. 平均惩罚适应度：删除 linestyle='--'（默认实线），或显式写 linestyle='-'
        plt.plot(self.avg_fitness_history, c='blue', label='平均惩罚适应度')
        # 2. 平均原始目标值：同样改为实线
        plt.plot(self.avg_raw_fitness_history, c='orange', label='平均原始目标值')
        # （已删除：最优惩罚适应度、最优原始目标值两条曲线）

        plt.xlabel('迭代次数')
        plt.ylabel('数值')
        plt.title('平均适应度与平均原始目标值变化曲线')  # 标题适配内容
        plt.grid(True, alpha=0.3)
        plt.legend()

        # 约束违反量曲线（保持不变）
        if self.ineq_constraints or self.eq_constraints:
            plt.subplot(1, 2, 2)
            plt.plot(self.avg_violation_history, c='purple', linewidth=2, label='平均违反量')
            plt.xlabel('迭代次数')
            plt.ylabel('平均约束违反量')
            plt.title('约束违反量变化曲线')
            plt.grid(True, alpha=0.3)
            plt.legend()
        plt.tight_layout()
        plt.show()
    # ----------------------------------------------------------------------

    def repair_solution(self, decoded: dict, max_time: float = 1.0, step: float = 0.01) -> dict:
        return repair_solution(self, decoded, max_time, step)

    def is_decoded_feasible(self, decoded, tol=1e-6) -> bool:
        return is_decoded_feasible(self, decoded, tol)


if __name__ == "__main__":
    fix_random_seed()
    init_mlp()
    var_types = [("real", (2, -2, 2))]


    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return -((1 - x) ** 2 + 100 * (y - x ** 2) ** 2)


    def ineq1(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return x + y  # <= 0


    def ineq2(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return x ** 2 + y ** 2 - 0.5  # <= 0


    def ineq3(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return x - y + 0.3  # <= 0


    ga = GA(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=100,
        max_gen=150,
        crossover_prob=0.9,
        mutation_prob=0.08,
        elitism_ratio=0.1,
        eq_constraints=[],
        ineq_constraints=[ineq1, ineq2, ineq3],
        penalty_coeff=1e3
    )

    best_solution = ga.run()
    best_decoded = decode(best_solution.chrom, var_types)
    print("\n最优解：")
    print(f"x = {best_decoded['real_0'][0]:.6f}, y = {best_decoded['real_0'][1]:.6f}")
    print(f"最优惩罚适应度：{best_solution.fitness:.6f}")
    print(f"最优原始目标值：{best_solution.raw_fitness:.6f}")
    print(f"违反量：{best_solution.violation:.6f}")

    ga.plot_fitness_curve()