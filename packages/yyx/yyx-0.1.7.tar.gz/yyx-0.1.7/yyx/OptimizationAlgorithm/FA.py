import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from sklearn.decomposition import PCA
from utils import decode, init_mlp, fix_random_seed, repair_solution, is_decoded_feasible, penalty_fun

plt.rcParams["font.family"] = ["SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


# ================= 萤火虫个体类（增强约束属性）=================
class Firefly:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（位置向量）
        self.fitness = None  # 惩罚后适应度（用于算法选择）
        self.raw_fitness = None  # 原始目标值（真实优化目标）
        self.violation = 0.0  # 约束违反量（评估解的可行性）
        self.brightness = None  # 亮度（与惩罚后适应度正相关）

    def __str__(self) -> str:
        if self.fitness is None:
            return "fitness=None"
        return (f"raw={self.raw_fitness:.6f}, fitness={self.fitness:.6f}, "
                f"violation={self.violation:.6f}, brightness={self.brightness:.6f}")


# ================= 带可选约束的萤火虫优化算法（FA）类 =================
class FA:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回原始目标值
            pop_size: int = 30,
            max_gen: int = 100,
            alpha: float = 0.2,  # 随机扰动系数
            beta0: float = 1.0,  # 最大吸引力
            gamma: float = 1.0,  # 光吸收系数
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
        self.alpha = alpha  # 随机扰动系数（控制探索能力）
        self.beta0 = beta0  # 最大吸引力（距离为0时的吸引力）
        self.gamma = gamma  # 光吸收系数（控制吸引力随距离的衰减）

        # 约束与目标相关扩展
        self.maximize = maximize
        self.eq_constraints = eq_constraints or []
        self.ineq_constraints = ineq_constraints or []
        self.has_constraints = len(self.eq_constraints) > 0 or len(self.ineq_constraints) > 0
        self.penalty_coeff = penalty_coeff
        self.visualize_gens = visualize_gens

        # 解析变量范围（位置约束+类型转换）
        self.var_ranges = []  # (类型, 下界, 上界)
        self.dim = 0  # 总变量数
        self.low = []  # 所有变量的下界（数组形式）
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

        # 迭代记录（核心指标+位置数据）
        self.best_fitness_history = []  # 每代最优惩罚适应度
        self.best_raw_history = []  # 每代最优原始目标值
        self.avg_fitness_history = []  # 每代平均惩罚适应度
        self.avg_violation_history = []  # 每代平均约束违反量（有约束时记录）
        self.position_history = []  # 种群位置记录（用于演化可视化）

    def _penalized_fitness(self, decoded: dict, gen: int) -> Tuple[float, float, float]:
        """计算惩罚后适应度、原始目标值、约束违反量（无约束时违反量为0）"""
        # 1. 计算原始目标值
        raw_val = self.evaluate(decoded)
        # 2. 计算约束违反量（无约束时直接为0）
        violation = 0.0
        if self.has_constraints:
            # 等式约束：允许1e-6误差
            for g in self.eq_constraints:
                violation += max(0.0, abs(g(decoded)) - 1e-6)
            # 不等式约束：h(x) ≤ 0 为满足
            for h in self.ineq_constraints:
                violation += max(0.0, h(decoded))

        # 3. 自适应惩罚系数（无约束时不启用惩罚）
        if self.has_constraints:
            adaptive_coeff = penalty_fun(gen, self.penalty_coeff, self.max_gen)
            # 按目标方向计算惩罚适应度
            if self.maximize:
                penalized = raw_val - adaptive_coeff * violation
            else:
                penalized = raw_val + adaptive_coeff * violation
        else:
            penalized = raw_val  # 无约束时直接使用原始目标值

        return penalized, raw_val, violation

    def init_firefly(self, gen: int = 0) -> Firefly:
        """初始化萤火虫个体（含约束属性+亮度计算）"""
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
        firefly = Firefly(np.array(chrom, dtype=float))
        # 计算适应度与约束属性
        decoded = decode(firefly.chrom, self.var_types)
        firefly.fitness, firefly.raw_fitness, firefly.violation = self._penalized_fitness(decoded, gen)
        # 初始化亮度（与惩罚后适应度正相关）
        firefly.brightness = firefly.fitness
        return firefly

    def bound_position(self, chrom: np.ndarray) -> np.ndarray:
        """位置越界处理+类型转换（确保变量合法）"""
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

    def attractiveness(self, r: float) -> float:
        """计算吸引力（随距离r衰减）"""
        return self.beta0 * np.exp(-self.gamma * r ** 2)

    def _record_fitness(self, population: List[Firefly]):
        """记录每代核心指标（根据有无约束动态调整）"""
        fitness_values = [f.fitness for f in population]
        raw_values = [f.raw_fitness for f in population]

        # 记录最优和平均适应度
        self.best_fitness_history.append(max(fitness_values) if self.maximize else min(fitness_values))
        self.best_raw_history.append(max(raw_values) if self.maximize else min(raw_values))
        self.avg_fitness_history.append(np.mean(fitness_values))

        # 仅在有约束时记录违反量
        if self.has_constraints:
            violation_values = [f.violation for f in population]
            self.avg_violation_history.append(np.mean(violation_values))

    def _record_positions(self, population: List[Firefly], gen: int):
        """记录种群位置（仅提取实数变量用于可视化）"""
        positions = []
        for firefly in population:
            decoded = decode(firefly.chrom, self.var_types)
            real_pos = []
            # 仅保留实数变量（二进制/整数可视化意义不大）
            for key in decoded:
                if key.startswith("real_"):
                    real_pos.extend(decoded[key].tolist())
            positions.append(real_pos)
        self.position_history.append({"gen": gen, "positions": np.array(positions)})

    def run(self) -> Firefly:
        """运行带可选约束的萤火虫优化算法"""
        # 初始化种群（类实例属性，后续统一通过self访问）
        self.population = [self.init_firefly(gen=0) for _ in range(self.pop_size)]

        # 初始状态记录（使用self.population）
        self._record_fitness(self.population)
        # 计算位置记录间隔（避免冗余数据，确保至少记录1代）
        interval = max(1, self.max_gen // (self.visualize_gens - 1))
        self._record_positions(self.population, gen=0)

        # 迭代优化（从第1代到第max_gen代）
        for gen in range(1, self.max_gen + 1):
            # 对每只萤火虫，向更亮的萤火虫移动（双重循环：i为当前萤火虫，j为对比萤火虫）
            for i in range(self.pop_size):
                for j in range(self.pop_size):
                    # 核心逻辑：仅当j的亮度优于i时，i才向j移动（适配最大化/最小化目标）
                    if (self.maximize and self.population[j].brightness > self.population[i].brightness) or \
                            (not self.maximize and self.population[j].brightness < self.population[i].brightness):
                        # 1. 计算两只萤火虫之间的欧氏距离
                        r = np.linalg.norm(self.population[i].chrom - self.population[j].chrom)
                        # 2. 计算吸引力（随距离衰减）
                        beta = self.attractiveness(r)
                        # 3. 计算随机扰动（随迭代线性衰减，平衡探索与开发）
                        alpha = self.alpha * (1 - gen / self.max_gen)  # 迭代后期减少扰动，强化局部搜索
                        rand = np.random.uniform(-1, 1, self.dim)  # [-1,1]均匀分布扰动
                        # 4. 更新当前萤火虫位置（核心公式：吸引力引导 + 随机扰动）
                        new_chrom = (self.population[i].chrom +
                                     beta * (self.population[j].chrom - self.population[i].chrom) +
                                     alpha * rand)
                        # 5. 位置越界处理+类型转换（确保变量符合定义范围）
                        new_chrom = self.bound_position(new_chrom)
                        # 6. 评估新位置的适应度、原始目标值和约束违反量
                        new_firefly = Firefly(new_chrom)
                        decoded = decode(new_firefly.chrom, self.var_types)
                        new_firefly.fitness, new_firefly.raw_fitness, new_firefly.violation = self._penalized_fitness(
                            decoded, gen
                        )
                        # 7. 更新新萤火虫的亮度（与惩罚后适应度正相关）
                        new_firefly.brightness = new_firefly.fitness
                        # 8. 贪婪选择：若新位置更优，则替换原萤火虫
                        if (self.maximize and new_firefly.fitness > self.population[i].fitness) or \
                                (not self.maximize and new_firefly.fitness < self.population[i].fitness):
                            self.population[i] = new_firefly

            # 记录当前代的核心指标（适应度、违反量等）
            self._record_fitness(self.population)
            # 按间隔记录种群位置（最后一代强制记录，确保完整演化过程）
            if (gen % interval == 0) or (gen == self.max_gen):
                self._record_positions(self.population, gen=gen)

            # 打印迭代进度（根据有无约束动态调整输出内容，避免无约束时显示无效信息）
            if gen % 10 == 0:
                progress_str = (f"第{gen}/{self.max_gen}代 | "
                                f"最优适应度: {self.best_fitness_history[-1]:.6f} | "
                                f"平均适应度: {self.avg_fitness_history[-1]:.6f}")
                # 仅当有约束时，才显示平均约束违反量
                if self.has_constraints:
                    progress_str += f" | 平均违反量: {self.avg_violation_history[-1]:.6f}"
                print(progress_str)

        # 裁剪位置记录（避免超出设定的可视化代数，减少冗余数据）
        if len(self.position_history) > self.visualize_gens:
            self.position_history = self.position_history[:self.visualize_gens]

        # 算法结束后自动绘制可视化图表（根据有无约束动态生成图表）
        self.visualize()
        # 返回全局最优个体（根据目标方向选择最大/最小适应度个体）
        return max(self.population, key=lambda x: x.fitness) if self.maximize else min(
            self.population, key=lambda x: x.fitness
        )

    def visualize(self):
        """核心可视化：根据有无约束动态调整图表内容"""
        # 1. 适应度与约束违反量图表（有约束时显示双子图，无约束时显示单图）
        if self.has_constraints:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # 子图1：适应度变化曲线
            ax1.plot(range(len(self.best_fitness_history)), self.best_fitness_history, c='red', linewidth=2,
                     label='最优惩罚适应度')
            ax1.plot(range(len(self.best_raw_history)), self.best_raw_history, c='green', linewidth=2, linestyle='--',
                     label='最优原始目标值')
            ax1.plot(range(len(self.avg_fitness_history)), self.avg_fitness_history, c='blue', linewidth=1.5,
                     linestyle='-.', label='平均惩罚适应度')
            ax1.set_xlabel('迭代次数')
            ax1.set_ylabel('适应度/目标值')
            ax1.set_title('FA适应度变化曲线')
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            # 子图2：约束违反量曲线
            ax2.plot(range(len(self.avg_violation_history)), self.avg_violation_history, c='purple', linewidth=2,
                     label='平均约束违反量')
            ax2.axhline(y=0, c='black', linestyle='--', alpha=0.5, label='约束满足线（违反量=0）')
            ax2.set_xlabel('迭代次数')
            ax2.set_ylabel('平均约束违反量')
            ax2.set_title('FA约束违反量变化曲线')
            ax2.grid(True, alpha=0.3)
            ax2.legend()

            plt.tight_layout()
            plt.show()
        else:
            # 无约束时只显示适应度曲线
            plt.figure(figsize=(10, 6))
            plt.plot(range(len(self.best_fitness_history)), self.best_fitness_history, c='red', linewidth=2,
                     label='每代最优适应度')
            plt.plot(range(len(self.avg_fitness_history)), self.avg_fitness_history, c='blue', linewidth=2,
                     linestyle='--', label='每代平均适应度')
            plt.xlabel('迭代次数')
            plt.ylabel('适应度值')
            plt.title('FA适应度变化曲线（无约束）')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.show()

        # 2. 种群位置演化可视化（仅实数变量）
        if not self.position_history:
            return
        sample_pos = self.position_history[0]["positions"]
        real_dim = sample_pos.shape[1] if sample_pos.size > 0 else 0
        all_positions = np.vstack([data["positions"] for data in self.position_history])

        # 2.1 2维实数变量：直接绘制位置演化
        if real_dim == 2:
            fig, ax = plt.subplots(figsize=(10, 6))
            gen_indices = []
            for i, data in enumerate(self.position_history):
                gen_indices.extend([i] * self.pop_size)
            # 颜色表示迭代进程（越深越接近最优代）
            colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))
            scatter = ax.scatter(all_positions[:, 0], all_positions[:, 1], c=colors, alpha=0.6, s=50)

            # 标记全局最优点
            best_idx = np.argmax([f.fitness for f in self.population]) if self.maximize else np.argmin(
                [f.fitness for f in self.population])
            best_decoded = decode(self.population[best_idx].chrom, self.var_types)
            best_pos = best_decoded["real_0"]
            ax.scatter(best_pos[0], best_pos[1], c='red', s=150, marker='*', label='全局最优')

            # 仅在有约束时绘制约束边界
            if self.has_constraints and self.ineq_constraints:
                x_min, x_max = all_positions[:, 0].min() - 0.5, all_positions[:, 0].max() + 0.5
                y_min, y_max = all_positions[:, 1].min() - 0.5, all_positions[:, 1].max() + 0.5
                xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200), np.linspace(y_min, y_max, 200))

                for i, h in enumerate(self.ineq_constraints):
                    # 计算约束值（h(x) ≤ 0 为可行域）
                    grid_decoded = {"real_0": (xx, yy)}
                    constraint_vals = h(grid_decoded)
                    # 获取约束边界线段
                    contour = ax.contour(xx, yy, constraint_vals, levels=[0], alpha=0)
                    # 遍历所有线段并绘制
                    for seg in contour.allsegs[0]:
                        ax.plot(seg[:, 0], seg[:, 1], color=f'C{i}', linewidth=2, linestyle='--')
                    # 手动添加图例
                    ax.plot([], [], color=f'C{i}', linewidth=2, linestyle='--', label=f'约束 {i + 1}')

            # 颜色条与图表设置
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('迭代进程（颜色越深越接近最优代）')
            ax.set_xlabel('变量1')
            ax.set_ylabel('变量2')
            ax.set_title('FA种群位置演化（2D实数变量）')
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.show()

        # 2.2 高维实数变量：PCA降维可视化
        elif real_dim > 2:
            # PCA降维到2维（保留主要特征）
            pca = PCA(n_components=2)
            positions_2d = pca.fit_transform(all_positions)

            fig, ax = plt.subplots(figsize=(10, 6))
            gen_indices = []
            for i, data in enumerate(self.position_history):
                gen_indices.extend([i] * self.pop_size)
            colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))

            # 绘制降维后种群位置
            scatter = ax.scatter(positions_2d[:, 0], positions_2d[:, 1], c=colors, alpha=0.6, s=50)

            # 标记全局最优（降维后位置）
            best_idx = np.argmax([f.fitness for f in self.population]) if self.maximize else np.argmin(
                [f.fitness for f in self.population])
            best_pos = self.position_history[-1]["positions"][best_idx]  # 最后一代最优个体原始位置
            best_pos_2d = pca.transform([best_pos])[0]  # 降维后的最优位置
            ax.scatter(best_pos_2d[0], best_pos_2d[1], c='red', s=150, marker='*', label='全局最优')

            # 图表设置（显示方差解释率）
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('迭代进程（颜色越深越接近最优代）')
            ax.set_xlabel(f'主成分1（解释方差：{pca.explained_variance_ratio_[0]:.2%}）')
            ax.set_ylabel(f'主成分2（解释方差：{pca.explained_variance_ratio_[1]:.2%}）')
            ax.set_title('FA种群位置演化（PCA降维至2D）')
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.show()

    def repair_solution(self, decoded: dict, max_time: float = 1.0, step: float = 0.01) -> dict:
        """修复违反约束的解（仅在有约束时有效）"""
        if self.has_constraints:
            return repair_solution(self, decoded, max_time, step)
        return decoded  # 无约束时直接返回原解

    def is_decoded_feasible(self, decoded, tol=1e-6) -> bool:
        """检查解是否可行（仅在有约束时有效）"""
        if self.has_constraints:
            return is_decoded_feasible(self, decoded, tol)
        return True  # 无约束时所有解均为可行解


# ================= 测试示例（支持有/无约束两种模式）=================
if __name__ == "__main__":
    # 1. 初始化工具（固定随机种子+中文显示）
    fix_random_seed(42)
    init_mlp()

    # 2. 变量定义（2个实数变量）
    var_types = [("real", (2, -2.0, 2.0))]  # 变量范围：x,y ∈ [-2,2]


    # 3. 目标函数（Rosenbrock函数，求最小值→转为最大化问题）
    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]
        # 原始Rosenbrock函数：f(x,y)=(1-x)² + 100(y-x²)²（最小值0，在(1,1)处）
        return -((1 - x) ** 2 + 100 * (y - x ** 2) ** 2)  # 转为最大化


    # 4. 约束条件（可注释掉以测试无约束模式）
    use_constraints = True  # 控制是否使用约束
    eq_constraints = []
    ineq_constraints = []

    if use_constraints:
        # (a) x + y <= 0 → 违反量=x+y（>0时违反）
        def ineq1(decoded: dict) -> float:
            x, y = decoded["real_0"]
            return x + y  # <= 0


        # (b) x² + y² <= 0.5 → 违反量=x²+y²-0.5（>0时违反）
        def ineq2(decoded: dict) -> float:
            x, y = decoded["real_0"]
            return x ** 2 + y ** 2 - 0.5  # <= 0


        # (c) y >= x + 0.3 → x - y + 0.3 <= 0 → 违反量=x-y+0.3（>0时违反）
        def ineq3(decoded: dict) -> float:
            x, y = decoded["real_0"]
            return x - y + 0.3  # <= 0


        ineq_constraints = [ineq1, ineq2, ineq3]

    # 5. 初始化FA算法实例
    fa_optimizer = FA(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=30,
        max_gen=100,
        alpha=0.2,
        beta0=1.0,
        gamma=1.0,
        maximize=True,
        eq_constraints=eq_constraints,
        ineq_constraints=ineq_constraints,
        penalty_coeff=1e3,
        visualize_gens=5
    )

    # 6. 运行优化算法
    print(f"=== 萤火虫优化算法（FA）开始运行 {'(带约束)' if use_constraints else '(无约束)'} ===")
    best_firefly = fa_optimizer.run()
    print(f"=== 萤火虫优化算法（FA）运行结束 {'(带约束)' if use_constraints else '(无约束)'} ===")

    # 7. 解析并输出最优结果
    best_decoded = decode(best_firefly.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]
    min_rosenbrock = -best_firefly.raw_fitness  # 还原为原始函数值

    print("\n========== 最优结果详情 ==========")
    print(f"1. 最优变量值：")
    print(f"   x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"2. 目标函数结果：")
    print(f"   原始Rosenbrock函数值（最小值）：{min_rosenbrock:.6f}")
    print(f"   适应度值：{best_firefly.fitness:.6f}")

    # 仅在有约束时显示约束相关信息
    if use_constraints:
        print(f"3. 约束满足情况：")
        print(f"   约束违反量：{best_firefly.violation:.6f}")
        print(f"   是否为可行解：{'是' if best_firefly.violation <= 1e-6 else '否'}")

        # 尝试修复不可行解
        if best_firefly.violation > 1e-6:
            print("\n========== 修复不可行解 ==========")
            repaired_decoded = fa_optimizer.repair_solution(best_decoded)
            x_rep, y_rep = repaired_decoded["real_0"]
            repaired_raw = evaluate(repaired_decoded)
            repaired_violation = 0.0
            for h in ineq_constraints:
                repaired_violation += max(0.0, h(repaired_decoded))

            print(f"修复后变量值：x = {x_rep:.6f}, y = {y_rep:.6f}")
            print(f"修复后Rosenbrock函数值：{-repaired_raw:.6f}")
            print(f"修复后约束违反量：{repaired_violation:.6f}")
            print(f"修复后是否为可行解：{'是' if repaired_violation <= 1e-6 else '否'}")

        # 输出约束检查详情
        print("\n========== 约束检查详情 ==========")
        for idx, constraint in enumerate(ineq_constraints, 1):
            constraint_val = constraint(best_decoded)
            status = "满足" if constraint_val <= 1e-6 else "违反"
            print(f"不等式约束 {idx}（{constraint.__name__}）：计算值 = {constraint_val:.6f} → {status}")
