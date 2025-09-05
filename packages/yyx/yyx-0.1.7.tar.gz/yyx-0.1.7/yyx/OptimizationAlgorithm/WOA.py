import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from utils import decode, init_mlp, fix_random_seed, repair_solution, is_decoded_feasible, penalty_fun
from sklearn.decomposition import PCA


class Whale:
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


# ================= 带约束的鲸鱼优化算法（WOA）类 =================
class WOA:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回原始目标值
            pop_size: int = 30,
            max_gen: int = 100,
            a_decrease: float = 2.0,  # 系数a的初始值（随迭代线性下降到0）
            b: float = 1.0,  # 螺旋形状参数（固定为1）
            maximize: bool = True,  # 目标方向（最大化/最小化）
            eq_constraints: List[Callable[[dict], float]] = None,  # 等式约束
            ineq_constraints: List[Callable[[dict], float]] = None,  # 不等式约束
            penalty_coeff: float = 1e3,  # 基础惩罚系数
            visualize_gens: int = 5  # 可视化记录的代数间隔
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.a_decrease = a_decrease
        self.b = b

        # 约束相关参数（与GA/PSO/SA完全对齐）
        self.maximize = maximize
        self.eq_constraints = eq_constraints or []
        self.ineq_constraints = ineq_constraints or []
        self.penalty_coeff = penalty_coeff
        self.visualize_gens = visualize_gens

        # 解析变量范围（用于位置更新时约束）
        self.var_ranges = []  # 存储每个变量的范围：(类型, 下界, 上界)
        self.dim = 0  # 总变量数
        for vtype, info in var_types:
            if vtype == "binary":
                n = info
                self.dim += n
                self.var_ranges.extend([(vtype, 0, 1)] * n)  # 二进制变量范围[0,1]
            elif vtype == "integer":
                n, low, high = info
                self.dim += n
                self.var_ranges.extend([(vtype, low, high)] * n)
            elif vtype == "real":
                n, low, high = info
                self.dim += n
                self.var_ranges.extend([(vtype, low, high)] * n)

        # 记录迭代过程（新增约束相关指标）
        self.best_fitness_history = []  # 每代最优惩罚适应度
        self.best_raw_history = []  # 每代最优原始目标值
        self.avg_fitness_history = []  # 每代平均惩罚适应度
        self.avg_violation_history = []  # 每代平均约束违反量
        self.position_history = []  # 可视化用的种群位置记录

    def _penalized_fitness(self, decoded: dict, gen: int) -> Tuple[float, float, float]:
        """计算惩罚后适应度、原始目标值、约束违反量（复用通用惩罚函数）"""
        # 1. 计算原始目标值
        raw_val = self.evaluate(decoded)
        # 2. 计算约束违反量（等式+不等式）
        violation = 0.0
        # 等式约束：|g(x)| - 1e-6（允许微小误差）
        for g in self.eq_constraints:
            violation += max(0.0, abs(g(decoded)) - 1e-6)
        # 不等式约束：h(x) > 0 的部分（h(x) ≤ 0 为满足约束）
        for h in self.ineq_constraints:
            violation += max(0.0, h(decoded))
        # 3. 调用自适应惩罚系数函数（与其他算法复用）
        adaptive_coeff = penalty_fun(gen, self.penalty_coeff, self.max_gen)
        # 4. 根据目标方向计算惩罚后适应度
        if self.maximize:
            penalized = raw_val - adaptive_coeff * violation  # 最大化：违反约束则适应度降低
        else:
            penalized = raw_val + adaptive_coeff * violation  # 最小化：违反约束则适应度升高
        return penalized, raw_val, violation

    def init_whale(self, gen: int = 0) -> Whale:
        """初始化鲸鱼个体（新增约束属性计算）"""
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
        whale = Whale(np.array(chrom, dtype=float))
        # 计算初始个体的约束相关属性（gen=0表示初始代）
        decoded = decode(whale.chrom, self.var_types)
        whale.fitness, whale.raw_fitness, whale.violation = self._penalized_fitness(decoded, gen)
        return whale

    def bound_position(self, chrom: np.ndarray) -> np.ndarray:
        """将位置约束在变量范围内（处理越界，保持原逻辑）"""
        bounded = chrom.copy()
        for i in range(self.dim):
            vtype, low, high = self.var_ranges[i]
            if bounded[i] < low:
                bounded[i] = low
            elif bounded[i] > high:
                bounded[i] = high
            # 对整数/二进制变量进行类型转换
            if vtype == "integer":
                bounded[i] = round(bounded[i])
            elif vtype == "binary":
                bounded[i] = 1 if bounded[i] >= 0.5 else 0
        return bounded

    def update_position(self, whale: Whale, best_whale: Whale, a: float, gen: int) -> Whale:
        """更新鲸鱼位置（WOA核心操作，新增约束属性计算）"""
        r1 = random.random()  # [0,1]随机数
        r2 = random.random()  # [0,1]随机数
        A = 2 * a * r1 - a  # 系数A（随a线性下降）
        C = 2 * r2  # 系数C

        p = random.random()  # 概率阈值（决定行为模式）
        l = random.uniform(-1, 1)  # 螺旋参数

        if p < 0.5:
            # 情况1：包围猎物（|A|<1）或搜索猎物（|A|≥1）
            if abs(A) < 1:
                # 包围猎物：向最优个体移动
                D = abs(C * best_whale.chrom - whale.chrom)
                new_chrom = best_whale.chrom - A * D
            else:
                # 搜索猎物：随机选择一个个体作为目标
                rand_whale = random.choice(self.population)
                D = abs(C * rand_whale.chrom - whale.chrom)
                new_chrom = rand_whale.chrom - A * D
        else:
            # 情况2：螺旋更新（模拟鲸鱼螺旋状包围）
            D = abs(best_whale.chrom - whale.chrom)
            new_chrom = D * np.exp(self.b * l) * np.cos(2 * np.pi * l) + best_whale.chrom

        # 约束位置并计算新个体的约束属性
        bounded_chrom = self.bound_position(new_chrom)
        new_whale = Whale(bounded_chrom)
        decoded = decode(new_whale.chrom, self.var_types)
        new_whale.fitness, new_whale.raw_fitness, new_whale.violation = self._penalized_fitness(decoded, gen)
        return new_whale

    def _record_fitness(self):
        """记录当前代的统计信息（新增原始目标值、约束违反量）"""
        fitness_values = [w.fitness for w in self.population]
        raw_values = [w.raw_fitness for w in self.population]
        violation_values = [w.violation for w in self.population]

        self.best_fitness_history.append(max(fitness_values) if self.maximize else min(fitness_values))
        self.best_raw_history.append(max(raw_values) if self.maximize else min(raw_values))
        self.avg_fitness_history.append(np.mean(fitness_values))
        self.avg_violation_history.append(np.mean(violation_values))

    def _record_positions(self, gen: int):
        """记录可视化用的种群位置（与其他算法对齐）"""
        positions = []
        for whale in self.population:
            decoded = decode(whale.chrom, self.var_types)
            real_pos = []
            for key in decoded:
                if key.startswith("real_"):
                    real_pos.extend(decoded[key].tolist())
            positions.append(real_pos)
        self.position_history.append({
            "gen": gen,
            "positions": np.array(positions)
        })

    def run(self) -> Whale:
        """运行带约束的鲸鱼优化算法"""
        # 初始化种群（gen=0表示初始代）
        self.population = [self.init_whale(gen=0) for _ in range(self.pop_size)]
        # 初始化全局最优（基于惩罚后适应度）
        best_whale = max(self.population, key=lambda x: x.fitness) if self.maximize else min(self.population,
                                                                                             key=lambda x: x.fitness)

        # 计算可视化代数间隔
        interval = max(1, self.max_gen // (self.visualize_gens - 1))
        # 记录初始状态
        self._record_fitness()
        self._record_positions(gen=0)

        # 迭代优化
        for gen in range(1, self.max_gen + 1):
            # 计算当前a值（线性下降）
            a = self.a_decrease - (self.a_decrease / self.max_gen) * gen

            # 更新每个鲸鱼的位置
            for i in range(self.pop_size):
                new_whale = self.update_position(self.population[i], best_whale, a, gen)
                self.population[i] = new_whale

            # 更新全局最优
            current_best = max(self.population, key=lambda x: x.fitness) if self.maximize else min(self.population,
                                                                                                   key=lambda
                                                                                                       x: x.fitness)
            if (self.maximize and current_best.fitness > best_whale.fitness) or (
                    not self.maximize and current_best.fitness < best_whale.fitness):
                best_whale = current_best

            # 记录当前代信息
            self._record_fitness()
            if (gen % interval == 0) or (gen == self.max_gen):
                self._record_positions(gen=gen)

            # 打印进度（与其他算法格式对齐）
            if (gen) % 10 == 0:
                print(f"第{gen}/{self.max_gen}代 | "
                      f"最优惩罚适应度: {self.best_fitness_history[-1]:.6f} | "
                      f"平均适应度: {self.avg_fitness_history[-1]:.6f} | "
                      f"平均违反量: {self.avg_violation_history[-1]:.6f}")

        # 裁剪可视化记录（避免过量）
        if len(self.position_history) > self.visualize_gens:
            self.position_history = self.position_history[:self.visualize_gens]

        # 运行结束后可视化
        self.visualize()
        return best_whale

    def repair_solution(self, decoded: dict, max_time: float = 1.0, step: float = 0.01) -> dict:
        """修复违反约束的解（与GA/PSO/SA接口完全一致）"""
        return repair_solution(self, decoded, max_time, step)

    def is_decoded_feasible(self, decoded, tol=1e-6) -> bool:
        """检查解是否可行（与GA/PSO/SA接口完全一致）"""
        return is_decoded_feasible(self, decoded, tol)

    def visualize(self):
        """核心可视化：适应度+约束违反量+变量位置演化（无额外图表）"""
        # 1. 适应度 + 约束违反量 双子图
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
        ax1.set_title('WOA适应度变化曲线')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # 子图2：约束违反量曲线（有约束时）/ 原始目标值（无约束时）
        if self.eq_constraints or self.ineq_constraints:
            ax2.plot(range(len(self.avg_violation_history)), self.avg_violation_history, c='purple', linewidth=2,
                     label='平均约束违反量')
            ax2.axhline(y=0, c='black', linestyle='--', alpha=0.5, label='约束满足线（违反量=0）')
            ax2.set_xlabel('迭代次数')
            ax2.set_ylabel('平均约束违反量')
            ax2.set_title('WOA约束违反量变化曲线')
        else:
            ax2.plot(range(len(self.best_raw_history)), self.best_raw_history, c='green', linewidth=2,
                     label='最优原始目标值')
            ax2.set_xlabel('迭代次数')
            ax2.set_ylabel('原始目标值')
            ax2.set_title('WOA原始目标值变化曲线')
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()
        plt.show()

        # 2. 变量位置演化可视化（仅实数变量，辅助观察）
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

                    # 关键修复：使用contour+allsegs替代contourf+collections
                    contour = ax.contour(xx, yy, constraint_vals, levels=[0], alpha=0)

                    # 遍历所有线段并设置样式（兼容新旧版本Matplotlib）
                    for seg in contour.allsegs[0]:  # allsegs[0]获取level=0的所有线段
                        ax.plot(seg[:, 0], seg[:, 1], color=f'C{i}', linewidth=2, linestyle='--')

                    # 手动添加图例（解决contour无label问题）
                    ax.plot([], [], color=f'C{i}', linewidth=2, linestyle='--', label=f'约束 {i + 1}')

            # 颜色条与图表设置
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('迭代进程（颜色越深越接近最优代）')
            ax.set_xlabel('变量1')
            ax.set_ylabel('变量2')
            ax.set_title('WOA种群位置演化（2D实数变量）')
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.show()

        # 2.2 高维实数变量：PCA降维可视化
        elif real_dim > 2:
            # PCA降维到2维
            pca = PCA(n_components=2)
            positions_2d = pca.fit_transform(all_positions)

            fig, ax = plt.subplots(figsize=(10, 6))
            gen_indices = []
            for i, data in enumerate(self.position_history):
                gen_indices.extend([i] * self.pop_size)
            colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))

            # 绘制降维后位置
            scatter = ax.scatter(positions_2d[:, 0], positions_2d[:, 1], c=colors, alpha=0.6, s=50)

            # 标记全局最优（降维后位置）
            best_idx = np.argmax([w.fitness for w in self.population]) if self.maximize else np.argmin(
                [w.fitness for w in self.population])
            best_pos = self.position_history[-1]["positions"][best_idx]
            best_pos_2d = pca.transform([best_pos])[0]
            ax.scatter(best_pos_2d[0], best_pos_2d[1], c='red', s=150, marker='*', label='全局最优')

            # 图表设置
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('迭代进程（颜色越深越接近最优代）')
            ax.set_xlabel(f'主成分1（解释方差：{pca.explained_variance_ratio_[0]:.2%}）')
            ax.set_ylabel(f'主成分2（解释方差：{pca.explained_variance_ratio_[1]:.2%}）')
            ax.set_title('WOA种群位置演化（PCA降维至2D）')
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.tight_layout()
            plt.show()

    # ================= 使用示例（main函数）=================
if __name__ == "__main__":
    # 1. 初始化工具与随机种子（确保实验可复现）
    fix_random_seed(42)  # 固定随机种子
    init_mlp()  # 复用utils中的初始化函数

    # 2. 定义优化变量（2个实数变量，范围[-5.12, 5.12]，经典Rastrigin函数定义域）
    var_types = [("real", (2, -5.12, 5.12))]  # 类型：(变量类型, (变量数, 下界, 上界))

    # 3. 定义目标函数（Rastrigin函数，转为最大化问题）
    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]  # 解析实数变量（real_0对应第一个实数变量组）
        # Rastrigin函数（最小值0，此处取负转为最大化，最大值0）
        return -(x ** 2 - 10 * np.cos(2 * np.pi * x) + y ** 2 - 10 * np.cos(2 * np.pi * y) + 20)

    # 4. 定义约束条件（3个不等式约束，模拟实际优化场景）
    # 约束1：x + y ≤ 2
    def ineq_constraint1(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return x + y - 2  # 约束满足条件：返回值 ≤ 0

    # 约束2：x - y ≥ -3 → y - x ≤ 3 → 转换为返回值 ≤ 0
    def ineq_constraint2(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return y - x - 3  # 约束满足条件：返回值 ≤ 0

    # 约束3：x² + y² ≥ 1 → 1 - x² - y² ≤ 0 → 转换为返回值 ≤ 0
    def ineq_constraint3(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return 1 - (x ** 2 + y ** 2)  # 约束满足条件：返回值 ≤ 0

    # 5. 初始化WOA算法实例
    woa_optimizer = WOA(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=30,  # 种群规模
        max_gen=100,  # 最大迭代次数
        a_decrease=2.0,  # 系数a初始值（线性下降到0）
        b=1.0,  # 螺旋形状参数
        maximize=True,  # 目标方向：最大化（因目标函数取负）
        eq_constraints=[],  # 无等式约束
        ineq_constraints=[ineq_constraint1, ineq_constraint2, ineq_constraint3],  # 3个不等式约束
        penalty_coeff=1e3,  # 基础惩罚系数
        visualize_gens=5  # 记录5个关键代用于位置演化可视化
    )

    # 6. 运行优化算法
    print("=== 鲸鱼优化算法（WOA）开始运行 ===")
    best_solution = woa_optimizer.run()
    print("=== 鲸鱼优化算法（WOA）运行结束 ===")

    # 7. 解析并输出最优结果
    best_decoded = decode(best_solution.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]  # 提取最优变量值

    print("\n========== 最优结果详情 ==========")
    print(f"1. 最优变量值：")
    print(f"   x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"2. 优化目标相关：")
    print(f"   原始目标值（Rastrigin函数值）：{-best_solution.raw_fitness:.6f}")  # 还原为原函数值（因之前取负）
    print(f"   惩罚后适应度：{best_solution.fitness:.6f}")
    if woa_optimizer.ineq_constraints is None and woa_optimizer.eq_constraints is None:
        print(f"3. 约束满足情况：")
        print(f"   约束违反量：{best_solution.violation:.6f}")
        print(f"   是否为可行解：{'是' if best_solution.violation <= 1e-6 else '否'}")

        if best_solution.violation > 1e-6:
            print("\n========== 修复不可行解 ==========")
            # 调用修复函数
            repaired_decoded = woa_optimizer.repair_solution(best_decoded, max_time=1.0, step=0.01)
            x_rep, y_rep = repaired_decoded["real_0"]
            # 计算修复后的值
            repaired_raw = evaluate(repaired_decoded)
            repaired_violation = 0.0
            # 重新计算修复后的约束违反量
            for h in woa_optimizer.ineq_constraints:
                repaired_violation += max(0.0, h(repaired_decoded))

            print(f"修复后变量值：x = {x_rep:.6f}, y = {y_rep:.6f}")
            print(f"修复后原始目标值（Rastrigin函数值）：{-repaired_raw:.6f}")
            print(f"修复后约束违反量：{repaired_violation:.6f}")
            print(f"修复后是否为可行解：{'是' if repaired_violation <= 1e-6 else '否'}")


