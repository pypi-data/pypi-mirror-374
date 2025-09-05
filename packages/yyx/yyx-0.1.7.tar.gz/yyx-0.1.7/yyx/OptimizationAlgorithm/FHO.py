import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from sklearn.decomposition import PCA
from utils import decode, init_mlp, fix_random_seed, repair_solution, is_decoded_feasible, penalty_fun

plt.rcParams["font.family"] = ["SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


# ================= 火鹰个体类（增强约束属性）=================
class FireHawk:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（位置向量）
        self.fitness = None  # 惩罚后适应度（用于算法选择）
        self.raw_fitness = None  # 原始目标值（真实优化目标）
        self.violation = 0.0  # 约束违反量（评估解的可行性）
        self.intensity = None  # 火焰强度（与适应度相关，影响群体交互）

    def __str__(self) -> str:
        if self.fitness is None:
            return "fitness=None"
        return (f"raw={self.raw_fitness:.6f}, fitness={self.fitness:.6f}, "
                f"violation={self.violation:.6f}, intensity={self.intensity:.6f}")


# ================= 带约束的火鹰优化算法（FHO）类 =================
class FHO:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回原始目标值
            pop_size: int = 30,
            max_gen: int = 100,
            alpha: float = 0.5,  # 火焰扩散系数
            beta: float = 0.3,  # 热气流影响系数
            gamma: float = 0.2,  # 随机扰动系数
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
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

        # 约束与目标相关扩展
        self.maximize = maximize
        self.eq_constraints = eq_constraints or []
        self.ineq_constraints = ineq_constraints or []
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
        self.avg_violation_history = []  # 每代平均约束违反量
        self.position_history = []  # 种群位置记录（用于演化可视化）

    def _penalized_fitness(self, decoded: dict, gen: int) -> Tuple[float, float, float]:
        """计算惩罚后适应度、原始目标值、约束违反量"""
        # 1. 计算原始目标值
        raw_val = self.evaluate(decoded)
        # 2. 计算约束违反量
        violation = 0.0
        # 等式约束：允许1e-6误差，违反量=|g(x)|-1e-6（仅保留正值）
        for g in self.eq_constraints:
            violation += max(0.0, abs(g(decoded)) - 1e-6)
        # 不等式约束：违反量=h(x)（仅保留h(x)>0的部分，h(x)≤0为满足）
        for h in self.ineq_constraints:
            violation += max(0.0, h(decoded))
        # 3. 自适应惩罚系数（随迭代增强）
        adaptive_coeff = penalty_fun(gen, self.penalty_coeff, self.max_gen)
        # 4. 按目标方向计算惩罚适应度
        if self.maximize:
            penalized = raw_val - adaptive_coeff * violation
        else:
            penalized = raw_val + adaptive_coeff * violation
        return penalized, raw_val, violation

    def init_firehawk(self, gen: int = 0) -> FireHawk:
        """初始化火鹰个体（含约束属性+火焰强度计算）"""
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
        hawk = FireHawk(np.array(chrom, dtype=float))
        # 计算适应度与约束属性
        decoded = decode(hawk.chrom, self.var_types)
        hawk.fitness, hawk.raw_fitness, hawk.violation = self._penalized_fitness(decoded, gen)
        # 初始化火焰强度（后续会更新）
        hawk.intensity = random.random()
        return hawk

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

    def update_intensity(self, population: List[FireHawk]):
        """根据惩罚后适应度更新火焰强度（适应度越高，强度越大）"""
        fitness_values = np.array([hawk.fitness for hawk in population])
        min_fit, max_fit = np.min(fitness_values), np.max(fitness_values)
        # 避免除以0（所有个体适应度相同时）
        if max_fit - min_fit < 1e-10:
            for hawk in population:
                hawk.intensity = 0.5
        else:
            # 归一化到[0.1, 0.9]，避免强度过小时失去引导作用
            for hawk in population:
                hawk.intensity = 0.1 + 0.8 * (hawk.fitness - min_fit) / (max_fit - min_fit)

    def _record_fitness(self, population: List[FireHawk]):
        """记录每代核心指标（适应度+约束违反量）"""
        fitness_values = [w.fitness for w in population]
        raw_values = [w.raw_fitness for w in population]
        violation_values = [w.violation for w in population]

        # 按目标方向记录最优值
        self.best_fitness_history.append(max(fitness_values) if self.maximize else min(fitness_values))
        self.best_raw_history.append(max(raw_values) if self.maximize else min(raw_values))
        self.avg_fitness_history.append(np.mean(fitness_values))
        self.avg_violation_history.append(np.mean(violation_values))

    def _record_positions(self, population: List[FireHawk], gen: int):
        """记录种群位置（仅提取实数变量用于可视化）"""
        positions = []
        for hawk in population:
            decoded = decode(hawk.chrom, self.var_types)
            real_pos = []
            # 仅保留实数变量（二进制/整数可视化意义不大）
            for key in decoded:
                if key.startswith("real_"):
                    real_pos.extend(decoded[key].tolist())
            positions.append(real_pos)
        self.position_history.append({"gen": gen, "positions": np.array(positions)})

    def run(self) -> FireHawk:
        """运行带约束的火鹰优化算法"""
        # 初始化种群
        self.population = [self.init_firehawk(gen=0) for _ in range(self.pop_size)]
        # 更新初始火焰强度
        self.update_intensity(self.population)
        # 初始状态记录
        self._record_fitness(self.population)
        # 计算位置记录间隔（避免冗余数据）
        interval = max(1, self.max_gen // (self.visualize_gens - 1))
        self._record_positions(self.population, gen=0)

        # 迭代优化
        for gen in range(1, self.max_gen + 1):
            # 1. 确定当前最优个体（火焰源，基于惩罚后适应度）
            best_hawk = max(self.population, key=lambda x: x.fitness) if self.maximize else min(self.population,
                                                                                                key=lambda x: x.fitness)
            best_chrom = best_hawk.chrom.copy()

            # 2. 逐个体更新位置（火焰扩散+热气流+随机探索）
            for i in range(self.pop_size):
                current = self.population[i]

                # a. 火焰扩散：向最优个体靠近，受自身强度影响
                flame_diffusion = self.alpha * current.intensity * (best_chrom - current.chrom)
                # b. 热气流影响：基于变量范围的高斯扰动
                thermal_current = self.beta * (self.high - self.low) * np.random.randn(self.dim)
                # c. 随机探索：均匀分布的随机扰动（平衡探索与开发）
                random_explore = self.gamma * (np.random.rand(self.dim) - 0.5) * (self.high - self.low)

                # 3. 计算新位置并约束
                new_chrom = current.chrom + flame_diffusion + thermal_current + random_explore
                new_chrom = self.bound_position(new_chrom)

                # 4. 计算新个体的适应度与约束属性
                new_hawk = FireHawk(new_chrom)
                decoded = decode(new_hawk.chrom, self.var_types)
                new_hawk.fitness, new_hawk.raw_fitness, new_hawk.violation = self._penalized_fitness(decoded, gen)

                # 5. 贪婪选择：新个体更优则替换
                if (self.maximize and new_hawk.fitness > current.fitness) or (
                        not self.maximize and new_hawk.fitness < current.fitness):
                    self.population[i] = new_hawk

            # 6. 更新所有个体的火焰强度
            self.update_intensity(self.population)

            # 7. 记录当前代信息
            self._record_fitness(self.population)
            # 按间隔记录位置（最后一代必记录）
            if (gen % interval == 0) or (gen == self.max_gen):
                self._record_positions(self.population, gen=gen)

            # 8. 打印迭代进度
            if gen % 10 == 0:
                print(f"第{gen}/{self.max_gen}代 | "
                      f"最优惩罚适应度: {self.best_fitness_history[-1]:.6f} | "
                      f"平均适应度: {self.avg_fitness_history[-1]:.6f} | "
                      f"平均违反量: {self.avg_violation_history[-1]:.6f}")

        # 裁剪位置记录（确保不超过设定代数）
        if len(self.position_history) > self.visualize_gens:
            self.position_history = self.position_history[:self.visualize_gens]

        # 算法结束后自动绘制可视化图表
        self.visualize()
        # 返回全局最优个体
        return max(self.population, key=lambda x: x.fitness) if self.maximize else min(self.population,
                                                                                       key=lambda x: x.fitness)

    def visualize(self):
        """核心可视化：适应度曲线+约束违反量+种群位置演化"""
        # 1. 适应度与约束违反量双子图
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
        ax1.set_title('FHO适应度变化曲线')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # 子图2：约束违反量曲线（有约束时）/ 原始目标值（无约束时）
        if self.eq_constraints or self.ineq_constraints:
            ax2.plot(range(len(self.avg_violation_history)), self.avg_violation_history, c='purple', linewidth=2,
                     label='平均约束违反量')
            ax2.axhline(y=0, c='black', linestyle='--', alpha=0.5, label='约束满足线（违反量=0）')
            ax2.set_xlabel('迭代次数')
            ax2.set_ylabel('平均约束违反量')
            ax2.set_title('FHO约束违反量变化曲线')
        else:
            ax2.plot(range(len(self.best_raw_history)), self.best_raw_history, c='green', linewidth=2,
                     label='最优原始目标值')
            ax2.set_xlabel('迭代次数')
            ax2.set_ylabel('原始目标值')
            ax2.set_title('FHO原始目标值变化曲线')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

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
            best_idx = np.argmax([w.fitness for w in self.population]) if self.maximize else np.argmin(
                [w.fitness for w in self.population])
            best_decoded = decode(self.population[best_idx].chrom, self.var_types)
            best_pos = best_decoded["real_0"]
            ax.scatter(best_pos[0], best_pos[1], c='red', s=150, marker='*', label='全局最优')

            # 绘制约束边界（修复Matplotlib 3.8+弃用警告）
            if self.ineq_constraints:
                x_min, x_max = all_positions[:, 0].min() - 0.5, all_positions[:, 0].max() + 0.5
                y_min, y_max = all_positions[:, 1].min() - 0.5, all_positions[:, 1].max() + 0.5
                xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200), np.linspace(y_min, y_max, 200))

                for i, h in enumerate(self.ineq_constraints):
                    # 计算约束值（h(x) ≤ 0 为可行域）
                    grid_decoded = {"real_0": (xx, yy)}
                    constraint_vals = h(grid_decoded)
                    # 用contour+allsegs获取边界线段，替代deprecated的collections
                    contour = ax.contour(xx, yy, constraint_vals, levels=[0], alpha=0)
                    # 遍历所有线段并绘制
                    for seg in contour.allsegs[0]:
                        ax.plot(seg[:, 0], seg[:, 1], color=f'C{i}', linewidth=2, linestyle='--')
                    # 手动添加图例（解决contour无label问题）
                    ax.plot([], [], color=f'C{i}', linewidth=2, linestyle='--', label=f'约束 {i + 1}')

            # 颜色条与图表设置
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('迭代进程（颜色越深越接近最优代）')
            ax.set_xlabel('变量1')
            ax.set_ylabel('变量2')
            ax.set_title('FHO种群位置演化（2D实数变量）')
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
            best_idx = np.argmax([w.fitness for w in self.population]) if self.maximize else np.argmin(
                [w.fitness for w in self.population])
            best_pos = self.position_history[-1]["positions"][best_idx]  # 最后一代最优个体原始位置
            best_pos_2d = pca.transform([best_pos])[0]  # 降维后的最优位置
            ax.scatter(best_pos_2d[0], best_pos_2d[1], c='red', s=150, marker='*', label='全局最优')

            # 图表设置（显示方差解释率，说明降维有效性）
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('迭代进程（颜色越深越接近最优代）')
            ax.set_xlabel(f'主成分1（解释方差：{pca.explained_variance_ratio_[0]:.2%}）')
            ax.set_ylabel(f'主成分2（解释方差：{pca.explained_variance_ratio_[1]:.2%}）')
            ax.set_title('FHO种群位置演化（PCA降维至2D）')
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.show()

    def repair_solution(self, decoded: dict, max_time: float = 1.0, step: float = 0.01) -> dict:
        """修复违反约束的解（与其他优化算法接口对齐）"""
        return repair_solution(self, decoded, max_time, step)

    def is_decoded_feasible(self, decoded, tol=1e-6) -> bool:
        """检查解是否可行（约束满足判定）"""
        return is_decoded_feasible(self, decoded, tol)

    # ================= 完整测试示例（使用指定目标函数与约束）=================
if __name__ == "__main__":
    # 1. 初始化工具（固定随机种子+中文显示）
    fix_random_seed(42)
    init_mlp()

    # 2. 变量定义（2个实数变量，适配指定目标函数定义域）
    var_types = [("real", (2, -2.0, 2.0))]  # 变量范围：x,y ∈ [-2,2]（Rosenbrock函数常用域）

    # 3. 目标函数（指定的Rosenbrock函数，求最小值→转为最大化问题）
    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]
        # 原始Rosenbrock函数：f(x,y)=(1-x)² + 100(y-x²)²（最小值0，在(1,1)处）
        return -((1 - x) ** 2 + 100 * (y - x ** 2) ** 2)  # 转为最大化：适应度越大，原始值越小

    # 4. 约束条件（指定的3个“敌对”不等式约束）
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

    # 5. 初始化FHO算法实例
    fho_optimizer = FHO(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=30,  # 种群规模
        max_gen=100,  # 最大迭代次数
        alpha=0.5,  # 火焰扩散系数
        beta=0.3,  # 热气流影响系数
        gamma=0.2,  # 随机扰动系数
        maximize=True,  # 目标方向：最大化（因目标函数取负）
        eq_constraints=[],  # 无等式约束
        ineq_constraints=[ineq1, ineq2, ineq3],  # 3个指定不等式约束
        penalty_coeff=1e3,  # 基础惩罚系数（平衡目标与约束）
        visualize_gens=5  # 记录5个关键代用于位置演化可视化
    )

    # 6. 运行优化算法
    print("=== 火鹰优化算法（FHO）开始运行 ===")
    best_hawk = fho_optimizer.run()
    print("=== 火鹰优化算法（FHO）运行结束 ===")

    # 7. 解析并输出最优结果
    best_decoded = decode(best_hawk.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]
    # 还原为原始Rosenbrock函数值（因目标函数取负）
    min_rosenbrock = -best_hawk.raw_fitness

    print("\n========== 最优结果详情 ==========")
    print(f"1. 最优变量值：")
    print(f"   x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"2. 目标函数结果：")
    print(f"   原始Rosenbrock函数值（最小值）：{min_rosenbrock:.6f}")  # 理论最小值0
    print(f"   惩罚后适应度：{best_hawk.fitness:.6f}")
    print(f"3. 约束满足情况：")
    print(f"   约束违反量：{best_hawk.violation:.6f}")
    print(f"   是否为可行解：{'是' if best_hawk.violation <= 1e-6 else '否'}")

    # 8. 若最优解不可行，尝试修复并输出修复结果
    if best_hawk.violation > 1e-6:
        print("\n========== 修复不可行解 ==========")
        repaired_decoded = fho_optimizer.repair_solution(best_decoded, max_time=1.0, step=0.01)
        x_rep, y_rep = repaired_decoded["real_0"]
        # 计算修复后的值
        repaired_raw = evaluate(repaired_decoded)
        repaired_violation = 0.0
        for h in fho_optimizer.ineq_constraints:
            repaired_violation += max(0.0, h(repaired_decoded))

        print(f"修复后变量值：x = {x_rep:.6f}, y = {y_rep:.6f}")
        print(f"修复后Rosenbrock函数值：{-repaired_raw:.6f}")
        print(f"修复后约束违反量：{repaired_violation:.6f}")
        print(f"修复后是否为可行解：{'是' if repaired_violation <= 1e-6 else '否'}")

    # 9. 输出约束检查详情（逐约束验证满足状态）
    print("\n========== 约束检查详情 ==========")
    for idx, constraint in enumerate(fho_optimizer.ineq_constraints, 1):
        constraint_val = constraint(best_decoded)
        status = "满足" if constraint_val <= 1e-6 else "违反"
        print(f"不等式约束 {idx}（{constraint.__name__}）：计算值 = {constraint_val:.6f} → {status}")