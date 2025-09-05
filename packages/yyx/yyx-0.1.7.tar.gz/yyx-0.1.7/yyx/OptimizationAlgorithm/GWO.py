import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from sklearn.decomposition import PCA
from utils import decode, init_mlp, fix_random_seed, repair_solution, is_decoded_feasible, penalty_fun

plt.rcParams["font.family"] = ["SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


# ================= 灰狼个体类（增强约束属性）=================
class GreyWolf:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（位置向量）
        self.fitness = None  # 惩罚后适应度（用于算法选择）
        self.raw_fitness = None  # 原始目标值（真实优化目标）
        self.violation = 0.0  # 约束违反量（评估解的可行性）

    def __str__(self) -> str:
        if self.fitness is None:
            return "fitness=None"
        return (f"raw={self.raw_fitness:.6f}, fitness={self.fitness:.6f}, "
                f"violation={self.violation:.6f}")


# ================= 带约束的灰狼优化算法（GWO）类 =================
class GWO:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回原始目标值
            pop_size: int = 30,
            max_gen: int = 100,
            a_decrease: float = 2.0,  # 系数a的初始值（随迭代线性下降到0）
            maximize: bool = True,  # 目标方向（最大化/最小化）
            eq_constraints: List[Callable[[dict], float]] = None,  # 等式约束：g(x)=0
            ineq_constraints: List[Callable[[dict], float]] = None,  # 不等式约束：h(x)≤0
            penalty_coeff: float = 1e3,  # 基础惩罚系数
            visualize_gens: int = 5  # 记录种群位置的代数间隔（用于可视化）
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = max(pop_size, 3)  # 确保至少3只狼（α, β, δ）
        self.max_gen = max_gen
        self.a_decrease = a_decrease

        # 约束与目标相关扩展
        self.maximize = maximize
        self.eq_constraints = eq_constraints or []
        self.ineq_constraints = ineq_constraints or []
        self.penalty_coeff = penalty_coeff
        self.visualize_gens = visualize_gens

        # 解析变量范围（位置约束+类型转换）
        self.var_ranges = []  # (类型, 下界, 上界)
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

        # 迭代记录（核心指标+位置数据）
        self.best_fitness_history = []  # 每代最优惩罚适应度（α狼）
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

    def init_wolf(self, gen: int = 0) -> GreyWolf:
        """初始化灰狼个体（含约束属性计算）"""
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
        wolf = GreyWolf(np.array(chrom, dtype=float))
        # 计算初始个体的适应度与约束属性
        decoded = decode(wolf.chrom, self.var_types)
        wolf.fitness, wolf.raw_fitness, wolf.violation = self._penalized_fitness(decoded, gen)
        return wolf

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

    def _record_fitness(self, population: List[GreyWolf]):
        """记录每代核心指标（适应度+约束违反量）"""
        fitness_values = [w.fitness for w in population]
        raw_values = [w.raw_fitness for w in population]
        violation_values = [w.violation for w in population]

        self.best_fitness_history.append(max(fitness_values) if self.maximize else min(fitness_values))
        self.best_raw_history.append(max(raw_values) if self.maximize else min(raw_values))
        self.avg_fitness_history.append(np.mean(fitness_values))
        self.avg_violation_history.append(np.mean(violation_values))

    def _record_positions(self, population: List[GreyWolf], gen: int):
        """记录种群位置（仅提取实数变量用于可视化）"""
        positions = []
        for wolf in population:
            decoded = decode(wolf.chrom, self.var_types)
            real_pos = []
            for key in decoded:
                if key.startswith("real_"):
                    real_pos.extend(decoded[key].tolist())
            positions.append(real_pos)
        self.position_history.append({"gen": gen, "positions": np.array(positions)})

    def run(self) -> GreyWolf:
        """运行带约束的灰狼优化算法"""
        # 初始化种群
        self.population = [self.init_wolf(gen=0) for _ in range(self.pop_size)]
        # 初始状态记录
        self._record_fitness(self.population)
        interval = max(1, self.max_gen // (self.visualize_gens - 1))
        self._record_positions(self.population, gen=0)

        # 迭代优化
        for gen in range(1, self.max_gen + 1):
            # 计算当前a值（线性下降）
            a = self.a_decrease - (self.a_decrease / self.max_gen) * gen

            # 排序种群，选出α(最优)、β(次优)、δ(第三优)
            sorted_pop = sorted(
                self.population,
                key=lambda x: x.fitness,
                reverse=self.maximize
            )
            alpha, beta, delta = sorted_pop[0], sorted_pop[1], sorted_pop[2]

            # 更新每只灰狼位置
            for i in range(self.pop_size):
                # α狼引导分量X1
                r1, r2 = random.random(), random.random()
                A1 = 2 * a * r1 - a
                C1 = 2 * r2
                D_alpha = abs(C1 * alpha.chrom - self.population[i].chrom)
                X1 = alpha.chrom - A1 * D_alpha

                # β狼引导分量X2
                r1, r2 = random.random(), random.random()
                A2 = 2 * a * r1 - a
                C2 = 2 * r2
                D_beta = abs(C2 * beta.chrom - self.population[i].chrom)
                X2 = beta.chrom - A2 * D_beta

                # δ狼引导分量X3
                r1, r2 = random.random(), random.random()
                A3 = 2 * a * r1 - a
                C3 = 2 * r2
                D_delta = abs(C3 * delta.chrom - self.population[i].chrom)
                X3 = delta.chrom - A3 * D_delta

                # 计算新位置并约束
                new_chrom = (X1 + X2 + X3) / 3
                new_chrom = self.bound_position(new_chrom)

                # 更新个体属性
                self.population[i].chrom = new_chrom
                decoded = decode(self.population[i].chrom, self.var_types)
                self.population[i].fitness, self.population[i].raw_fitness, self.population[i].violation = self._penalized_fitness(decoded, gen)

            # 记录当前代信息
            self._record_fitness(self.population)
            if (gen % interval == 0) or (gen == self.max_gen):
                self._record_positions(self.population, gen=gen)

            # 打印进度
            if gen % 10 == 0:
                print(f"第{gen}/{self.max_gen}代 | "
                      f"最优惩罚适应度: {self.best_fitness_history[-1]:.6f} | "
                      f"平均适应度: {self.avg_fitness_history[-1]:.6f} | "
                      f"平均违反量: {self.avg_violation_history[-1]:.6f}")

        # 裁剪位置记录
        if len(self.position_history) > self.visualize_gens:
            self.position_history = self.position_history[:self.visualize_gens]

        # 可视化核心图表
        self.visualize()
        # 返回全局最优个体
        return max(self.population, key=lambda x: x.fitness) if self.maximize else min(self.population, key=lambda x: x.fitness)

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
        ax1.set_title('GWO适应度变化曲线')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # 子图2：约束违反量曲线（有约束时）
        if self.eq_constraints or self.ineq_constraints:
            ax2.plot(range(len(self.avg_violation_history)), self.avg_violation_history, c='purple', linewidth=2,
                     label='平均约束违反量')
            ax2.axhline(y=0, c='black', linestyle='--', alpha=0.5, label='约束满足线（违反量=0）')
            ax2.set_xlabel('迭代次数')
            ax2.set_ylabel('平均约束违反量')
            ax2.set_title('GWO约束违反量变化曲线')
        else:
            ax2.plot(range(len(self.best_raw_history)), self.best_raw_history, c='green', linewidth=2,
                     label='最优原始目标值')
            ax2.set_xlabel('迭代次数')
            ax2.set_ylabel('原始目标值')
            ax2.set_title('GWO原始目标值变化曲线')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()
        plt.show()

        # 2. 种群位置演化可视化
        if not self.position_history:
            return
        sample_pos = self.position_history[0]["positions"]
        real_dim = sample_pos.shape[1] if sample_pos.size > 0 else 0
        all_positions = np.vstack([data["positions"] for data in self.position_history])

        # 2.1 2维实数变量：直接绘制
        if real_dim == 2:
            fig, ax = plt.subplots(figsize=(10, 6))
            gen_indices = []
            for i, data in enumerate(self.position_history):
                gen_indices.extend([i] * self.pop_size)
            colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))
            scatter = ax.scatter(all_positions[:, 0], all_positions[:, 1], c=colors, alpha=0.6, s=50)

            # 标记全局最优
            best_idx = np.argmax([w.fitness for w in self.population]) if self.maximize else np.argmin(
                [w.fitness for w in self.population])
            best_decoded = decode(self.population[best_idx].chrom, self.var_types)
            best_pos = best_decoded["real_0"]
            ax.scatter(best_pos[0], best_pos[1], c='red', s=150, marker='*', label='全局最优')

            # 绘制约束边界（修复Matplotlib警告）
            if self.ineq_constraints:
                x_min, x_max = all_positions[:, 0].min() - 0.5, all_positions[:, 0].max() + 0.5
                y_min, y_max = all_positions[:, 1].min() - 0.5, all_positions[:, 1].max() + 0.5
                xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200), np.linspace(y_min, y_max, 200))

                for i, h in enumerate(self.ineq_constraints):
                    grid_decoded = {"real_0": (xx, yy)}
                    constraint_vals = h(grid_decoded)
                    # 用allsegs获取边界线段（替代deprecated的collections）
                    contour = ax.contour(xx, yy, constraint_vals, levels=[0], alpha=0)
                    for seg in contour.allsegs[0]:  # 提取level=0的所有线段
                        ax.plot(seg[:, 0], seg[:, 1], color=f'C{i}', linewidth=2, linestyle='--')
                    # 手动添加图例（解决contour无label问题）
                    ax.plot([], [], color=f'C{i}', linewidth=2, linestyle='--', label=f'约束 {i + 1}')

            # 颜色条与图表设置
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('迭代进程（颜色越深越接近最优代）')
            ax.set_xlabel('变量1')
            ax.set_ylabel('变量2')
            ax.set_title('GWO种群位置演化（2D实数变量）')
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
            best_pos = self.position_history[-1]["positions"][best_idx]  # 最后一代最优个体的原始位置
            best_pos_2d = pca.transform([best_pos])[0]  # 降维后的最优位置
            ax.scatter(best_pos_2d[0], best_pos_2d[1], c='red', s=150, marker='*', label='全局最优')

            # 图表设置（显示方差解释率）
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('迭代进程（颜色越深越接近最优代）')
            ax.set_xlabel(f'主成分1（解释方差：{pca.explained_variance_ratio_[0]:.2%}）')
            ax.set_ylabel(f'主成分2（解释方差：{pca.explained_variance_ratio_[1]:.2%}）')
            ax.set_title('GWO种群位置演化（PCA降维至2D）')
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

# ================= 完整测试示例（main函数）=================
if __name__ == "__main__":
    # 1. 初始化工具（固定随机种子+中文显示）
    fix_random_seed(42)
    init_mlp()

    # 2. 定义优化变量（2个实数变量，经典Rastrigin函数定义域）
    var_types = [("real", (2, -5.12, 5.12))]  # (变量类型, (变量数, 下界, 上界))

    # 3. 定义目标函数（Rastrigin函数，求最小值→转为最大化问题）
    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]
        # 原始Rastrigin函数：f(x,y)=20 + x² + y² - 10cos(2πx) - 10cos(2πy)（最小值0）
        raw_val = 20 + x ** 2 + y ** 2 - 10 * np.cos(2 * np.pi * x) - 10 * np.cos(2 * np.pi * y)
        return -raw_val  # 转为最大化：适应度越大，原始函数值越小

    # 4. 定义约束条件（3个不等式约束，模拟实际优化场景）
    # 约束1：x + y ≤ 2 → 违反量=x+y-2（>0时违反）
    def ineq_constraint1(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return x + y - 2

    # 约束2：x - y ≥ -3 → y - x ≤ 3 → 违反量=y-x-3（>0时违反）
    def ineq_constraint2(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return y - x - 3

    # 约束3：x² + y² ≥ 1 → 违反量=1 - (x² + y²)（>0时违反）
    def ineq_constraint3(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return 1 - (x ** 2 + y ** 2)

    # 5. 初始化GWO算法实例
    gwo_optimizer = GWO(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=30,  # 种群规模（至少3）
        max_gen=100,  # 最大迭代次数
        a_decrease=2.0,  # 系数a初始值（线性下降到0）
        maximize=True,  # 目标方向：最大化（因目标函数取负）
        eq_constraints=[],  # 无等式约束
        ineq_constraints=[ineq_constraint1, ineq_constraint2, ineq_constraint3],  # 3个不等式约束
        penalty_coeff=1e3,  # 基础惩罚系数
        visualize_gens=5  # 记录5个关键代用于位置演化可视化
    )

    # 6. 运行优化算法
    print("=== 灰狼优化算法（GWO）开始运行 ===")
    best_wolf = gwo_optimizer.run()
    print("=== 灰狼优化算法（GWO）运行结束 ===")

    # 7. 解析并输出最优结果
    best_decoded = decode(best_wolf.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]
    # 还原为原始Rastrigin函数值（因目标函数取负）
    min_rastrigin = -best_wolf.raw_fitness

    print("\n========== 最优结果详情 ==========")
    print(f"1. 最优变量值：")
    print(f"   x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"2. 目标函数结果：")
    print(f"   原始Rastrigin函数值（最小值）：{min_rastrigin:.6f}")  # 理论最小值0
    print(f"   惩罚后适应度：{best_wolf.fitness:.6f}")
    print(f"3. 约束满足情况：")
    print(f"   约束违反量：{best_wolf.violation:.6f}")
    print(f"   是否为可行解：{'是' if best_wolf.violation <= 1e-6 else '否'}")

    # 8. 若最优解不可行，尝试修复并输出修复结果
    if best_wolf.violation > 1e-6:
        print("\n========== 修复不可行解 ==========")
        repaired_decoded = gwo_optimizer.repair_solution(best_decoded, max_time=1.0, step=0.01)
        x_rep, y_rep = repaired_decoded["real_0"]
        # 计算修复后的值
        repaired_raw = evaluate(repaired_decoded)
        repaired_violation = 0.0
        for h in gwo_optimizer.ineq_constraints:
            repaired_violation += max(0.0, h(repaired_decoded))

        print(f"修复后变量值：x = {x_rep:.6f}, y = {y_rep:.6f}")
        print(f"修复后Rastrigin函数值：{-repaired_raw:.6f}")
        print(f"修复后约束违反量：{repaired_violation:.6f}")
        print(f"修复后是否为可行解：{'是' if repaired_violation <= 1e-6 else '否'}")
