#模拟退火算法
import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from operators import universal_mutate, decode  # 复用变异算子和解析函数

plt.rcParams["font.family"] = ["SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# ================= 个体类（简化，单目标场景）=================
class Solution:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体
        self.fitness = None  # 单目标适应度值

    def __eq__(self, other):
        return np.array_equal(self.chrom, other.chrom)

    def __str__(self) -> str:
        return f"fitness={self.fitness:.6f}" if self.fitness is not None else "fitness=None"


# ================= 模拟退火算法（SA）类 =================
class SA:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回适应度（越大越好）
            init_temp: float = 100.0,  # 初始温度
            cooling_rate: float = 0.95,  # 冷却速率（每次迭代降温比例）
            max_iter: int = 1000,  # 总迭代次数
            max_stay: int = 100,  # 连续未改进的最大迭代次数（提前终止）
            mutate_prob: float = 0.1  # 变异概率（用于生成邻域解）
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.init_temp = init_temp
        self.cooling_rate = cooling_rate
        self.max_iter = max_iter
        self.max_stay = max_stay
        self.mutate_prob = mutate_prob

        # 计算染色体长度
        self.chrom_length = 0
        for vtype, info in var_types:
            if vtype == "binary":
                self.chrom_length += info
            else:
                self.chrom_length += info[0]

        # 记录迭代过程
        self.best_fitness_history = []  # 每步最优适应度
        self.current_temp_history = []  # 温度变化记录

    def init_solution(self) -> Solution:
        """初始化一个随机解"""
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

    def generate_neighbor(self, current: Solution) -> Solution:
        """生成邻域解（通过变异当前解实现）"""
        new_chrom = universal_mutate(
            current.chrom.copy(),
            self.var_types,
            self.mutate_prob
        )
        return Solution(new_chrom)

    def accept_probability(self, current_fitness: float, new_fitness: float, temp: float) -> float:
        """计算接受新解的概率"""
        if new_fitness > current_fitness:
            return 1.0  # 更优解直接接受
        else:
            # 较差解以一定概率接受（温度越高概率越大）
            return np.exp((new_fitness - current_fitness) / temp)

    def run(self) -> Solution:
        """运行模拟退火算法"""
        # 初始化
        current = self.init_solution()
        decoded = decode(current.chrom, self.var_types)
        current.fitness = self.evaluate(decoded)

        best = current  # 记录全局最优
        temp = self.init_temp
        no_improve_cnt = 0  # 连续未改进计数器

        # 记录初始状态
        self.best_fitness_history.append(best.fitness)
        self.current_temp_history.append(temp)

        # 迭代退火过程
        for iter in range(self.max_iter):
            # 生成邻域解并计算适应度
            neighbor = self.generate_neighbor(current)
            neighbor_decoded = decode(neighbor.chrom, self.var_types)
            neighbor.fitness = self.evaluate(neighbor_decoded)

            # 计算接受概率并决定是否接受
            prob = self.accept_probability(current.fitness, neighbor.fitness, temp)
            if random.random() < prob:
                current = neighbor  # 接受新解

            # 更新全局最优
            if current.fitness > best.fitness:
                best = current
                no_improve_cnt = 0  # 重置未改进计数器
            else:
                no_improve_cnt += 1

            # 记录历史数据
            self.best_fitness_history.append(best.fitness)
            self.current_temp_history.append(temp)

            # 打印进度（每100次迭代）
            if (iter + 1) % 100 == 0:
                print(f"迭代 {iter + 1}/{self.max_iter} | 温度: {temp:.2f} | 最优适应度: {best.fitness:.6f}")

            # 提前终止条件（连续多次未改进）
            if no_improve_cnt >= self.max_stay:
                print(f"提前终止：连续{self.max_stay}次迭代未改进")
                break

            # 降温
            temp *= self.cooling_rate
            if temp < 1e-8:  # 温度过低时强制终止
                print("温度过低，停止迭代")
                break

        return best

    def plot_process(self):
        """绘制退火过程曲线（适应度+温度）"""
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # 绘制适应度曲线
        ax1.plot(
            range(len(self.best_fitness_history)),
            self.best_fitness_history,
            c='red',
            linewidth=2,
            label='最优适应度'
        )
        ax1.set_xlabel('迭代次数', fontsize=12, color='black')
        ax1.set_ylabel('最优适应度', fontsize=12, color='black')
        ax1.tick_params(axis='y', labelcolor='black')
        ax1.grid(True, alpha=0.3)

        # 绘制温度曲线（双坐标轴）
        ax2 = ax1.twinx()
        ax2.plot(
            range(len(self.current_temp_history)),
            self.current_temp_history,
            c='blue',
            linewidth=2,
            linestyle='--',
            label='当前温度'
        )
        ax2.set_ylabel('温度', fontsize=12, color='black')
        ax2.tick_params(axis='y', labelcolor='black')

        # 标题和图例
        plt.title('模拟退火算法过程曲线', fontsize=14)
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=10)

        plt.tight_layout()
        plt.show()

# ================= 使用示例 =================
if __name__ == "__main__":
    # 设置中文字体


    # 1. 变量定义（与PSO/GA保持一致）
    var_types = [("real", (2, -2, 2))]  # 2个实数变量


    # 2. 目标函数（适应度越大越好，与GA示例一致）
    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]
        # Rosenbrock函数变种（最大化）
        return -((1 - x) ** 2 + 100 * (y - x ** 2) ** 2)


    # 3. 初始化SA
    sa = SA(
        var_types=var_types,
        evaluate=evaluate,
        init_temp=100.0,
        cooling_rate=0.95,
        max_iter=1000,
        max_stay=100,
        mutate_prob=0.1
    )

    # 4. 运行算法
    best_solution = sa.run()

    # 5. 输出结果
    best_decoded = decode(best_solution.chrom, var_types)
    print("\n最优解：")
    print(f"变量值：x={best_decoded['real_0'][0]:.6f}, y={best_decoded['real_0'][1]:.6f}")
    print(f"最优适应度：{best_solution.fitness:.6f}")

    # 6. 绘制过程曲线
    sa.plot_process()