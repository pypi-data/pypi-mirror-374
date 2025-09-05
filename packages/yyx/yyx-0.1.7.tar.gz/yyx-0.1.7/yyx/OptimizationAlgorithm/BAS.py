import numpy as np
import random
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from typing import List, Tuple, Callable
from utils import decode, init_mlp, fix_random_seed, repair_solution, is_decoded_feasible, penalty_fun

# 确保中文显示正常
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False


# ================= 天牛个体类（增强约束属性）=================
class Beetle:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（位置向量）
        self.fitness = None  # 惩罚后适应度（算法选择依据）
        self.raw_fitness = None  # 原始目标值（真实优化目标）
        self.violation = 0.0  # 约束违反量（评估解的可行性）
        self.step = None  # 步长（动态调整）
        self.direction = None  # 最近搜索方向（用于可视化）

    def __str__(self) -> str:
        if self.fitness is None:
            return "fitness=None"
        return (f"raw={self.raw_fitness:.6f}, fitness={self.fitness:.6f}, "
                f"violation={self.violation:.6f}, step={self.step:.6f}")


# ================= 带约束的天牛须算法（BAS）类 =================
class BAS:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回原始目标值
            pop_size: int = 1,  # 可设置为1（标准BAS）或更大值（改进版）
            max_gen: int = 100,
            step_init: float = 1.0,  # 初始步长
            step_decay: float = 0.95,  # 步长衰减系数
            step_min: float = 1e-5,  # 最小步长（避免步长过小）
            antenna_len: float = 0.5,  # 触角长度（相对于步长的比例）
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
        self.step_init = step_init
        self.step_decay = step_decay
        self.step_min = step_min
        self.antenna_len = antenna_len

        # 约束与目标扩展
        self.maximize = maximize
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

    def init_beetle(self, gen: int = 0) -> Beetle:
        """初始化天牛个体（带约束属性）"""
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

        beetle = Beetle(np.array(chrom, dtype=float))
        beetle.step = self.step_init  # 初始化步长
        # 计算初始适应度
        decoded = decode(beetle.chrom, self.var_types)
        beetle.fitness, beetle.raw_fitness, beetle.violation = self._penalized_fitness(decoded, gen)
        return beetle

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

    def random_direction(self) -> np.ndarray:
        """生成随机单位方向向量（天牛搜索方向）"""
        dir_vec = np.random.randn(self.dim)
        norm = np.linalg.norm(dir_vec)
        return dir_vec / norm if norm != 0 else np.ones(self.dim) / np.sqrt(self.dim)

    def run(self) -> Beetle:
        """运行带约束的天牛须算法（完整实现）"""
        # 1. 初始化种群
        self.population = [self.init_beetle(gen=0) for _ in range(self.pop_size)]

        # 2. 初始状态记录
        self._record_fitness(self.population)
        interval = max(1, self.max_gen // (self.visualize_gens - 1))  # 位置记录间隔
        self._record_positions(self.population, gen=0)

        # 3. 迭代优化
        for gen in range(1, self.max_gen + 1):
            # 对每个天牛进行搜索
            for beetle in self.population:
                # 3.1 生成随机方向向量
                dir_vec = self.random_direction()
                beetle.direction = dir_vec  # 记录方向用于可视化

                # 3.2 计算左右触角位置
                len_antenna = self.antenna_len * beetle.step  # 触角长度与步长相关
                x_left = beetle.chrom + dir_vec * len_antenna / 2  # 左触角
                x_right = beetle.chrom - dir_vec * len_antenna / 2  # 右触角

                # 3.3 评估左右触角的适应度（带约束）
                x_left = self.bound_position(x_left)
                x_right = self.bound_position(x_right)
                decoded_left = decode(x_left, self.var_types)
                decoded_right = decode(x_right, self.var_types)
                fit_left, _, _ = self._penalized_fitness(decoded_left, gen)
                fit_right, _, _ = self._penalized_fitness(decoded_right, gen)

                # 3.4 更新位置：向适应度更高的方向移动
                if (self.maximize and fit_left > fit_right) or (not self.maximize and fit_left < fit_right):
                    beetle.chrom += dir_vec * beetle.step
                else:
                    beetle.chrom -= dir_vec * beetle.step

                # 3.5 边界处理与适应度更新
                beetle.chrom = self.bound_position(beetle.chrom)
                decoded = decode(beetle.chrom, self.var_types)
                beetle.fitness, beetle.raw_fitness, beetle.violation = self._penalized_fitness(decoded, gen)

                # 3.6 步长衰减（不小于最小值）
                beetle.step = max(self.step_min, beetle.step * self.step_decay)

            # 3.7 记录当前代信息
            self._record_fitness(self.population)
            # 按间隔记录位置（最后一代强制记录）
            if (gen % interval == 0) or (gen == self.max_gen):
                self._record_positions(self.population, gen=gen)

            # 3.8 打印进度
            if gen % 10 == 0:
                progress_str = (f"第{gen}/{self.max_gen}代 | "
                                f"最优适应度: {self.best_fitness_history[-1]:.6f} | "
                                f"平均适应度: {self.avg_fitness_history[-1]:.6f}")
                if self.has_constraints:
                    progress_str += f" | 平均违反量: {self.avg_violation_history[-1]:.6f}"
                print(progress_str)

        # 4. 裁剪位置记录
        if len(self.position_history) > self.visualize_gens:
            self.position_history = self.position_history[:self.visualize_gens]

        # 5. 自动可视化
        self.visualize()

        # 6. 返回全局最优个体
        return max(self.population, key=lambda x: x.fitness) if self.maximize else min(
            self.population, key=lambda x: x.fitness
        )

    def _record_fitness(self, population: List[Beetle]):
        """记录每代适应度指标"""
        fitness_values = [b.fitness for b in population]
        raw_values = [b.raw_fitness for b in population]

        self.best_fitness_history.append(max(fitness_values) if self.maximize else min(fitness_values))
        self.best_raw_history.append(max(raw_values) if self.maximize else min(raw_values))
        self.avg_fitness_history.append(np.mean(fitness_values))

        if self.has_constraints:
            violation_values = [b.violation for b in population]
            self.avg_violation_history.append(np.mean(violation_values))

    def _record_positions(self, population: List[Beetle], gen: int):
        """记录种群位置（仅实数变量）"""
        positions = []
        for beetle in population:
            decoded = decode(beetle.chrom, self.var_types)
            real_pos = []
            for key in decoded:
                if key.startswith("real_"):
                    real_pos.extend(decoded[key].tolist())
            positions.append(real_pos)
        self.position_history.append({"gen": gen, "positions": np.array(positions)})

    def visualize(self):
        """可视化适应度曲线和种群位置演化"""
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
            ax1.set_title('天牛须算法适应度变化曲线（带约束）')
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            # 子图2：约束违反量曲线
            ax2.plot(range(len(self.avg_violation_history)), self.avg_violation_history,
                     c='purple', linewidth=2, label='平均约束违反量')
            ax2.axhline(y=0, c='black', linestyle='--', alpha=0.5, label='约束满足线')
            ax2.set_xlabel('迭代次数')
            ax2.set_ylabel('平均约束违反量')
            ax2.set_title('天牛须算法约束违反量变化曲线')
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
            plt.title('天牛须算法适应度变化曲线（无约束）')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.show()

        # 2. 种群位置演化可视化
        if not self.position_history:
            return
        sample_pos = self.position_history[0]["positions"]
        real_dim = sample_pos.shape[1] if sample_pos.size > 0 else 0
        all_positions = np.vstack([data["positions"] for data in self.position_history])

        # 2.1 2维实数变量可视化
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
            ax.set_title('天牛须算法种群位置演化（2D实数变量）')
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.show()

        # 2.2 高维实数变量PCA降维可视化
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
            ax.set_title(f'天牛须算法种群位置演化（PCA降维至2D，原始维度{real_dim}）')
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

    # 4. 初始化BAS算法
    bas_optimizer = BAS(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=5,  # 改进版BAS，使用5个个体增强搜索
        max_gen=150,
        step_init=1.0,  # 初始步长
        step_decay=0.95,  # 步长衰减
        step_min=1e-5,  # 最小步长
        antenna_len=0.5,  # 触角长度比例
        maximize=True,
        eq_constraints=eq_constraints,
        ineq_constraints=ineq_constraints,
        penalty_coeff=1e3,
        visualize_gens=6
    )

    # 5. 运行算法
    print(f"=== 天牛须算法（BAS）开始运行 {'(带约束)' if use_constraints else '(无约束)'} ===")
    best_beetle = bas_optimizer.run()
    print(f"=== 天牛须算法（BAS）运行结束 {'(带约束)' if use_constraints else '(无约束)'} ===")

    # 6. 解析并输出结果
    best_decoded = decode(best_beetle.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]
    min_raw_val = -best_beetle.raw_fitness  # 还原为原始函数值

    print("\n========== 最优结果详情 ==========")
    print(f"1. 最优变量值：")
    print(f"   x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"2. 目标函数结果：")
    print(f"   原始Rosenbrock函数值（最小值）：{min_raw_val:.6f}")
    print(f"   算法适应度值：{best_beetle.fitness:.6f}")

    # 带约束时输出约束信息
    if use_constraints:
        print(f"3. 约束满足情况：")
        print(f"   总约束违反量：{best_beetle.violation:.6f}")
        is_feasible = best_beetle.violation <= 1e-6
        print(f"   是否为可行解：{'是' if is_feasible else '否'}")

        if not is_feasible:
            print("\n========== 修复不可行解 ==========")
            repaired_decoded = bas_optimizer.repair_solution(best_decoded, max_time=1.5, step=0.005)
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
