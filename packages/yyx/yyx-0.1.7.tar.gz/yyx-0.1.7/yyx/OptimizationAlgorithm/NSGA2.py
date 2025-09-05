import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from sklearn.decomposition import PCA
from .utils import universal_crossover, universal_mutate, decode,init_mlp  # 导入通用算子

class Solution:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom
        self.fitness = None
        self.rank = None
        self.crowding_distance = 0
        self.domination_cnt = 0
        self.domination_solutions = []

    def __eq__(self, other):
        return np.array_equal(self.chrom, other.chrom)

    def __str__(self, maximize: List[bool] = None) -> str:
        if self.fitness is None:
            return "fitness=None"
        if maximize is not None:
            assert len(maximize) == len(self.fitness), \
                f"maximize长度需与目标数量一致（{len(self.fitness)}）"
            display_values = [
                -self.fitness[i] if maximize[i] else self.fitness[i]
                for i in range(len(self.fitness))
            ]
            values_str = ", ".join([f"{v:.6f}" for v in display_values])
            return f"fitness=[{values_str}]"
        else:
            values_str = ", ".join([f"{v:.6f}" for v in self.fitness])
            return f"fitness=[{values_str}]"

def dominated(s1: Solution, s2: Solution) -> bool:
    f1_le = np.all(s1.fitness <= s2.fitness + 1e-8)
    f1_lt = np.any(s1.fitness < s2.fitness - 1e-8)
    return f1_le and f1_lt


def non_dominated_sorting(population: List[Solution], evaluate: Callable) -> List[List[Solution]]:
    for sol in population:
        if sol.fitness is None:
            sol.fitness = evaluate(sol.chrom)
        sol.domination_cnt = 0
        sol.domination_solutions = []

    for i in range(len(population)):
        for j in range(len(population)):
            if i == j: continue
            if dominated(population[i], population[j]):
                population[i].domination_solutions.append(population[j])
                population[j].domination_cnt += 1

    fronts = []
    curr_front = [sol for sol in population if sol.domination_cnt == 0]
    while curr_front:
        fronts.append(curr_front)
        next_front = []
        for sol in curr_front:
            for dominate in sol.domination_solutions:
                dominate.domination_cnt -= 1
                if dominate.domination_cnt == 0:
                    next_front.append(dominate)
        curr_front = next_front

    for i, front in enumerate(fronts):
        for sol in front:
            sol.rank = i + 1
    return fronts


def cal_crowding_distance(front: List[Solution]):
    if len(front) <= 1:
        return
    num_obj = len(front[0].fitness)
    for sol in front:
        sol.crowding_distance = 0
    for m in range(num_obj):
        front_sorted = sorted(front, key=lambda x: x.fitness[m])
        front_sorted[0].crowding_distance = front_sorted[-1].crowding_distance = float("inf")
        obj_range = front_sorted[-1].fitness[m] - front_sorted[0].fitness[m]
        if obj_range == 0: continue
        for i in range(1, len(front_sorted) - 1):
            dis = front_sorted[i + 1].fitness[m] - front_sorted[i - 1].fitness[m]
            front_sorted[i].crowding_distance += dis / obj_range


# ================= NSGA2 类（修改后）=================
class NSGA2:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], np.ndarray],  # 新增：目标函数在初始化时传入
            pop_size: int = 50,
            max_gen: int = 100,
            crossover_prob: float = 0.9,
            mutation_prob: float = 0.05,
            sbx_eta: int = 15
    ):
        self.var_types = var_types
        self.evaluate = evaluate  # 保存目标函数
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.sbx_eta = sbx_eta
        self.chrom_length = 0
        for vtype, info in var_types:
            if vtype == "binary":
                self.chrom_length += info
            else:
                self.chrom_length += info[0]

    def init_solution(self):
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
        return Solution(np.array(chrom, dtype=float))

    def run(self):  # 修改：不再需要传入evaluate，直接使用self.evaluate
        population = [self.init_solution() for _ in range(self.pop_size)]
        for gen in range(self.max_gen):
            if (gen+1)%10==0:
                print(f'第{gen+1}/{self.max_gen}代')
            offspring = []
            while len(offspring) < self.pop_size:
                p1, p2 = random.sample(population, 2)
                c1, c2 = universal_crossover(
                    p1.chrom, p2.chrom,
                    self.var_types,
                    self.sbx_eta,
                    self.crossover_prob
                )
                offspring.append(Solution(universal_mutate(c1, self.var_types, self.mutation_prob)))
                if len(offspring) < self.pop_size:
                    offspring.append(Solution(universal_mutate(c2, self.var_types, self.mutation_prob)))
            combined = population + offspring
            # 使用self.evaluate调用目标函数
            fronts = non_dominated_sorting(combined, lambda c: self.evaluate(decode(c, self.var_types)))
            for f in fronts: cal_crowding_distance(f)
            new_pop = []
            for f in fronts:
                if len(new_pop) + len(f) <= self.pop_size:
                    new_pop.extend(f)
                else:
                    sorted_f = sorted(f, key=lambda x: x.crowding_distance, reverse=True)
                    new_pop.extend(sorted_f[:self.pop_size - len(new_pop)])
                    break
            population = new_pop

        # 返回时同样使用self.evaluate
        return non_dominated_sorting(population, lambda c: self.evaluate(decode(c, self.var_types)))[0]

    def plot_pareto_front(self, pareto: List[Solution], maximize: List[bool] = None):
        """
        绘制帕累托前沿，支持指定最大化目标（自动乘以-1）和自定义样式
        参数:
            pareto: 帕累托前沿解列表
            maximize: 布尔列表，指示每个目标是否为最大化（如[True, False]表示第一个目标最大化）
                      若为None，默认所有目标均为最小化（不处理）
        """
        fitness = np.array([sol.fitness for sol in pareto])
        num_obj = fitness.shape[1]

        for sol in pareto:
            print(sol.__str__(maximize))
        if maximize is not None:
            assert len(maximize) == num_obj, f"maximize长度需与目标数量一致（{num_obj}）"
            for i in range(num_obj):
                if maximize[i]:
                    fitness[:, i] = -fitness[:, i]  # 最大化目标还原

        if num_obj == 2:
            plt.figure(figsize=(10, 6))
            plt.scatter(
                fitness[:, 0],
                fitness[:, 1],
                c='blue',
                alpha=0.5,
                s=50,
                label='帕累托前沿'
            )
            plt.xlabel('f1 (商超利润)')
            plt.ylabel('f2 (市场满意度)')
            plt.title('多目标优化问题的帕累托前沿')
            plt.legend()
            plt.grid(True)
            plt.show()

        elif num_obj == 3:
            from mpl_toolkits.mplot3d import Axes3D
            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(
                fitness[:, 0],
                fitness[:, 1],
                fitness[:, 2],
                c='blue',
                alpha=0.5,
                s=50,
                label='帕累托前沿'
            )
            ax.set_xlabel('f1 (目标1)')
            ax.set_ylabel('f2 (目标2)')
            ax.set_zlabel('f3 (目标3)')
            ax.set_title('多目标优化问题的帕累托前沿')
            ax.legend()
            plt.grid(True)
            plt.show()

        else:
            pca = PCA(n_components=2)
            reduced = pca.fit_transform(fitness)
            plt.figure(figsize=(10, 6))
            plt.scatter(
                reduced[:, 0],
                reduced[:, 1],
                c='blue',
                alpha=0.5,
                s=50,
                label='帕累托前沿'
            )
            plt.xlabel('PC1 (主成分1)')
            plt.ylabel('PC2 (主成分2)')
            plt.title('多目标优化问题的帕累托前沿（PCA降维）')
            plt.legend()
            plt.grid(True)
            plt.show()


# ================= 使用示例（修改后）=================
if __name__ == "__main__":
    init_mlp()
    var_types = [
        ("integer", (2, 0, 5)),   # 整数组1
        ("integer", (3, 10, 20)), # 整数组2
        ("real", (2, -1, 1)),     # 实数组1
        ("real", (1, 0, 10)),     # 实数组2
        ("binary", 4)             # 二进制组
    ]

    # 定义目标函数
    def evaluate(decoded):
        x1 = decoded["integer_0"]
        x2 = decoded["integer_1"]
        z1 = decoded["real_0"]
        z2 = decoded["real_1"]
        b = decoded["binary_0"]
        f1 = np.sum(x1) + np.sum(x2) + np.sum(z1**2) + np.sum(z2) + np.sum(b)
        f2 = np.sum((x1 - 2)**2) + np.sum((z1 - 0.5)**2) + np.sum((z2 - 5)**2)
        return np.array([f1, f2])

    # 初始化时传入目标函数evaluate
    nsga2 = NSGA2(
        var_types=var_types,
        evaluate=evaluate,  # 目标函数在这里传入
        pop_size=50,
        max_gen=50
    )

    pareto = nsga2.run()
    nsga2.plot_pareto_front(pareto)

    # 打印前几个解
    for sol in pareto[:5]:
        print(decode(sol.chrom, var_types), sol.fitness)