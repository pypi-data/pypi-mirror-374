import numpy as np
import random
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from typing import List, Tuple, Callable
from utils import decode, init_mlp, fix_random_seed, repair_solution, is_decoded_feasible, penalty_fun

# 确保中文显示正常
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False


# ================= 蜜蜂个体类（增强约束属性）=================
class Bee:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（蜜源位置）
        self.fitness = None  # 惩罚后适应度（算法选择依据）
        self.raw_fitness = None  # 原始目标值（真实优化目标）
        self.violation = 0.0  # 约束违反量（评估解的可行性）
        self.trials = 0  # 尝试次数（用于侦察蜂判断）
        self.is_employed = True  # 是否为雇佣蜂（区分蜂群角色）

    def __str__(self) -> str:
        if self.fitness is None:
            return "fitness=None"
        return (f"raw={self.raw_fitness:.6f}, fitness={self.fitness:.6f}, "
                f"violation={self.violation:.6f}, trials={self.trials}")


# ================= 带约束的人工蜂群算法（ABC）类 =================
class ABC:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回原始目标值
            pop_size: int = 30,
            max_gen: int = 100,
            limit_init: int = 100,  # 初始蜜源放弃阈值
            limit_factor: float = 0.5,  # 阈值调整因子
            mutation_prob: float = 0.1,  # 变异概率（增强多样性）
            maximize: bool = True,  # 目标方向（最大化/最小化）
            eq_constraints: List[Callable[[dict], float]] = None,  # 等式约束：g(x)=0
            ineq_constraints: List[Callable[[dict], float]] = None,  # 不等式约束：h(x)≤0
            penalty_coeff: float = 1e3,  # 基础惩罚系数
            visualize_gens: int = 5  # 种群位置记录代数（用于可视化）
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.limit_init = limit_init
        self.limit_factor = limit_factor
        self.mutation_prob = mutation_prob  # 用于增强种群多样性
        self.maximize = maximize

        # 约束与目标扩展
        self.eq_constraints = eq_constraints or []
        self.ineq_constraints = ineq_constraints or []
        self.has_constraints = len(self.eq_constraints) > 0 or len(self.ineq_constraints) > 0
        self.penalty_coeff = penalty_coeff
        self.visualize_gens = visualize_gens

        # 解析变量范围
        self.var_ranges = []  # (类型, 下界, 上界)
        self.dim = 0  # 总变量数
        self.low = []  # 所有变量下界
        self.high = []  # 所有变量上界
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

        # 迭代记录（根据有无约束动态调整）
        self.best_fitness_history = []  # 每代最优惩罚适应度
        self.best_raw_history = []  # 每代最优原始目标值
        self.avg_fitness_history = []  # 每代平均惩罚适应度
        self.avg_violation_history = []  # 每代平均约束违反量（仅带约束时）
        self.position_history = []  # 种群位置记录（用于可视化）
        self.diversity_history = []  # 种群多样性记录

    def _penalized_fitness(self, decoded: dict, gen: int) -> Tuple[float, float, float]:
        """计算惩罚后适应度、原始目标值、约束违反量"""
        # 1. 计算原始目标值
        raw_val = self.evaluate(decoded)

        # 2. 计算约束违反量（无约束时为0）
        violation = 0.0
        if self.has_constraints:
            # 等式约束：允许1e-6误差
            for g in self.eq_constraints:
                violation += max(0.0, abs(g(decoded)) - 1e-6)
            # 不等式约束：h(x) > 0时计算违反量
            for h in self.ineq_constraints:
                violation += max(0.0, h(decoded))

        # 3. 计算惩罚后适应度
        if self.has_constraints:
            # 自适应惩罚系数：随迭代增强
            adaptive_coeff = penalty_fun(gen, self.penalty_coeff, self.max_gen)
            if self.maximize:
                penalized = raw_val - adaptive_coeff * violation
            else:
                penalized = raw_val + adaptive_coeff * violation
        else:
            penalized = raw_val

        return penalized, raw_val, violation

    def init_bee(self, gen: int = 0) -> Bee:
        """初始化蜜蜂个体（带约束属性）"""
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

        bee = Bee(np.array(chrom, dtype=float))
        # 计算初始适应度
        decoded = decode(bee.chrom, self.var_types)
        bee.fitness, bee.raw_fitness, bee.violation = self._penalized_fitness(decoded, gen)
        return bee

    def bound_position(self, chrom: np.ndarray) -> np.ndarray:
        """位置边界处理+类型转换"""
        bounded = chrom.copy()
        for i in range(self.dim):
            vtype, low, high = self.var_ranges[i]
            # 范围约束
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

    def _calculate_diversity(self, population: List[Bee]) -> float:
        """计算种群多样性（平均欧氏距离）"""
        positions = np.array([bee.chrom for bee in population])
        distances = []
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                distances.append(np.linalg.norm(positions[i] - positions[j]))
        return np.mean(distances) if distances else 0.0

    def run(self) -> Bee:
        """运行带约束的人工蜂群算法（完整实现）"""
        # 1. 初始化蜂群（雇佣蜂数量=观察蜂数量=pop_size/2）
        self.population = [self.init_bee(gen=0) for _ in range(self.pop_size)]

        # 2. 初始状态记录
        self._record_fitness(self.population)
        self.diversity_history.append(self._calculate_diversity(self.population))
        interval = max(1, self.max_gen // (self.visualize_gens - 1))  # 位置记录间隔
        self._record_positions(self.population, gen=0)

        # 3. 迭代优化
        for gen in range(1, self.max_gen + 1):
            # 自适应调整放弃阈值（基于种群多样性）
            current_diversity = self.diversity_history[-1]
            if current_diversity < 0.1 * np.mean(self.high - self.low):  # 多样性低时减小阈值
                current_limit = max(10, int(self.limit_init * self.limit_factor))
            else:  # 多样性高时增大阈值
                current_limit = min(200, int(self.limit_init / self.limit_factor))

            # 1. 雇佣蜂阶段：更新蜜源并评估
            for i in range(self.pop_size // 2):  # 前半部分为雇佣蜂
                bee = self.population[i]
                bee.is_employed = True

                # 随机选择一个不同的蜜源和维度
                while True:
                    k = random.randint(0, self.pop_size - 1)
                    j = random.randint(0, self.dim - 1)
                    if k != i:
                        break

                # 生成新蜜源（引入自适应步长）
                phi = random.uniform(-1, 1) * (1 - gen / self.max_gen)  # 步长随迭代减小
                new_chrom = bee.chrom.copy()
                new_chrom[j] = bee.chrom[j] + phi * (bee.chrom[j] - self.population[k].chrom[j])
                new_chrom = self.bound_position(new_chrom)

                # 评估新蜜源
                decoded = decode(new_chrom, self.var_types)
                new_fitness, new_raw, new_violation = self._penalized_fitness(decoded, gen)

                # 贪婪选择：若新蜜源更优则替换
                if (self.maximize and new_fitness > bee.fitness) or (not self.maximize and new_fitness < bee.fitness):
                    bee.chrom = new_chrom
                    bee.fitness = new_fitness
                    bee.raw_fitness = new_raw
                    bee.violation = new_violation
                    bee.trials = 0  # 重置尝试次数
                else:
                    bee.trials += 1  # 尝试次数加1

            # 2. 观察蜂阶段：基于轮盘赌选择蜜源（适应度越大被选中概率越高）
            # 计算选择概率（处理负适应度情况）
            fitness_values = [bee.fitness for bee in self.population]
            min_fitness = min(fitness_values)
            adjusted_fitness = [f - min_fitness + 1e-6 for f in fitness_values]  # 确保非负
            probabilities = [f / sum(adjusted_fitness) for f in adjusted_fitness]

            for i in range(self.pop_size // 2, self.pop_size):  # 后半部分为观察蜂
                self.population[i].is_employed = False

                # 轮盘赌选择一个蜜源
                selected = random.choices(range(self.pop_size), weights=probabilities)[0]
                selected_bee = self.population[selected]

                # 随机选择一个不同的蜜源和维度
                while True:
                    k = random.randint(0, self.pop_size - 1)
                    j = random.randint(0, self.dim - 1)
                    if k != selected:
                        break

                # 生成新蜜源
                phi = random.uniform(-1, 1) * (1 - gen / self.max_gen)
                new_chrom = selected_bee.chrom.copy()
                new_chrom[j] = selected_bee.chrom[j] + phi * (selected_bee.chrom[j] - self.population[k].chrom[j])
                new_chrom = self.bound_position(new_chrom)

                # 评估新蜜源
                decoded = decode(new_chrom, self.var_types)
                new_fitness, new_raw, new_violation = self._penalized_fitness(decoded, gen)

                # 贪婪选择：若新蜜源更优则替换
                if (self.maximize and new_fitness > selected_bee.fitness) or (
                        not self.maximize and new_fitness < selected_bee.fitness):
                    selected_bee.chrom = new_chrom
                    selected_bee.fitness = new_fitness
                    selected_bee.raw_fitness = new_raw
                    selected_bee.violation = new_violation
                    selected_bee.trials = 0  # 重置尝试次数
                else:
                    selected_bee.trials += 1  # 尝试次数加1

            # 3. 侦察蜂阶段：放弃超过阈值的蜜源并随机生成新蜜源
            for i in range(self.pop_size):
                if self.population[i].trials >= current_limit:
                    # 对最优蜜源进行变异而非完全随机（保留优质信息）
                    if i == np.argmax([b.fitness for b in self.population]) and self.maximize:
                        best_chrom = self.population[i].chrom.copy()
                        # 对随机维度进行小幅度变异
                        for j in range(self.dim):
                            if random.random() < self.mutation_prob:
                                best_chrom[j] += random.uniform(-0.1, 0.1) * (self.high[j] - self.low[j])
                        self.population[i].chrom = self.bound_position(best_chrom)
                    else:
                        self.population[i] = self.init_bee(gen=gen)
                    # 重新计算适应度
                    decoded = decode(self.population[i].chrom, self.var_types)
                    fit, raw, viol = self._penalized_fitness(decoded, gen)
                    self.population[i].fitness = fit
                    self.population[i].raw_fitness = raw
                    self.population[i].violation = viol
                    self.population[i].trials = 0  # 重置尝试次数

            # 4. 记录当前代信息
            self._record_fitness(self.population)
            self.diversity_history.append(self._calculate_diversity(self.population))
            # 按间隔记录位置（最后一代强制记录）
            if (gen % interval == 0) or (gen == self.max_gen):
                self._record_positions(self.population, gen=gen)

            # 5. 打印进度
            if gen % 10 == 0:
                progress_str = (f"第{gen}/{self.max_gen}代 | "
                                f"最优适应度: {self.best_fitness_history[-1]:.6f} | "
                                f"平均适应度: {self.avg_fitness_history[-1]:.6f}")
                if self.has_constraints:
                    progress_str += f" | 平均违反量: {self.avg_violation_history[-1]:.6f}"
                progress_str += f" | 多样性: {self.diversity_history[-1]:.6f}"
                print(progress_str)

        # 6. 裁剪位置记录
        if len(self.position_history) > self.visualize_gens:
            self.position_history = self.position_history[:self.visualize_gens]

        # 7. 自动可视化
        self.visualize()

        # 8. 返回全局最优个体
        return max(self.population, key=lambda x: x.fitness) if self.maximize else min(
            self.population, key=lambda x: x.fitness
        )

    def _record_fitness(self, population: List[Bee]):
        """记录每代适应度指标"""
        fitness_values = [b.fitness for b in population]
        raw_values = [b.raw_fitness for b in population]

        self.best_fitness_history.append(max(fitness_values) if self.maximize else min(fitness_values))
        self.best_raw_history.append(max(raw_values) if self.maximize else min(raw_values))
        self.avg_fitness_history.append(np.mean(fitness_values))

        if self.has_constraints:
            violation_values = [b.violation for b in population]
            self.avg_violation_history.append(np.mean(violation_values))

    def _record_positions(self, population: List[Bee], gen: int):
        """记录种群位置（仅实数变量）"""
        positions = []
        for bee in population:
            decoded = decode(bee.chrom, self.var_types)
            real_pos = []
            for key in decoded:
                if key.startswith("real_"):
                    real_pos.extend(decoded[key].tolist())
            positions.append(real_pos)
        self.position_history.append({"gen": gen, "positions": np.array(positions)})

    def visualize(self):
        """可视化适应度曲线、种群多样性和位置演化"""
        # 1. 适应度与约束违反量图表
        if self.has_constraints:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # 子图1：适应度曲线
            ax1.plot(range(len(self.best_fitness_history)), self.best_fitness_history,
                     c='red', linewidth=2, label='最优惩罚适应度')
            ax1.plot(range(len(self.best_raw_history)), self.best_raw_history,
                     c='green', linewidth=2, linestyle='--', label='最优原始目标值')
            ax1.plot(range(len(self.avg_fitness_history)), self.avg_fitness_history,
                     c='blue', linewidth=1.5, linestyle='-.', label='平均惩罚适应度')
            ax1.set_xlabel('迭代次数')
            ax1.set_ylabel('适应度/目标值')
            ax1.set_title('人工蜂群算法适应度变化曲线（带约束）')
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            # 子图2：约束违反量曲线
            ax2.plot(range(len(self.avg_violation_history)), self.avg_violation_history,
                     c='purple', linewidth=2, label='平均约束违反量')
            ax2.axhline(y=0, c='black', linestyle='--', alpha=0.5, label='约束满足线')
            ax2.set_xlabel('迭代次数')
            ax2.set_ylabel('平均约束违反量')
            ax2.set_title('人工蜂群算法约束违反量变化曲线')
            ax2.grid(True, alpha=0.3)
            ax2.legend()

            plt.tight_layout()
            plt.show()
        else:
            # 无约束时仅显示适应度曲线
            plt.figure(figsize=(10, 6))
            plt.plot(range(len(self.best_fitness_history)), self.best_fitness_history,
                     c='red', linewidth=2, label='每代最优适应度')
            plt.plot(range(len(self.avg_fitness_history)), self.avg_fitness_history,
                     c='blue', linewidth=2, linestyle='--', label='每代平均适应度')
            plt.xlabel('迭代次数')
            plt.ylabel('适应度值')
            plt.title('人工蜂群算法适应度变化曲线（无约束）')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.show()

        # 2. 种群多样性曲线
        plt.figure(figsize=(10, 6))
        plt.plot(range(len(self.diversity_history)), self.diversity_history,
                 c='orange', linewidth=2, label='种群平均欧氏距离')
        plt.xlabel('迭代次数')
        plt.ylabel('多样性指标')
        plt.title('人工蜂群算法种群多样性变化曲线')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()

        # 3. 种群位置演化可视化
        if not self.position_history:
            return
        sample_pos = self.position_history[0]["positions"]
        real_dim = sample_pos.shape[1] if sample_pos.size > 0 else 0
        all_positions = np.vstack([data["positions"] for data in self.position_history])

        # 3.1 2维实数变量可视化
        if real_dim == 2:
            fig, ax = plt.subplots(figsize=(10, 6))
            gen_indices = []
            for i, data in enumerate(self.position_history):
                gen_indices.extend([i] * self.pop_size)

            colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))
            scatter = ax.scatter(all_positions[:, 0], all_positions[:, 1],
                                 c=colors, alpha=0.6, s=50, edgecolors='white', linewidth=0.5)

            # 标记全局最优点
            best_idx = np.argmax([b.fitness for b in self.population]) if self.maximize else np.argmin(
                [b.fitness for b in self.population])
            best_decoded = decode(self.population[best_idx].chrom, self.var_types)
            best_pos = best_decoded["real_0"]
            ax.scatter(best_pos[0], best_pos[1], c='red', s=150, marker='*',
                       edgecolors='darkred', linewidth=2, label='全局最优解')

            # 绘制约束边界（带约束时）
            if self.has_constraints and self.ineq_constraints:
                x_min, x_max = all_positions[:, 0].min() - 0.5, all_positions[:, 0].max() + 0.5
                y_min, y_max = all_positions[:, 1].min() - 0.5, all_positions[:, 1].max() + 0.5
                xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200), np.linspace(y_min, y_max, 200))

                for i, h in enumerate(self.ineq_constraints):
                    grid_decoded = {"real_0": (xx, yy)}
                    constraint_vals = h(grid_decoded)
                    contour = ax.contour(xx, yy, constraint_vals, levels=[0], alpha=0)
                    for seg in contour.allsegs[0]:
                        ax.plot(seg[:, 0], seg[:, 1], color=f'C{i}', linewidth=2.5,
                                linestyle='--', alpha=0.8)
                    ax.plot([], [], color=f'C{i}', linewidth=2.5, linestyle='--',
                            label=f'不等式约束 {i + 1}')

            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('迭代进程（颜色越深越接近最优代）')
            ax.set_xlabel('实数变量1')
            ax.set_ylabel('实数变量2')
            ax.set_title('人工蜂群算法种群位置演化（2D实数变量）')
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.show()

        # 3.2 高维实数变量PCA降维可视化
        elif real_dim > 2:
            pca = PCA(n_components=2)
            positions_2d = pca.fit_transform(all_positions)

            fig, ax = plt.subplots(figsize=(10, 6))
            gen_indices = []
            for i, data in enumerate(self.position_history):
                gen_indices.extend([i] * self.pop_size)
            colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))

            scatter = ax.scatter(positions_2d[:, 0], positions_2d[:, 1],
                                 c=colors, alpha=0.6, s=50, edgecolors='white', linewidth=0.5)

            # 标记全局最优解
            best_idx = np.argmax([b.fitness for b in self.population]) if self.maximize else np.argmin(
                [b.fitness for b in self.population])
            best_pos_high_dim = self.position_history[-1]["positions"][best_idx]
            best_pos_2d = pca.transform([best_pos_high_dim])[0]
            ax.scatter(best_pos_2d[0], best_pos_2d[1], c='red', s=150, marker='*',
                       edgecolors='darkred', linewidth=2, label='全局最优解')

            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('迭代进程（颜色越深越接近最优代）')
            ax.set_xlabel(f'主成分1（解释方差：{pca.explained_variance_ratio_[0]:.2%}）')
            ax.set_ylabel(f'主成分2（解释方差：{pca.explained_variance_ratio_[1]:.2%}）')
            ax.set_title(f'人工蜂群算法种群位置演化（PCA降维至2D，原始维度{real_dim}）')
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.show()

    def repair_solution(self, decoded: dict, max_time: float = 1.0, step: float = 0.01) -> dict:
        """修复违反约束的解"""
        if self.has_constraints:
            return repair_solution(self, decoded, max_time, step)
        return decoded

    def is_decoded_feasible(self, decoded: dict, tol: float = 1e-6) -> bool:
        """检查解是否可行"""
        if self.has_constraints:
            return is_decoded_feasible(self, decoded, tol)
        return True


# ================= 测试示例（支持有/无约束两种模式）=================
if __name__ == "__main__":
    # 初始化工具
    fix_random_seed(42)
    init_mlp()

    # 1. 变量定义（2个实数变量，范围[-2.0, 2.0]）
    var_types = [("real", (2, -2.0, 2.0))]


    # 2. 目标函数（Rosenbrock函数，求最小值→转为最大化问题）
    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]
        raw_val = (1 - x) ** 2 + 100 * (y - x ** 2) ** 2  # 原始函数值（越小越好）
        return -raw_val  # 转为最大化问题


    # 3. 约束条件控制
    use_constraints = True  # True=带约束，False=无约束
    eq_constraints = []
    ineq_constraints = []

    if use_constraints:
        # 约束1：x + y ≤ 0
        def ineq1(decoded: dict) -> float:
            x, y = decoded["real_0"]
            return x + y


        # 约束2：x² + y² ≤ 0.5
        def ineq2(decoded: dict) -> float:
            x, y = decoded["real_0"]
            return x ** 2 + y ** 2 - 0.5


        # 约束3：y ≥ x + 0.3 → x - y + 0.3 ≤ 0
        def ineq3(decoded: dict) -> float:
            x, y = decoded["real_0"]
            return x - y + 0.3


        ineq_constraints = [ineq1, ineq2, ineq3]

    # 4. 初始化ABC算法
    abc_optimizer = ABC(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=30,
        max_gen=150,
        limit_init=100,
        limit_factor=0.5,
        mutation_prob=0.1,
        maximize=True,
        eq_constraints=eq_constraints,
        ineq_constraints=ineq_constraints,
        penalty_coeff=1e3,
        visualize_gens=6
    )

    # 5. 运行算法
    print(f"=== 人工蜂群算法（ABC）开始运行 {'(带约束)' if use_constraints else '(无约束)'} ===")
    best_bee = abc_optimizer.run()
    print(f"=== 人工蜂群算法（ABC）运行结束 {'(带约束)' if use_constraints else '(无约束)'} ===")

    # 6. 解析并输出结果
    best_decoded = decode(best_bee.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]
    min_raw_val = -best_bee.raw_fitness  # 还原为原始函数值

    print("\n========== 最优结果详情 ==========")
    print(f"1. 最优变量值：")
    print(f"   x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"2. 目标函数结果：")
    print(f"   原始Rosenbrock函数值（最小值）：{min_raw_val:.6f}")
    print(f"   算法适应度值：{best_bee.fitness:.6f}")

    # 带约束时输出约束信息
    if use_constraints:
        print(f"3. 约束满足情况：")
        print(f"   总约束违反量：{best_bee.violation:.6f}")
        is_feasible = best_bee.violation <= 1e-6
        print(f"   是否为可行解：{'是' if is_feasible else '否'}")

        if not is_feasible:
            print("\n========== 修复不可行解 ==========")
            repaired_decoded = abc_optimizer.repair_solution(best_decoded, max_time=1.5, step=0.005)
            x_repaired, y_repaired = repaired_decoded["real_0"]
            repaired_raw = (1 - x_repaired) ** 2 + 100 * (y_repaired - x_repaired ** 2) ** 2
            repaired_violation = 0.0
            for constraint in ineq_constraints:
                repaired_violation += max(0.0, constraint(repaired_decoded))

            print(f"修复后变量值：x = {x_repaired:.6f}, y = {y_repaired:.6f}")
            print(f"修复后Rosenbrock函数值：{repaired_raw:.6f}")
            print(f"修复后约束违反量：{repaired_violation:.6f}")
            print(f"修复后是否为可行解：{'是' if repaired_violation <= 1e-6 else '否'}")

        # 约束检查详情
        print("\n========== 约束检查详情 ==========")
        for i, constraint in enumerate(ineq_constraints, 1):
            val = constraint(best_decoded)
            status = "满足" if val <= 1e-6 else "违反"
            print(f"不等式约束 {i}：计算值 = {val:.6f} → {status}（要求 ≤ 0）")

    # 无约束场景说明
    else:
        print(f"\n========== 无约束场景说明 ==========")
        print(f"理论最优解：x=1.0, y=1.0（函数值0）")
        print(f"当前解与理论值偏差：")
        print(f"   Δx = {abs(x_opt - 1.0):.6f}, Δy = {abs(y_opt - 1.0):.6f}")
        print(f"   函数值偏差：{abs(min_raw_val - 0.0):.6f}")
