import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from sklearn.decomposition import PCA
from utils import decode, init_mlp, fix_random_seed, repair_solution, is_decoded_feasible, penalty_fun

plt.rcParams["font.family"] = ["SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


# ================= 差分进化个体类（增强约束属性）=================
class DESolution:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（解向量）
        self.fitness = None  # 惩罚后适应度（用于算法选择）
        self.raw_fitness = None  # 原始目标值（真实优化目标）
        self.violation = 0.0  # 约束违反量（评估解的可行性）

    def __str__(self) -> str:
        if self.fitness is None:
            return "fitness=None"
        return (f"raw={self.raw_fitness:.6f}, fitness={self.fitness:.6f}, "
                f"violation={self.violation:.6f}")


# ================= 带可选约束的差分进化算法（DE）类 =================
class DE:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回原始目标值
            pop_size: int = 50,
            max_gen: int = 100,
            f: float = 0.5,  # 缩放因子（差分权重，通常0.4-1.0）
            cr: float = 0.9,  # 交叉概率（通常0.1-1.0）
            strategy: str = "rand/1/bin",  # 变异策略（默认经典rand/1/bin）
            maximize: bool = True,  # 目标方向（最大化/最小化）
            eq_constraints: List[Callable[[dict], float]] = None,  # 等式约束：g(x)=0
            ineq_constraints: List[Callable[[dict], float]] = None,  # 不等式约束：h(x)≤0
            penalty_coeff: float = 1e3,  # 基础惩罚系数
            visualize_gens: int = 5  # 记录种群位置的代数间隔（用于可视化）
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.f = f  # 缩放因子（控制差分变异的幅度）
        self.cr = cr  # 交叉概率（控制试验向量的多样性）
        self.strategy = strategy  # 变异策略（后续可扩展rand/2、best/1等）

        # 约束与目标相关扩展（核心：通过has_constraints标记动态适配）
        self.maximize = maximize
        self.eq_constraints = eq_constraints or []
        self.ineq_constraints = ineq_constraints or []
        self.has_constraints = len(self.eq_constraints) > 0 or len(self.ineq_constraints) > 0
        self.penalty_coeff = penalty_coeff
        self.visualize_gens = visualize_gens

        # 解析变量范围（位置约束+类型转换）
        self.var_ranges = []  # 存储每个变量的（类型, 下界, 上界）
        self.dim = 0  # 总变量数
        self.low = []  # 所有变量的下界（数组形式，用于快速计算）
        self.high = []  # 所有变量的上界（数组形式）
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

        # 迭代记录（根据有无约束动态存储指标）
        self.best_fitness_history = []  # 每代最优惩罚适应度
        self.best_raw_history = []  # 每代最优原始目标值
        self.avg_fitness_history = []  # 每代平均惩罚适应度
        self.avg_violation_history = []  # 每代平均约束违反量（仅在有约束时记录）
        self.position_history = []  # 种群位置记录（用于演化可视化）

    def _penalized_fitness(self, decoded: dict, gen: int) -> Tuple[float, float, float]:
        """计算惩罚后适应度、原始目标值、约束违反量（无约束时违反量为0）"""
        # 1. 计算原始目标值（不依赖约束）
        raw_val = self.evaluate(decoded)

        # 2. 计算约束违反量（无约束时直接返回0，避免多余计算）
        violation = 0.0
        if self.has_constraints:
            # 等式约束：允许1e-6误差（工程上的数值容忍）
            for g in self.eq_constraints:
                violation += max(0.0, abs(g(decoded)) - 1e-6)
            # 不等式约束：仅当h(x) > 0时计算违反量（h(x) ≤ 0为满足）
            for h in self.ineq_constraints:
                violation += max(0.0, h(decoded))

        # 3. 计算惩罚后适应度（无约束时不启用惩罚，直接用原始值）
        if self.has_constraints:
            # 自适应惩罚系数：随迭代增强，后期更严格惩罚违反约束的解
            adaptive_coeff = penalty_fun(gen, self.penalty_coeff, self.max_gen)
            # 按目标方向调整惩罚逻辑（最大化→减惩罚，最小化→加惩罚）
            if self.maximize:
                penalized = raw_val - adaptive_coeff * violation
            else:
                penalized = raw_val + adaptive_coeff * violation
        else:
            penalized = raw_val

        return penalized, raw_val, violation

    def init_solution(self, gen: int = 0) -> DESolution:
        """初始化个体（含约束属性，确保初始解的合法性）"""
        chrom = []
        for vtype, info in self.var_types:
            if vtype == "binary":
                # 二进制变量：0/1随机生成
                chrom.extend(np.random.randint(0, 2, size=info))
            elif vtype == "integer":
                # 整数变量：在[low, high]范围内随机整数
                n, low, high = info
                chrom.extend(np.random.randint(low, high + 1, size=n))
            elif vtype == "real":
                # 实数变量：在[low, high]范围内均匀分布随机数
                n, low, high = info
                chrom.extend(np.random.uniform(low, high, size=n))

        # 生成个体并计算适应度与约束属性
        sol = DESolution(np.array(chrom, dtype=float))
        decoded = decode(sol.chrom, self.var_types)
        sol.fitness, sol.raw_fitness, sol.violation = self._penalized_fitness(decoded, gen)
        return sol

    def bound_handler(self, chrom: np.ndarray) -> np.ndarray:
        """边界处理+类型转换（确保变量符合定义范围，避免无效解）"""
        bounded = chrom.copy()
        for i in range(self.dim):
            vtype, low, high = self.var_ranges[i]
            # 1. 范围约束：将越界值拉回[low, high]
            if bounded[i] < low:
                bounded[i] = low
            elif bounded[i] > high:
                bounded[i] = high
            # 2. 类型转换：确保变量类型正确（整数/二进制）
            if vtype == "integer":
                bounded[i] = round(bounded[i])
            elif vtype == "binary":
                bounded[i] = 1 if bounded[i] >= 0.5 else 0
        return bounded

    def mutate(self, target_idx: int, population: List[DESolution]) -> np.ndarray:
        """变异操作（生成变异向量，支持经典rand/1策略，可扩展）"""
        # 核心：选择3个与目标个体不同的随机个体
        while True:
            r1, r2, r3 = random.sample(range(self.pop_size), 3)
            if r1 != target_idx and r2 != target_idx and r3 != target_idx:
                break

        x1 = population[r1].chrom
        x2 = population[r2].chrom
        x3 = population[r3].chrom

        # 经典rand/1变异策略（差分进化核心公式）
        if self.strategy == "rand/1/bin":
            return x1 + self.f * (x2 - x3)
        # 可扩展其他策略（如best/1、rand/2等），此处保持经典实现
        else:
            raise ValueError(f"不支持的变异策略：{self.strategy}，当前仅支持rand/1/bin")

    def crossover(self, target_chrom: np.ndarray, mutant_chrom: np.ndarray) -> np.ndarray:
        """交叉操作（生成试验向量，二进制交叉bin）"""
        trial_chrom = target_chrom.copy()
        # 随机选择一个维度强制交叉（确保试验向量至少有一个维度来自变异向量）
        j_rand = random.randint(0, self.dim - 1)

        # 逐维度判断是否交叉（交叉概率cr控制）
        for j in range(self.dim):
            if random.random() < self.cr or j == j_rand:
                trial_chrom[j] = mutant_chrom[j]
        return trial_chrom

    def select(self, target: DESolution, trial: DESolution) -> DESolution:
        """选择操作（贪婪选择，基于惩罚后适应度）"""
        # 最大化目标：试验向量适应度高则保留；最小化则相反
        if (self.maximize and trial.fitness > target.fitness) or \
                (not self.maximize and trial.fitness < target.fitness):
            return trial
        return target

    def _record_fitness(self, population: List[DESolution]):
        """记录每代核心指标（根据有无约束动态调整）"""
        fitness_values = [sol.fitness for sol in population]
        raw_values = [sol.raw_fitness for sol in population]

        # 记录最优和平均适应度（适配目标方向）
        self.best_fitness_history.append(max(fitness_values) if self.maximize else min(fitness_values))
        self.best_raw_history.append(max(raw_values) if self.maximize else min(raw_values))
        self.avg_fitness_history.append(np.mean(fitness_values))

        # 仅在有约束时记录平均违反量（无约束时无需记录）
        if self.has_constraints:
            violation_values = [sol.violation for sol in population]
            self.avg_violation_history.append(np.mean(violation_values))

    def _record_positions(self, population: List[DESolution], gen: int):
        """记录种群位置（仅提取实数变量，二进制/整数可视化意义有限）"""
        positions = []
        for sol in population:
            decoded = decode(sol.chrom, self.var_types)
            real_pos = []
            # 仅保留实数变量（key以"real_"开头）
            for key in decoded:
                if key.startswith("real_"):
                    real_pos.extend(decoded[key].tolist())
            positions.append(real_pos)
        self.position_history.append({"gen": gen, "positions": np.array(positions)})

    def run(self) -> DESolution:
        """运行带可选约束的差分进化算法"""
        # 1. 初始化种群（类实例属性，后续统一通过self访问）
        self.population = [self.init_solution(gen=0) for _ in range(self.pop_size)]

        # 2. 初始状态记录（适应度+位置）
        self._record_fitness(self.population)
        # 计算位置记录间隔（避免冗余数据，确保至少记录1代）
        interval = max(1, self.max_gen // (self.visualize_gens - 1))
        self._record_positions(self.population, gen=0)

        # 3. 迭代优化（核心循环：变异→交叉→选择）
        for gen in range(1, self.max_gen + 1):
            new_population = []  # 存储新一代种群
            for target_idx in range(self.pop_size):
                # 3.1 目标向量（当前待更新的个体）
                target_sol = self.population[target_idx]

                # 3.2 变异：生成变异向量
                mutant_chrom = self.mutate(target_idx, self.population)

                # 3.3 交叉：生成试验向量（并处理边界）
                trial_chrom = self.crossover(target_sol.chrom, mutant_chrom)
                trial_chrom = self.bound_handler(trial_chrom)  # 确保试验向量合法

                # 3.4 评估试验向量（计算适应度与约束属性）
                trial_sol = DESolution(trial_chrom)
                decoded = decode(trial_sol.chrom, self.var_types)
                trial_sol.fitness, trial_sol.raw_fitness, trial_sol.violation = self._penalized_fitness(
                    decoded, gen
                )

                # 3.5 选择：保留更优的个体（目标向量/试验向量）
                new_population.append(self.select(target_sol, trial_sol))

            # 3.6 更新种群（新一代替换旧一代）
            self.population = new_population

            # 3.7 记录当前代信息（适应度+位置）
            self._record_fitness(self.population)
            # 按间隔记录位置（最后一代强制记录，确保演化过程完整）
            if (gen % interval == 0) or (gen == self.max_gen):
                self._record_positions(self.population, gen=gen)

            # 3.8 打印迭代进度（根据有无约束动态调整输出内容）
            if gen % 10 == 0:
                progress_str = (f"第{gen}/{self.max_gen}代 | "
                                f"最优适应度: {self.best_fitness_history[-1]:.6f} | "
                                f"平均适应度: {self.avg_fitness_history[-1]:.6f}")
                # 仅当有约束时，才显示平均约束违反量
                if self.has_constraints:
                    progress_str += f" | 平均违反量: {self.avg_violation_history[-1]:.6f}"
                print(progress_str)

        # 4. 裁剪位置记录（避免超出设定的可视化代数，减少内存占用）
        if len(self.position_history) > self.visualize_gens:
            self.position_history = self.position_history[:self.visualize_gens]

        # 5. 算法结束后自动绘制可视化图表（动态适配有无约束）
        self.visualize()

        # 6. 返回全局最优个体（根据目标方向选择）
        return max(self.population, key=lambda x: x.fitness) if self.maximize else min(
            self.population, key=lambda x: x.fitness
        )

    def visualize(self):
        """核心可视化：根据有无约束动态生成图表（适应度+位置演化）"""
        # 1. 适应度与约束违反量图表（有约束→双子图，无约束→单图）
        if self.has_constraints:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # 子图1：适应度变化曲线（区分惩罚适应度与原始目标值）
            ax1.plot(range(len(self.best_fitness_history)), self.best_fitness_history,
                     c='red', linewidth=2, label='最优惩罚适应度')
            ax1.plot(range(len(self.best_raw_history)), self.best_raw_history,
                     c='green', linewidth=2, linestyle='--', label='最优原始目标值')
            ax1.plot(range(len(self.avg_fitness_history)), self.avg_fitness_history,
                     c='blue', linewidth=1.5, linestyle='-.', label='平均惩罚适应度')
            ax1.set_xlabel('迭代次数')
            ax1.set_ylabel('适应度/目标值')
            ax1.set_title('DE适应度变化曲线（带约束）')
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            # 子图2：约束违反量曲线（仅带约束时显示）
            ax2.plot(range(len(self.avg_violation_history)), self.avg_violation_history,
                     c='purple', linewidth=2, label='平均约束违反量')
            ax2.axhline(y=0, c='black', linestyle='--', alpha=0.5, label='约束满足线（违反量=0）')
            ax2.set_xlabel('迭代次数')
            ax2.set_ylabel('平均约束违反量')
            ax2.set_title('DE约束违反量变化曲线')
            ax2.grid(True, alpha=0.3)
            ax2.legend()

            plt.tight_layout()
            plt.show()
        else:
            # 无约束时仅显示适应度曲线（简化图表）
            plt.figure(figsize=(10, 6))
            plt.plot(range(len(self.best_fitness_history)), self.best_fitness_history,
                     c='red', linewidth=2, label='每代最优适应度')
            plt.plot(range(len(self.avg_fitness_history)), self.avg_fitness_history,
                     c='blue', linewidth=2, linestyle='--', label='每代平均适应度')
            plt.xlabel('迭代次数')
            plt.ylabel('适应度值')
            plt.title('DE适应度变化曲线（无约束）')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.show()

        # 2. 种群位置演化可视化（仅针对实数变量，二进制/整数可视化意义有限）
        if not self.position_history:
            return  # 无位置记录时跳过
        sample_pos = self.position_history[0]["positions"]
        real_dim = sample_pos.shape[1] if sample_pos.size > 0 else 0  # 实数变量维度
        all_positions = np.vstack([data["positions"] for data in self.position_history])  # 所有代位置合并

        # 2.1 2维实数变量：直接绘制位置演化（直观展示搜索轨迹）
        if real_dim == 2:
            fig, ax = plt.subplots(figsize=(10, 6))
            gen_indices = []  # 标记每个位置所属的迭代代次
            for i, data in enumerate(self.position_history):
                gen_indices.extend([i] * self.pop_size)

            # 颜色映射：代次越晚，颜色越深（体现演化过程）
            colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))
            scatter = ax.scatter(all_positions[:, 0], all_positions[:, 1],
                                 c=colors, alpha=0.6, s=50, edgecolors='white', linewidth=0.5)

            # 标记全局最优点（红色星号突出显示）
            best_idx = np.argmax([sol.fitness for sol in self.population]) if self.maximize else np.argmin(
                [sol.fitness for sol in self.population])
            best_decoded = decode(self.population[best_idx].chrom, self.var_types)
            best_pos = best_decoded["real_0"]  # 2维实数变量的最优位置
            ax.scatter(best_pos[0], best_pos[1], c='red', s=150, marker='*',
                       edgecolors='darkred', linewidth=2, label='全局最优解')

            # 仅带约束时绘制不等式约束边界（直观展示可行域）
            if self.has_constraints and self.ineq_constraints:
                # 计算坐标轴范围（基于所有位置的极值，预留一定余量）
                x_min, x_max = all_positions[:, 0].min() - 0.5, all_positions[:, 0].max() + 0.5
                y_min, y_max = all_positions[:, 1].min() - 0.5, all_positions[:, 1].max() + 0.5
                xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200), np.linspace(y_min, y_max, 200))  # 网格点

                # 逐约束绘制边界（h(x)=0为约束边界，h(x)≤0为可行域）
                for i, h in enumerate(self.ineq_constraints):
                    grid_decoded = {"real_0": (xx, yy)}  # 网格点解码为DE可识别格式
                    constraint_vals = h(grid_decoded)  # 计算每个网格点的约束值

                    # 提取约束边界（h(x)=0的线段），避免Matplotlib弃用警告
                    contour = ax.contour(xx, yy, constraint_vals, levels=[0], alpha=0)  # 透明轮廓获取边界
                    for seg in contour.allsegs[0]:  # 遍历所有边界线段
                        ax.plot(seg[:, 0], seg[:, 1], color=f'C{i}', linewidth=2.5,
                                linestyle='--', alpha=0.8)
                    # 手动添加约束图例（解决contour无label问题）
                    ax.plot([], [], color=f'C{i}', linewidth=2.5, linestyle='--',
                            label=f'不等式约束 {i + 1}')

            # 图表补充设置（颜色条、网格、图例）
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('迭代进程（颜色越深越接近最优代）', fontsize=10)
            ax.set_xlabel('实数变量1', fontsize=12)
            ax.set_ylabel('实数变量2', fontsize=12)
            ax.set_title('DE种群位置演化（2D实数变量）', fontsize=14)
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            ax.legend(fontsize=10, loc='upper right')
            plt.tight_layout()
            plt.show()

        # 2.2 高维实数变量（>2维）：PCA降维可视化（保留主要特征）
        elif real_dim > 2:
            # PCA降维：将高维位置投影到2维平面（保留最大方差的两个主成分）
            pca = PCA(n_components=2)
            positions_2d = pca.fit_transform(all_positions)  # 降维后的2D位置

            fig, ax = plt.subplots(figsize=(10, 6))
            gen_indices = []
            for i, data in enumerate(self.position_history):
                gen_indices.extend([i] * self.pop_size)
            colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))  # 代次颜色映射

            # 绘制降维后的种群位置
            scatter = ax.scatter(positions_2d[:, 0], positions_2d[:, 1],
                                 c=colors, alpha=0.6, s=50, edgecolors='white', linewidth=0.5)

            # 标记全局最优解（降维后位置）
            best_idx = np.argmax([sol.fitness for sol in self.population]) if self.maximize else np.argmin(
                [sol.fitness for sol in self.population])
            best_pos_high_dim = self.position_history[-1]["positions"][best_idx]  # 最后一代最优个体的高维位置
            best_pos_2d = pca.transform([best_pos_high_dim])[0]  # 最优位置降维到2D
            ax.scatter(best_pos_2d[0], best_pos_2d[1], c='red', s=150, marker='*',
                       edgecolors='darkred', linewidth=2, label='全局最优解')

            # 图表补充设置（显示方差解释率，说明降维有效性）
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('迭代进程（颜色越深越接近最优代）', fontsize=10)
            ax.set_xlabel(f'主成分1（解释方差：{pca.explained_variance_ratio_[0]:.2%}）', fontsize=12)
            ax.set_ylabel(f'主成分2（解释方差：{pca.explained_variance_ratio_[1]:.2%}）', fontsize=12)
            ax.set_title(f'DE种群位置演化（PCA降维至2D，原始维度{real_dim}）', fontsize=14)
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            ax.legend(fontsize=10, loc='upper right')
            plt.tight_layout()
            plt.show()

    def repair_solution(self, decoded: dict, max_time: float = 1.0, step: float = 0.01) -> dict:
        """修复违反约束的解（仅带约束时生效，无约束时直接返回原解）"""
        if self.has_constraints:
            return repair_solution(self, decoded, max_time, step)
        return decoded  # 无约束时所有解均可行，无需修复

    def is_decoded_feasible(self, decoded: dict, tol: float = 1e-6) -> bool:
        """检查解是否可行（仅带约束时生效，无约束时默认可行）"""
        if self.has_constraints:
            return is_decoded_feasible(self, decoded, tol)
        return True  # 无约束场景下，所有解均满足“可行”定义

# ================= 测试示例（支持有/无约束两种模式）=================
# ================= 测试示例（支持有/无约束两种模式）=================
if __name__ == "__main__":
    # 1. 初始化工具（固定随机种子+中文显示，确保结果可复现）
    fix_random_seed(42)  # 固定种子：让每次运行结果一致，便于调试
    init_mlp()  # 初始化中文显示（复用utils中的封装函数）

    # 2. 变量定义（2个实数变量，适配Rosenbrock函数常用定义域）
    # 格式：[("变量类型", (变量数量, 下界, 上界))]，此处为2个实数变量x,y ∈ [-2, 2]
    var_types = [("real", (2, -2.0, 2.0))]


    # 3. 目标函数（Rosenbrock函数，求最小值→转为最大化问题）
    # 原始Rosenbrock函数：f(x,y)=(1-x)² + 100(y-x²)²，理论最小值0（在x=1,y=1处）
    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]  # 从解码结果中提取2个实数变量
        raw_target_val = (1 - x) ** 2 + 100 * (y - x ** 2) ** 2  # 原始目标值（越小越好）
        return -raw_target_val  # 转为最大化问题：适应度 = -原始值（适应度越大，原始值越小）


    # 4. 约束条件控制（通过use_constraints切换「有约束」和「无约束」模式）
    use_constraints = True  # True=测试带约束场景；False=测试无约束场景
    eq_constraints = []  # 等式约束列表（本次测试暂不使用，设为空）
    ineq_constraints = []  # 不等式约束列表（带约束时添加具体约束）

    # 若开启约束模式，定义3个不等式约束（与之前萤火虫算法测试约束一致，便于对比）
    if use_constraints:
        # 约束1：x + y ≤ 0 → 违反量 = x+y（当x+y>0时违反约束）
        def ineq1(decoded: dict) -> float:
            x, y = decoded["real_0"]
            return x + y  # 约束满足条件：返回值 ≤ 0


        # 约束2：x² + y² ≤ 0.5 → 违反量 = x²+y²-0.5（当结果>0时违反约束）
        def ineq2(decoded: dict) -> float:
            x, y = decoded["real_0"]
            return x ** 2 + y ** 2 - 0.5  # 约束满足条件：返回值 ≤ 0


        # 约束3：y ≥ x + 0.3 → 变形为 x - y + 0.3 ≤ 0（违反量 = x-y+0.3，>0时违反）
        def ineq3(decoded: dict) -> float:
            x, y = decoded["real_0"]
            return x - y + 0.3  # 约束满足条件：返回值 ≤ 0


        # 将约束函数加入列表（算法会自动遍历计算违反量）
        ineq_constraints = [ineq1, ineq2, ineq3]

    # 5. 初始化差分进化（DE）算法实例
    de_optimizer = DE(
        var_types=var_types,  # 变量类型与范围定义
        evaluate=evaluate,  # 目标函数（输入解码后的字典，输出适应度）
        pop_size=50,  # 种群规模（DE建议50-100，平衡效率与搜索能力）
        max_gen=150,  # 最大迭代次数（150代足够收敛到可行域最优）
        f=0.6,  # 缩放因子（0.5-0.8较优，控制变异幅度）
        cr=0.9,  # 交叉概率（0.8-0.9较优，控制试验向量多样性）
        strategy="rand/1/bin",  # 经典变异策略（rand/1/bin，稳定性好）
        maximize=True,  # 目标方向：最大化适应度（因目标函数已取负）
        eq_constraints=eq_constraints,  # 等式约束（空列表，本次不使用）
        ineq_constraints=ineq_constraints,  # 不等式约束（根据use_constraints动态赋值）
        penalty_coeff=1e3,  # 基础惩罚系数（平衡目标优化与约束满足的权重）
        visualize_gens=6  # 位置演化可视化的记录代数（6代，避免冗余）
    )

    # 6. 运行DE算法（打印运行状态，区分有/无约束场景）
    print(f"=== 差分进化算法（DE）开始运行 {'(带约束)' if use_constraints else '(无约束)'} ===")
    best_solution = de_optimizer.run()  # 执行优化，返回全局最优个体
    print(f"=== 差分进化算法（DE）运行结束 {'(带约束)' if use_constraints else '(无约束)'} ===")

    # 7. 解析最优结果（从染色体解码为实际变量值）
    best_decoded = decode(best_solution.chrom, var_types)  # 复用utils的解码函数
    x_opt, y_opt = best_decoded["real_0"]  # 提取2个实数变量的最优值
    min_raw_target = -best_solution.raw_fitness  # 还原为原始Rosenbrock函数的最小值（因适应度取负）

    # 8. 输出最优结果详情（根据有无约束动态调整输出内容）
    print("\n========== 最优结果详情 ==========")
    print(f"1. 最优变量值：")
    print(f"   x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"2. 目标函数结果：")
    print(f"   原始Rosenbrock函数值（最小值）：{min_raw_target:.6f}")  # 理论最小值0（无约束时接近0）
    print(f"   算法适应度值：{best_solution.fitness:.6f}")  # 适应度（越大越好）

    # 仅在有约束时，输出约束满足情况和修复逻辑
    if use_constraints:
        print(f"3. 约束满足情况：")
        print(f"   约束违反量：{best_solution.violation:.6f}")  # 总违反量（0表示完全满足）
        is_feasible = best_solution.violation <= 1e-6  # 数值容忍：1e-6以内视为可行
        print(f"   是否为可行解：{'是' if is_feasible else '否'}")

        # 若最优解不可行，调用修复函数优化，并输出修复结果
        if not is_feasible:
            print("\n========== 修复不可行解 ==========")
            # 修复参数：最大修复时间1.5秒，步长0.005（精细调整）
            repaired_decoded = de_optimizer.repair_solution(best_decoded, max_time=1.5, step=0.005)
            x_repaired, y_repaired = repaired_decoded["real_0"]  # 修复后的变量值

            # 计算修复后的目标值与约束违反量
            repaired_raw = (1 - x_repaired) ** 2 + 100 * (y_repaired - x_repaired ** 2) ** 2
            repaired_violation = 0.0
            for constraint in ineq_constraints:
                repaired_violation += max(0.0, constraint(repaired_decoded))

            # 输出修复详情
            print(f"修复后变量值：x = {x_repaired:.6f}, y = {y_repaired:.6f}")
            print(f"修复后Rosenbrock函数值：{repaired_raw:.6f}")
            print(f"修复后约束违反量：{repaired_violation:.6f}")
            print(f"修复后是否为可行解：{'是' if repaired_violation <= 1e-6 else '否'}")

    # 9. 额外：无约束场景的补充说明（帮助用户理解结果差异）
    else:
        print(f"\n========== 无约束场景说明 ==========")
        print(f"Rosenbrock函数理论最优解：x=1.0, y=1.0（函数值0）")
        print(f"当前最优解与理论值的偏差：")
        print(f"   Δx = {abs(x_opt - 1.0):.6f}, Δy = {abs(y_opt - 1.0):.6f}")
        print(f"   函数值偏差：{abs(min_raw_target - 0.0):.6f}")