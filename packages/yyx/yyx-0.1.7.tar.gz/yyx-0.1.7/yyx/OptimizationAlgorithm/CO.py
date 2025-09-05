import numpy as np
import matplotlib.pyplot as plt
import random
from typing import List, Tuple, Callable
from sklearn.decomposition import PCA
from utils import decode, init_mlp, fix_random_seed, repair_solution, is_decoded_feasible, penalty_fun

plt.rcParams["font.family"] = ["SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


# ================= 猎豹个体类（增强约束属性）=================
class Cheetah:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（位置向量）
        self.fitness = None  # 惩罚后适应度（算法选择依据）
        self.raw_fitness = None  # 原始目标值（真实优化目标）
        self.violation = 0.0  # 约束违反量（评估解的可行性）
        self.speed = 0.0  # 移动速度（影响行为步长）
        self.stamina = 0.0  # 耐力（控制行为模式切换）

    def __str__(self) -> str:
        if self.fitness is None:
            return "fitness=None"
        return (f"raw={self.raw_fitness:.6f}, fitness={self.fitness:.6f}, "
                f"violation={self.violation:.6f}, speed={self.speed:.6f}, stamina={self.stamina:.6f}")


# ================= 带可选约束的猎豹优化算法（CO）类 =================
class CO:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标评估函数（返回原始目标值）
            pop_size: int = 30,
            max_gen: int = 100,
            speed_init: float = 1.0,  # 初始速度（控制探索步长）
            speed_decay: float = 0.97,  # 速度衰减系数（后期减少扰动）
            stamina_init: float = 1.0,  # 初始耐力（行为模式切换阈值）
            stamina_recovery: float = 0.05,  # 耐力恢复系数（每代恢复量）
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
        self.speed_init = speed_init
        self.speed_decay = speed_decay
        self.stamina_init = stamina_init
        self.stamina_recovery = stamina_recovery

        # 约束与目标扩展（核心：通过has_constraints动态适配逻辑）
        self.maximize = maximize
        self.eq_constraints = eq_constraints or []
        self.ineq_constraints = ineq_constraints or []
        self.has_constraints = len(self.eq_constraints) > 0 or len(self.ineq_constraints) > 0
        self.penalty_coeff = penalty_coeff
        self.visualize_gens = visualize_gens

        # 解析变量范围（位置约束+类型转换）
        self.var_ranges = []  # 每个变量的（类型, 下界, 上界）
        self.dim = 0  # 总变量维度
        self.low = []  # 所有变量下界（数组形式，快速计算）
        self.high = []  # 所有变量上界（数组形式）
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
        self.avg_violation_history = []  # 每代平均约束违反量（仅带约束时记录）
        self.position_history = []  # 种群位置记录（用于演化可视化）

    def _penalized_fitness(self, decoded: dict, gen: int) -> Tuple[float, float, float]:
        """计算惩罚后适应度、原始目标值、约束违反量（无约束时违反量=0）"""
        # 1. 计算原始目标值（不依赖约束）
        raw_val = self.evaluate(decoded)

        # 2. 计算约束违反量（无约束时直接返回0，减少冗余计算）
        violation = 0.0
        if self.has_constraints:
            # 等式约束：允许1e-6数值误差（工程上的容忍范围）
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

    def _init_cheetah(self, gen: int = 0) -> Cheetah:
        """初始化猎豹个体（含约束属性，确保速度、耐力、适应度均有值）"""
        chrom = []
        for vtype, info in self.var_types:
            if vtype == "binary":
                # 二进制变量：0/1随机生成
                chrom.extend(np.random.randint(0, 2, size=info))
            elif vtype == "integer":
                # 整数变量：[low, high]范围内随机整数
                n, low, high = info
                chrom.extend(np.random.randint(low, high + 1, size=n))
            elif vtype == "real":
                # 实数变量：[low, high]范围内均匀分布随机数
                n, low, high = info
                chrom.extend(np.random.uniform(low, high, size=n))

        # 生成个体并初始化核心属性
        cheetah = Cheetah(np.array(chrom, dtype=float))
        # 速度：初始速度×[0.8,1.2]随机因子（增加种群多样性）
        cheetah.speed = self.speed_init * np.random.uniform(0.8, 1.2)
        # 耐力：初始值（所有个体统一，后续随行为变化）
        cheetah.stamina = self.stamina_init
        # 计算适应度与约束属性
        decoded = decode(cheetah.chrom, self.var_types)
        cheetah.fitness, cheetah.raw_fitness, cheetah.violation = self._penalized_fitness(decoded, gen)
        return cheetah

    def _bound_position(self, chrom: np.ndarray) -> np.ndarray:
        """位置边界处理+类型转换（确保变量合法）"""
        bounded = chrom.copy()
        for i in range(self.dim):
            vtype, low, high = self.var_ranges[i]
            # 1. 范围约束：越界值拉回[low, high]
            if bounded[i] < low:
                bounded[i] = low
            elif bounded[i] > high:
                bounded[i] = high
            # 2. 类型转换：确保整数/二进制变量类型正确
            if vtype == "integer":
                bounded[i] = round(bounded[i])
            elif vtype == "binary":
                bounded[i] = 1 if bounded[i] >= 0.5 else 0
        return bounded

    def _stalk_behavior(self, cheetah: Cheetah, prey_pos: np.ndarray) -> np.ndarray:
        """潜伏行为：小步长靠近最优解（局部开发，适合高适应度个体）"""
        # 方向：指向当前最优解（猎物位置）
        direction = prey_pos - cheetah.chrom
        # 移动步长：小系数×速度×耐力（控制缓慢靠近）
        move = 0.1 * cheetah.speed * cheetah.stamina * direction
        # 小范围噪声：增加局部探索多样性（基于变量范围的正态分布噪声）
        noise = 0.03 * (self.high - self.low) * np.random.randn(self.dim)
        return cheetah.chrom + move + noise

    def _chase_behavior(self, cheetah: Cheetah, prey_pos: np.ndarray) -> np.ndarray:
        """追捕行为：大步长冲向最优解（全局收敛，适合中等适应度个体）"""
        direction = prey_pos - cheetah.chrom
        # 移动步长：速度×耐力（快速接近），附加小方向扰动
        move = cheetah.speed * cheetah.stamina * direction
        dir_noise = (np.random.rand(self.dim) - 0.5) * 2 * 0.08  # [-0.08, 0.08]方向扰动
        return cheetah.chrom + move * (1 + dir_noise)

    def _ambush_behavior(self, cheetah: Cheetah) -> np.ndarray:
        """突袭行为：大范围随机搜索（全局探索，适合低适应度/低耐力个体）"""
        # 随机跳跃：基于速度和变量范围，避免陷入局部最优
        jump = cheetah.speed * (np.random.rand(self.dim) - 0.5) * (self.high - self.low)
        return cheetah.chrom + jump

    def _record_fitness(self, population: List[Cheetah]):
        """记录每代核心指标（根据有无约束动态调整）"""
        fitness_values = [c.fitness for c in population]
        raw_values = [c.raw_fitness for c in population]

        # 记录最优和平均适应度（适配目标方向）
        self.best_fitness_history.append(max(fitness_values) if self.maximize else min(fitness_values))
        self.best_raw_history.append(max(raw_values) if self.maximize else min(raw_values))
        self.avg_fitness_history.append(np.mean(fitness_values))

        # 仅带约束时记录平均违反量（无约束时无需记录）
        if self.has_constraints:
            violation_values = [c.violation for c in population]
            self.avg_violation_history.append(np.mean(violation_values))

    def _record_positions(self, population: List[Cheetah], gen: int):
        """记录种群位置（仅提取实数变量，二进制/整数可视化意义有限）"""
        positions = []
        for cheetah in population:
            decoded = decode(cheetah.chrom, self.var_types)
            real_pos = []
            # 仅保留实数变量（key以"real_"开头）
            for key in decoded:
                if key.startswith("real_"):
                    real_pos.extend(decoded[key].tolist())
            positions.append(real_pos)
        self.position_history.append({"gen": gen, "positions": np.array(positions)})

    def run(self) -> Cheetah:
        """运行带可选约束的猎豹优化算法（完整实现）"""
        # 1. 初始化种群（类实例属性，后续统一通过self访问）
        self.population = [self._init_cheetah(gen=0) for _ in range(self.pop_size)]

        # 2. 初始状态记录（适应度+位置）
        self._record_fitness(self.population)
        # 计算位置记录间隔（避免冗余数据，确保至少记录1代）
        interval = max(1, self.max_gen // (self.visualize_gens - 1))
        self._record_positions(self.population, gen=0)

        # 3. 迭代优化（核心循环：行为选择→位置更新→贪婪选择）
        for gen in range(1, self.max_gen + 1):
            # 3.1 确定当前最优个体（猎物位置，基于惩罚后适应度）
            if self.maximize:
                best_cheetah = max(self.population, key=lambda x: x.fitness)
            else:
                best_cheetah = min(self.population, key=lambda x: x.fitness)
            prey_pos = best_cheetah.chrom.copy()

            # 3.2 逐个体更新行为与位置
            new_population = []
            for cheetah in self.population:
                # 耐力恢复：每代恢复少量耐力，不超过最大值1.0（避免耐力无限累积）
                cheetah.stamina = min(1.0, cheetah.stamina + self.stamina_recovery)

                # 行为模式选择（基于当前个体与最优个体的适应度差距+耐力）
                # 处理适应度为0的边界情况，避免除零错误
                if best_cheetah.fitness == 0:
                    fitness_ratio = 0.0
                else:
                    fitness_ratio = cheetah.fitness / best_cheetah.fitness

                # 根据适应度比例和耐力选择行为
                if fitness_ratio > 0.8 and cheetah.stamina > 0.7:
                    # 高适应度+高耐力 → 潜伏（局部开发，精细搜索）
                    new_chrom = self._stalk_behavior(cheetah, prey_pos)
                elif fitness_ratio > 0.3 and cheetah.stamina > 0.3:
                    # 中等适应度+中等耐力 → 追捕（向优解聚集，快速收敛）
                    new_chrom = self._chase_behavior(cheetah, prey_pos)
                    cheetah.stamina *= 0.75  # 追捕消耗耐力
                else:
                    # 低适应度或低耐力 → 突袭（全局探索，跳出局部最优）
                    new_chrom = self._ambush_behavior(cheetah)
                    cheetah.stamina = 0.4  # 突袭后耐力重置

                # 3.3 位置处理与新个体评估
                new_chrom = self._bound_position(new_chrom)  # 确保位置合法
                new_cheetah = Cheetah(new_chrom)
                # 继承速度（并衰减），初始化耐力
                new_cheetah.speed = cheetah.speed * self.speed_decay
                new_cheetah.stamina = cheetah.stamina  # 继承当前耐力状态
                # 计算新个体的适应度与约束属性
                decoded = decode(new_cheetah.chrom, self.var_types)
                new_cheetah.fitness, new_cheetah.raw_fitness, new_cheetah.violation = self._penalized_fitness(
                    decoded, gen
                )

                # 3.4 贪婪选择：保留更优个体（基于惩罚后适应度）
                if (self.maximize and new_cheetah.fitness > cheetah.fitness) or \
                        (not self.maximize and new_cheetah.fitness < cheetah.fitness):
                    new_population.append(new_cheetah)
                else:
                    new_population.append(cheetah)

            # 3.5 更新种群（新一代替换旧一代）
            self.population = new_population

            # 3.6 记录当前代信息（适应度+位置）
            self._record_fitness(self.population)
            # 按间隔记录位置（最后一代强制记录，确保演化过程完整）
            if (gen % interval == 0) or (gen == self.max_gen):
                self._record_positions(self.population, gen=gen)

            # 3.7 打印迭代进度（根据有无约束动态调整输出内容）
            if gen % 10 == 0:
                progress_str = (f"第{gen}/{self.max_gen}代 | "
                                f"最优适应度: {self.best_fitness_history[-1]:.6f} | "
                                f"平均适应度: {self.avg_fitness_history[-1]:.6f}")
                # 仅带约束时显示平均违反量，无约束时屏蔽
                if self.has_constraints:
                    progress_str += f" | 平均违反量: {self.avg_violation_history[-1]:.6f}"
                print(progress_str)

        # 4. 裁剪位置记录（避免超出设定的可视化代数，减少内存占用）
        if len(self.position_history) > self.visualize_gens:
            self.position_history = self.position_history[:self.visualize_gens]

        # 5. 算法结束后自动绘制可视化图表（动态适配有无约束）
        self.visualize()

        # 6. 返回全局最优个体（根据目标方向选择）
        if self.maximize:
            return max(self.population, key=lambda x: x.fitness)
        else:
            return min(self.population, key=lambda x: x.fitness)

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
            ax1.set_title('猎豹优化算法适应度变化曲线（带约束）')
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            # 子图2：约束违反量曲线（仅带约束时显示）
            ax2.plot(range(len(self.avg_violation_history)), self.avg_violation_history,
                     c='purple', linewidth=2, label='平均约束违反量')
            ax2.axhline(y=0, c='black', linestyle='--', alpha=0.5, label='约束满足线（违反量=0）')
            ax2.set_xlabel('迭代次数')
            ax2.set_ylabel('平均约束违反量')
            ax2.set_title('猎豹优化算法约束违反量变化曲线')
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
            plt.title('猎豹优化算法适应度变化曲线（无约束）')
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
            best_idx = np.argmax([c.fitness for c in self.population]) if self.maximize else np.argmin(
                [c.fitness for c in self.population])
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
                    grid_decoded = {"real_0": (xx, yy)}  # 网格点解码为CO可识别格式
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
            ax.set_title('猎豹优化算法种群位置演化（2D实数变量）', fontsize=14)
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
            best_idx = np.argmax([c.fitness for c in self.population]) if self.maximize else np.argmin(
                [c.fitness for c in self.population])
            best_pos_high_dim = self.position_history[-1]["positions"][best_idx]  # 最后一代最优个体的高维位置
            best_pos_2d = pca.transform([best_pos_high_dim])[0]  # 最优位置降维到2D
            ax.scatter(best_pos_2d[0], best_pos_2d[1], c='red', s=150, marker='*',
                       edgecolors='darkred', linewidth=2, label='全局最优解')

            # 图表补充设置（显示方差解释率，说明降维有效性）
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('迭代进程（颜色越深越接近最优代）', fontsize=10)
            ax.set_xlabel(f'主成分1（解释方差：{pca.explained_variance_ratio_[0]:.2%}）', fontsize=12)
            ax.set_ylabel(f'主成分2（解释方差：{pca.explained_variance_ratio_[1]:.2%}）', fontsize=12)
            ax.set_title(f'猎豹优化算法种群位置演化（PCA降维至2D，原始维度{real_dim}）', fontsize=14)
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


if __name__ == "__main__":
    # 1. 初始化工具（固定随机种子+中文显示，确保结果可复现）
    fix_random_seed(42)  # 固定种子：保证每次运行结果一致
    init_mlp()  # 初始化中文显示（解决matplotlib中文乱码）

    # 2. 变量定义（2个实数变量，适配Rosenbrock函数常用定义域）
    # 格式：[("变量类型", (数量, 下界, 上界))]，此处x,y ∈ [-2, 2]
    var_types = [("real", (2, -2.0, 2.0))]


    # 3. 目标函数（Rosenbrock函数，求最小值→转为最大化问题）
    # 原始函数：f(x,y)=(1-x)² + 100(y-x²)²，理论最小值0（在x=1,y=1处）
    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]  # 从解码结果提取变量
        raw_target = (1 - x) ** 2 + 100 * (y - x ** 2) ** 2  # 原始目标值（越小越好）
        return -raw_target  # 转为最大化问题：适应度 = -原始值（越大越好）


    # 4. 约束条件控制（通过use_constraints切换模式）
    use_constraints = True  # True=带约束测试；False=无约束测试
    eq_constraints = []  # 等式约束（本次测试暂不使用）
    ineq_constraints = []  # 不等式约束（带约束时添加）

    if use_constraints:
        # 约束1：x + y ≤ 0 → 违反量 = x + y（>0时违反）
        def ineq1(decoded: dict) -> float:
            x, y = decoded["real_0"]
            return x + y  # 约束满足条件：返回值 ≤ 0


        # 约束2：x² + y² ≤ 0.5 → 违反量 = x² + y² - 0.5（>0时违反）
        def ineq2(decoded: dict) -> float:
            x, y = decoded["real_0"]
            return x ** 2 + y ** 2 - 0.5  # 约束满足条件：返回值 ≤ 0


        # 约束3：y ≥ x + 0.3 → 变形为 x - y + 0.3 ≤ 0（违反量 = x - y + 0.3）
        def ineq3(decoded: dict) -> float:
            x, y = decoded["real_0"]
            return x - y + 0.3  # 约束满足条件：返回值 ≤ 0


        ineq_constraints = [ineq1, ineq2, ineq3]  # 加入约束列表

    # 5. 初始化猎豹优化算法（CO）实例
    co_optimizer = CO(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=30,  # 种群规模（30-50较优，平衡效率与多样性）
        max_gen=150,  # 最大迭代次数（150代足够收敛）
        speed_init=0.7,  # 初始速度（控制探索步长，0.6-0.8较优）
        speed_decay=0.96,  # 速度衰减系数（后期减小步长，强化局部搜索）
        stamina_init=1.0,  # 初始耐力（行为模式切换的基础值）
        stamina_recovery=0.04,  # 耐力恢复系数（每代恢复量，避免过快耗尽）
        maximize=True,  # 目标方向：最大化适应度（因目标函数已取负）
        eq_constraints=eq_constraints,
        ineq_constraints=ineq_constraints,
        penalty_coeff=1e3,  # 基础惩罚系数（平衡目标优化与约束满足）
        visualize_gens=6  # 记录6个关键代用于位置演化可视化
    )

    # 6. 运行CO算法（打印运行状态）
    print(f"=== 猎豹优化算法（CO）开始运行 {'(带约束)' if use_constraints else '(无约束)'} ===")
    best_cheetah = co_optimizer.run()  # 执行优化，返回全局最优个体
    print(f"=== 猎豹优化算法（CO）运行结束 {'(带约束)' if use_constraints else '(无约束)'} ===")

    # 7. 解析最优结果（从染色体解码为实际变量值）
    best_decoded = decode(best_cheetah.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]  # 提取2个实数变量的最优值
    min_raw_target = -best_cheetah.raw_fitness  # 还原为原始函数的最小值

    # 8. 输出最优结果详情（根据有无约束动态调整内容）
    print("\n========== 最优结果详情 ==========")
    print(f"1. 最优变量值：")
    print(f"   x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"2. 目标函数结果：")
    print(f"   原始Rosenbrock函数值（最小值）：{min_raw_target:.6f}")  # 理论最小值0
    print(f"   算法适应度值：{best_cheetah.fitness:.6f}")

    # 仅在有约束时，输出约束满足情况和修复逻辑
    if use_constraints:
        print(f"3. 约束满足情况：")
        print(f"   总约束违反量：{best_cheetah.violation:.6f}")  # 0表示完全满足
        is_feasible = best_cheetah.violation <= 1e-6  # 数值容忍：1e-6以内视为可行
        print(f"   是否为可行解：{'是' if is_feasible else '否'}")

        # 若最优解不可行，调用修复函数优化，并输出修复结果
        if not is_feasible:
            print("\n========== 修复不可行解 ==========")
            # 修复参数：最大修复时间1.5秒，步长0.005（精细调整）
            repaired_decoded = co_optimizer.repair_solution(best_decoded, max_time=1.5, step=0.005)
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


    # 9. 无约束场景的补充说明（帮助理解结果与理论最优的差异）
    else:
        print(f"\n========== 无约束场景说明 ==========")
        print(f"Rosenbrock函数理论最优解：x=1.0, y=1.0（函数值0）")
        print(f"当前最优解与理论值的偏差：")
        print(f"   Δx = {abs(x_opt - 1.0):.6f}, Δy = {abs(y_opt - 1.0):.6f}")
        print(f"   函数值偏差：{abs(min_raw_target - 0.0):.6f}")
