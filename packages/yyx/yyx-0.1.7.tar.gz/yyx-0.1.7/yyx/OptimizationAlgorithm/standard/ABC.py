#人工蜂群算法
import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from operators import decode, init_mlp  # 复用解析函数和中文设置


# ================= 蜜蜂个体类（单目标场景）=================
class Bee:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（蜜源位置）
        self.fitness = None  # 适应度值（越大越好）
        self.trials = 0  # 尝试次数（用于侦察蜂判断）

    def __str__(self) -> str:
        return f"fitness={self.fitness:.6f}, trials={self.trials}" if self.fitness is not None else "fitness=None"


# ================= 人工蜂群算法（ABC）类 =================
class ABC:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回适应度
            pop_size: int = 30,
            max_gen: int = 100,
            limit: int = 100  # 蜜源放弃阈值
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.limit = limit  # 超过该次数未改进则放弃蜜源

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

    def init_bee(self) -> Bee:
        """初始化蜜蜂个体（随机蜜源位置）"""
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
        return Bee(np.array(chrom, dtype=float))

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

    def run(self) -> Bee:
        """运行人工蜂群算法"""
        # 初始化蜂群（所有蜜蜂均为雇佣蜂）
        population = [self.init_bee() for _ in range(self.pop_size)]
        for bee in population:
            decoded = decode(bee.chrom, self.var_types)
            bee.fitness = self.evaluate(decoded)

        # 记录初始状态
        self._record_fitness(population)

        # 迭代优化
        for gen in range(self.max_gen):
            # 1. 雇佣蜂阶段：更新蜜源并评估
            for i in range(self.pop_size):
                # 随机选择一个不同的蜜源和维度
                while True:
                    k = random.randint(0, self.pop_size - 1)
                    j = random.randint(0, self.dim - 1)
                    if k != i:
                        break

                # 生成新蜜源
                new_chrom = population[i].chrom.copy()
                new_chrom[j] = population[i].chrom[j] + random.uniform(-1, 1) * (
                    population[i].chrom[j] - population[k].chrom[j]
                )
                new_chrom = self.bound_position(new_chrom)

                # 评估新蜜源
                new_bee = Bee(new_chrom)
                decoded = decode(new_bee.chrom, self.var_types)
                new_bee.fitness = self.evaluate(decoded)

                # 贪婪选择：若新蜜源更优则替换
                if new_bee.fitness > population[i].fitness:
                    population[i] = new_bee
                    population[i].trials = 0  # 重置尝试次数
                else:
                    population[i].trials += 1  # 尝试次数加1

            # 2. 观察蜂阶段：基于轮盘赌选择蜜源
            probabilities = [bee.fitness / sum(b.fitness for b in population) for bee in population]
            for i in range(self.pop_size):
                # 轮盘赌选择一个蜜源
                selected = random.choices(range(self.pop_size), weights=probabilities)[0]

                # 随机选择一个不同的蜜源和维度
                while True:
                    k = random.randint(0, self.pop_size - 1)
                    j = random.randint(0, self.dim - 1)
                    if k != selected:
                        break

                # 生成新蜜源
                new_chrom = population[selected].chrom.copy()
                new_chrom[j] = population[selected].chrom[j] + random.uniform(-1, 1) * (
                    population[selected].chrom[j] - population[k].chrom[j]
                )
                new_chrom = self.bound_position(new_chrom)

                # 评估新蜜源
                new_bee = Bee(new_chrom)
                decoded = decode(new_bee.chrom, self.var_types)
                new_bee.fitness = self.evaluate(decoded)

                # 贪婪选择：若新蜜源更优则替换
                if new_bee.fitness > population[selected].fitness:
                    population[selected] = new_bee
                    population[selected].trials = 0  # 重置尝试次数
                else:
                    population[selected].trials += 1  # 尝试次数加1

            # 3. 侦察蜂阶段：放弃超过阈值的蜜源并随机生成新蜜源
            for i in range(self.pop_size):
                if population[i].trials >= self.limit:
                    population[i] = self.init_bee()
                    decoded = decode(population[i].chrom, self.var_types)
                    population[i].fitness = self.evaluate(decoded)
                    population[i].trials = 0  # 重置尝试次数

            # 记录当前代信息
            self._record_fitness(population)

            # 打印进度
            if (gen + 1) % 10 == 0:
                best_fitness = self.best_fitness_history[-1]
                avg_fitness = self.avg_fitness_history[-1]
                print(f"第{gen+1}/{self.max_gen}代 | 最优适应度: {best_fitness:.6f} | 平均适应度: {avg_fitness:.6f}")

        # 返回最优个体
        return max(population, key=lambda x: x.fitness)

    def _record_fitness(self, population: List[Bee]):
        """记录适应度统计信息"""
        fitness_values = [bee.fitness for bee in population]
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
        plt.title('人工蜂群算法适应度变化曲线', fontsize=14)
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

    # 3. 初始化ABC算法
    abc = ABC(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=30,
        max_gen=100,
        limit=100
    )

    # 4. 运行算法
    best_bee = abc.run()

    # 5. 解析并输出结果
    best_decoded = decode(best_bee.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]
    # 转换为原始函数的最小值
    min_value = -(best_bee.fitness)

    print("\n========== 优化结果 ==========")
    print(f"最优变量值：x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"Rastrigin函数最小值：{min_value:.6f}")  # 理论最小值为0

    # 6. 绘制适应度曲线
    abc.plot_fitness_curve()