import random
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from typing import List, Tuple, Callable
from utils import decode, init_mlp, fix_random_seed, repair_solution, is_decoded_feasible, penalty_fun  # 补充导入约束工具


# ================= 粒子类（增强约束相关属性） =================
class Particle:
    """粒子类（适配单目标+约束优化）"""
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 粒子位置（染色体）
        self.fitness = None      # 惩罚后适应度
        self.raw_fitness = None  # 原始目标值
        self.violation = 0.0     # 约束违反量
        self.pbest_chrom = None  # 个体最优位置
        self.pbest_fitness = None  # 个体最优适应度（惩罚后）
        self.pbest_raw = None     # 个体最优原始目标值
        self.pbest_violation = 0.0  # 个体最优约束违反量

    def __str__(self, maximize: bool = False) -> str:
        if self.fitness is None:
            return "fitness=None"
        return (f"raw={self.raw_fitness:.6f}, fitness={self.fitness:.6f}, "
                f"violation={self.violation:.6f}")


# ================= 带约束的粒子群算法（PSO）类 =================
class PSO:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],
            pop_size: int = 50,
            max_gen: int = 100,
            w: float = 0.8,
            c1: float = 2.0,
            c2: float = 2.0,
            mutation_prob: float = 0.05,
            visualize_gens: int = 5,  # 要可视化的代数
            maximize: bool = False,  # 目标方向（默认最小化，与GA对齐）
            eq_constraints: List[Callable[[dict], float]] = None,  # 等式约束
            ineq_constraints: List[Callable[[dict], float]] = None,  # 不等式约束
            penalty_coeff: float = 1e3  # 惩罚系数（与GA对齐）
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.mutation_prob = mutation_prob
        self.visualize_gens = visualize_gens

        # 约束相关参数（完全对齐GA版本）
        self.maximize = maximize
        self.eq_constraints = eq_constraints or []
        self.ineq_constraints = ineq_constraints or []
        self.penalty_coeff = penalty_coeff

        # 计算染色体长度
        self.chrom_length = 0
        for vtype, info in var_types:
            if vtype == "binary":
                self.chrom_length += info
            else:
                self.chrom_length += info[0]

        # 粒子群核心变量
        self.particles = []
        self.velocities = []
        self.gbest_chrom = None
        self.gbest_fitness = None  # 全局最优惩罚后适应度
        self.gbest_raw = None      # 全局最优原始目标值
        self.gbest_violation = 0.0  # 全局最优约束违反量

        # 变量边界
        self.lb, self.ub = self._get_bounds()
        self.vmax = 0.1 * (self.ub - self.lb)
        self.vmin = -self.vmax

        # 历史记录（新增约束违反量记录，对齐GA）
        self.position_history = []  # 粒子位置历史（可视化用）
        self.best_fitness_history = []  # 每代最优惩罚适应度
        self.avg_fitness_history = []   # 每代平均惩罚适应度
        self.avg_violation_history = [] # 每代平均约束违反量

    def _get_bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        """计算变量边界（与原逻辑一致）"""
        lb = []
        ub = []
        for vtype, info in self.var_types:
            if vtype == "binary":
                n = info
                lb.extend([0] * n)
                ub.extend([1] * n)
            elif vtype == "integer":
                n, low, high = info
                lb.extend([low] * n)
                ub.extend([high] * n)
            elif vtype == "real":
                n, low, high = info
                lb.extend([low] * n)
                ub.extend([high] * n)
        return np.array(lb), np.array(ub)

    def _penalized_fitness(self, decoded: dict, gen: int) -> Tuple[float, float, float]:
        """计算惩罚后适应度、原始目标值、约束违反量（完全对齐GA）"""
        # 1. 计算原始目标值
        raw_val = self.evaluate(decoded)
        # 2. 计算约束违反量
        violation = 0.0
        # 等式约束：|g(x)|（允许1e-6误差）
        for g in self.eq_constraints:
            violation += max(0.0, abs(g(decoded)) - 1e-6)
        # 不等式约束：h(x) > 0 的部分
        for h in self.ineq_constraints:
            violation += max(0.0, h(decoded))
        # 3. 调用外部自适应惩罚函数（与GA复用同一逻辑）
        adaptive_coeff = penalty_fun(gen, self.penalty_coeff, self.max_gen)
        # 4. 计算惩罚后适应度（根据目标方向调整）
        if self.maximize:
            penalized = raw_val - adaptive_coeff * violation  # 最大化：惩罚项递减
        else:
            penalized = raw_val + adaptive_coeff * violation  # 最小化：惩罚项递增
        # 调试输出（每10代打印一次，与GA一致）
        if gen % 10 == 0:
            print(f"调试: raw_val={raw_val:.4f}, violation={violation:.4f}, "
                  f"coeff={adaptive_coeff:.4f}, 惩罚项={adaptive_coeff * violation:.4f}")
        return penalized, raw_val, violation

    def init_particles(self):
        """初始化粒子群（新增约束属性初始化）"""
        self.particles = [self._init_particle(gen=0) for _ in range(self.pop_size)]
        self.velocities = [
            np.random.uniform(self.vmin, self.vmax, size=self.chrom_length)
            for _ in range(self.pop_size)
        ]
        # 初始化个体最优和全局最优（基于惩罚后适应度）
        self._update_pbest()
        self._update_gbest()
        # 记录初始代的历史数据
        self._record_history()

    def _init_particle(self, gen: int) -> Particle:
        """初始化单个粒子（新增约束属性计算）"""
        # 1. 生成随机染色体（与原逻辑一致）
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
        particle = Particle(np.array(chrom, dtype=float))
        # 2. 解码并计算约束相关属性（新增）
        decoded = decode(particle.chrom, self.var_types)
        particle.fitness, particle.raw_fitness, particle.violation = self._penalized_fitness(decoded, gen)
        return particle

    def _update_pbest(self):
        """更新个体最优（基于惩罚后适应度，新增约束属性记录）"""
        for particle in self.particles:
            if particle.pbest_fitness is None:
                # 初始化个体最优
                particle.pbest_chrom = particle.chrom.copy()
                particle.pbest_fitness = particle.fitness
                particle.pbest_raw = particle.raw_fitness
                particle.pbest_violation = particle.violation
            else:
                # 按目标方向更新（最大化/最小化）
                if self.maximize:
                    if particle.fitness > particle.pbest_fitness:
                        particle.pbest_chrom = particle.chrom.copy()
                        particle.pbest_fitness = particle.fitness
                        particle.pbest_raw = particle.raw_fitness
                        particle.pbest_violation = particle.violation
                else:
                    if particle.fitness < particle.pbest_fitness:
                        particle.pbest_chrom = particle.chrom.copy()
                        particle.pbest_fitness = particle.fitness
                        particle.pbest_raw = particle.raw_fitness
                        particle.pbest_violation = particle.violation

    def _update_gbest(self):
        """更新全局最优（基于惩罚后适应度，新增约束属性记录）"""
        # 找到当前群体中最优的个体（按惩罚后适应度）
        if self.maximize:
            current_best = max(self.particles, key=lambda p: p.pbest_fitness)
        else:
            current_best = min(self.particles, key=lambda p: p.pbest_fitness)
        # 更新全局最优
        if self.gbest_fitness is None:
            self.gbest_chrom = current_best.pbest_chrom.copy()
            self.gbest_fitness = current_best.pbest_fitness
            self.gbest_raw = current_best.pbest_raw
            self.gbest_violation = current_best.pbest_violation
        else:
            if self.maximize:
                if current_best.pbest_fitness > self.gbest_fitness:
                    self.gbest_chrom = current_best.pbest_chrom.copy()
                    self.gbest_fitness = current_best.pbest_fitness
                    self.gbest_raw = current_best.pbest_raw
                    self.gbest_violation = current_best.pbest_violation
            else:
                if current_best.pbest_fitness < self.gbest_fitness:
                    self.gbest_chrom = current_best.pbest_chrom.copy()
                    self.gbest_fitness = current_best.pbest_fitness
                    self.gbest_raw = current_best.pbest_raw
                    self.gbest_violation = current_best.pbest_violation

    def _update_velocity(self, idx: int):
        """更新粒子速度（与原逻辑一致）"""
        particle = self.particles[idx]
        r1 = np.random.random(size=self.chrom_length)
        r2 = np.random.random(size=self.chrom_length)
        vel = self.w * self.velocities[idx] + \
              self.c1 * r1 * (particle.pbest_chrom - particle.chrom) + \
              self.c2 * r2 * (self.gbest_chrom - particle.chrom)
        self.velocities[idx] = np.clip(vel, self.vmin, self.vmax)

    def _update_position(self, idx: int, gen: int):
        """更新粒子位置（新增约束属性重新计算）"""
        particle = self.particles[idx]
        # 1. 计算新位置（与原逻辑一致）
        new_chrom = particle.chrom + self.velocities[idx]
        # 2. 按变量类型裁剪位置（二进制/整数/实数分别处理）
        pos = 0
        for vtype, info in self.var_types:
            if vtype == "binary":
                n = info
                new_chrom[pos:pos+n] = (new_chrom[pos:pos+n] > 0.5).astype(int)
                pos += n
            elif vtype == "integer":
                n, low, high = info
                new_chrom[pos:pos+n] = np.rint(new_chrom[pos:pos+n])
                new_chrom[pos:pos+n] = np.clip(new_chrom[pos:pos+n], low, high)
                pos += n
            elif vtype == "real":
                n, low, high = info
                new_chrom[pos:pos+n] = np.clip(new_chrom[pos:pos+n], low, high)
                pos += n
        # 3. 变异（与原逻辑一致）
        if random.random() < self.mutation_prob:
            new_chrom = self._mutate(new_chrom)
        # 4. 更新粒子位置并重新计算约束相关属性（新增）
        particle.chrom = new_chrom
        decoded = decode(particle.chrom, self.var_types)
        particle.fitness, particle.raw_fitness, particle.violation = self._penalized_fitness(decoded, gen)

    def _mutate(self, chrom: np.ndarray) -> np.ndarray:
        """粒子变异（与原逻辑一致）"""
        mutated = chrom.copy()
        pos = 0
        for vtype, info in self.var_types:
            if vtype == "binary":
                n = info
                for i in range(pos, pos+n):
                    if random.random() < 0.1:
                        mutated[i] = 1 - mutated[i]
                pos += n
            elif vtype == "integer":
                n, low, high = info
                for i in range(pos, pos+n):
                    if random.random() < 0.1:
                        delta = random.choice([-1, 1])
                        mutated[i] = np.clip(mutated[i] + delta, low, high)
                pos += n
            elif vtype == "real":
                n, low, high = info
                for i in range(pos, pos+n):
                    if random.random() < 0.1:
                        mutated[i] += np.random.normal(0, 0.1 * (high - low))
                        mutated[i] = np.clip(mutated[i], low, high)
                pos += n
        return mutated

    def _record_positions(self, gen: int):
        """记录粒子位置（可视化用，与原逻辑一致）"""
        real_positions = []
        for particle in self.particles:
            decoded = decode(particle.chrom, self.var_types)
            real_vars = []
            for key in decoded:
                if key.startswith("real_"):
                    real_vars.extend(decoded[key].tolist())
            real_positions.append(real_vars)
        self.position_history.append({
            "gen": gen,
            "positions": np.array(real_positions)
        })

    def _record_history(self):
        """记录每代的适应度和约束违反量（对齐GA的_record方法）"""
        fitness_values = [p.fitness for p in self.particles]
        violations = [p.violation for p in self.particles]
        # 记录最优惩罚适应度
        if self.maximize:
            self.best_fitness_history.append(np.max(fitness_values))
        else:
            self.best_fitness_history.append(np.min(fitness_values))
        # 记录平均惩罚适应度和平均违反量
        self.avg_fitness_history.append(np.mean(fitness_values))
        self.avg_violation_history.append(np.mean(violations))

    def repair_solution(self, decoded: dict, max_time: float = 1.0, step: float = 0.01) -> dict:
        """修复违反约束的解（完全对齐GA的接口）"""
        return repair_solution(self, decoded, max_time, step)

    def is_decoded_feasible(self, decoded, tol=1e-6) -> bool:
        """检查解是否可行（完全对齐GA的接口）"""
        return is_decoded_feasible(self, decoded, tol)

    def run(self) -> Particle:
        """算法主流程（新增约束逻辑集成，输出格式对齐GA）"""
        self.init_particles()

        # 计算可视化代数间隔（与原逻辑一致）
        interval = max(1, self.max_gen // (self.visualize_gens - 1))

        # 迭代优化
        for gen in range(1, self.max_gen + 1):
            # 更新每个粒子的速度和位置
            for i in range(self.pop_size):
                self._update_velocity(i)
                self._update_position(i, gen)  # 传入当前代数，用于计算自适应惩罚
            # 更新个体最优和全局最优
            self._update_pbest()
            self._update_gbest()
            # 记录历史数据（适应度+约束违反量）
            self._record_history()
            # 记录可视化用的粒子位置
            if (gen % interval == 0) or (gen == self.max_gen):
                self._record_positions(gen)
            # 打印迭代信息（对齐GA格式，包含约束违反量）
            print(f'第{gen}/{self.max_gen}代 | '
                  f'最优惩罚适应度: {self.best_fitness_history[-1]:.6f} | '
                  f'平均适应度: {self.avg_fitness_history[-1]:.6f} | '
                  f'平均违反量: {self.avg_violation_history[-1]:.6f}')

        # 确保可视化代数不超过设定值
        if len(self.position_history) > self.visualize_gens:
            self.position_history = self.position_history[:self.visualize_gens]

        # 运行结束后可视化（增强约束相关图表）
        self.visualize()
        # 返回全局最优粒子（与GA保持一致的返回类型）
        best_particle = Particle(self.gbest_chrom.copy())
        best_particle.fitness = self.gbest_fitness
        best_particle.raw_fitness = self.gbest_raw
        best_particle.violation = self.gbest_violation
        return best_particle

    def visualize(self):
        """可视化函数：保留原可视化逻辑，新增约束违反量曲线"""
        # 1. 绘制适应度和约束违反量曲线（对齐GA的可视化）
        plt.figure(figsize=(12, 6))
        # 子图1：适应度曲线（最优+平均）
        plt.subplot(1, 2, 1)
        plt.plot(self.best_fitness_history, c='red', label='最优惩罚适应度')
        plt.plot(self.avg_fitness_history, c='blue', linestyle='--', label='平均适应度')
        plt.xlabel('迭代次数')
        plt.ylabel('适应度值')
        plt.title('适应度变化曲线')
        plt.grid(True, alpha=0.3)
        plt.legend()
        # 子图2：约束违反量曲线（仅当有约束时显示）
        if self.eq_constraints or self.ineq_constraints:
            plt.subplot(1, 2, 2)
            plt.plot(self.avg_violation_history, c='purple', linewidth=2, label='平均违反量')
            plt.xlabel('迭代次数')
            plt.ylabel('平均约束违反量')
            plt.title('约束违反量变化曲线')
            plt.grid(True, alpha=0.3)
            plt.legend()
        plt.tight_layout()
        plt.show()

        # 2. 提取实数变量维度和位置（保留原粒子分布可视化）
        if not self.position_history:
            return
        real_dim = self.position_history[0]["positions"].shape[1]
        all_positions = np.vstack([data["positions"] for data in self.position_history])

        # 3. 根据维度绘制粒子分布（保留原逻辑）
        if real_dim == 2:
            self._visualize_particles_2d(all_positions)
            self._visualize_3d_surface()
            self._visualize_contour()
        else:
            self._visualize_particles_pca(all_positions)
            if real_dim >= 3:
                self._visualize_particles_3d(all_positions)
            else:
                self._visualize_particles_1d(all_positions)

    # 以下可视化方法保留原逻辑，仅调整最优解标记的数据源（从gbest_raw获取原始值

    def _visualize_particles_2d(self, positions: np.ndarray):
        fig, ax = plt.subplots(figsize=(10, 6))
        gen_indices = []
        for i, data in enumerate(self.position_history):
            gen_indices.extend([i] * self.pop_size)
        colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))
        scatter = ax.scatter(positions[:, 0], positions[:, 1], c=colors, alpha=0.6, s=50)
        # 标记全局最优（使用原始目标值对应的位置）
        decoded_gbest = decode(self.gbest_chrom, self.var_types)
        gbest_pos = decoded_gbest["real_0"]
        ax.scatter(gbest_pos[0], gbest_pos[1], c='red', s=150, marker='*', label='全局最优')
        # 样式设置
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('迭代代数')
        ax.set_xlabel('变量1')
        ax.set_ylabel('变量2')
        ax.set_title('粒子群位置变化（2D）')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def _visualize_3d_surface(self):
        # 生成目标函数网格（以Rastrigin为例，可根据实际问题调整）
        x = np.linspace(self.lb[0], self.ub[0], 100)
        y = np.linspace(self.lb[1], self.ub[1], 100)
        X, Y = np.meshgrid(x, y)
        Z = 20 + X ** 2 + Y ** 2 - 10 * np.cos(2 * np.pi * X) - 10 * np.cos(2 * np.pi * Y)

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        # 绘制3D曲面
        surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8, edgecolor='none')
        # 标记全局最优
        decoded_gbest = decode(self.gbest_chrom, self.var_types)
        gbest_pos = decoded_gbest["real_0"]
        ax.scatter(gbest_pos[0], gbest_pos[1], self.gbest_raw,
                   c='red', s=150, marker='*', label='全局最优')
        # 样式设置
        fig.colorbar(surf, ax=ax, label='函数值')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('函数值')
        ax.set_title('目标函数3D曲面')
        ax.legend()
        plt.tight_layout()
        plt.show()

    def _visualize_contour(self):
        x = np.linspace(self.lb[0], self.ub[0], 100)
        y = np.linspace(self.lb[1], self.ub[1], 100)
        X, Y = np.meshgrid(x, y)
        Z = 20 + X ** 2 + Y ** 2 - 10 * np.cos(2 * np.pi * X) - 10 * np.cos(2 * np.pi * Y)

        fig, ax = plt.subplots(figsize=(10, 8))
        contour = ax.contourf(X, Y, Z, levels=30, cmap='viridis', alpha=0.8)
        # 标记全局最优
        decoded_gbest = decode(self.gbest_chrom, self.var_types)
        gbest_pos = decoded_gbest["real_0"]
        ax.scatter(gbest_pos[0], gbest_pos[1], c='red', s=150, marker='*', label='全局最优')
        # 样式设置
        fig.colorbar(contour, ax=ax, label='函数值')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('目标函数等高线')
        ax.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def _visualize_particles_3d(self, positions: np.ndarray):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        gen_indices = []
        for i, data in enumerate(self.position_history):
            gen_indices.extend([i] * self.pop_size)
        colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))
        scatter = ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2],
                             c=colors, alpha=0.6, s=50)
        # 标记全局最优
        decoded_gbest = decode(self.gbest_chrom, self.var_types)
        gbest_pos = decoded_gbest["real_0"]
        ax.scatter(gbest_pos[0], gbest_pos[1], gbest_pos[2],
                   c='red', s=150, marker='*', label='全局最优')
        # 样式设置
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('迭代代数')
        ax.set_xlabel('变量1')
        ax.set_ylabel('变量2')
        ax.set_zlabel('变量3')
        ax.set_title('粒子群位置变化（3D）')
        ax.legend()
        plt.tight_layout()
        plt.show()

    def _visualize_particles_1d(self, positions: np.ndarray):
        fig, ax = plt.subplots(figsize=(10, 6))
        gen_indices = []
        for i, data in enumerate(self.position_history):
            gen_indices.extend([i] * self.pop_size)
        colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))
        y = np.random.normal(0, 0.1, size=len(positions))  # 随机扰动避免重叠
        scatter = ax.scatter(positions[:, 0], y, c=colors, alpha=0.6, s=50)
        # 标记全局最优
        decoded_gbest = decode(self.gbest_chrom, self.var_types)
        gbest_pos = decoded_gbest["real_0"][0]
        ax.scatter(gbest_pos, 0, c='red', s=150, marker='*', label='全局最优')
        # 样式设置
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('迭代代数')
        ax.set_xlabel('变量值')
        ax.set_ylabel('随机扰动')
        ax.set_title('粒子群位置变化（1D）')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def _visualize_particles_pca(self, positions: np.ndarray):
        pca = PCA(n_components=2)
        positions_pca = pca.fit_transform(positions)
        fig, ax = plt.subplots(figsize=(10, 6))
        gen_indices = []
        for i, data in enumerate(self.position_history):
            gen_indices.extend([i] * self.pop_size)
        colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))
        scatter = ax.scatter(positions_pca[:, 0], positions_pca[:, 1],
                             c=colors, alpha=0.6, s=50)
        # 标记全局最优（PCA降维后）
        decoded_gbest = decode(self.gbest_chrom, self.var_types)
        gbest_pos = []
        for key in decoded_gbest:
            if key.startswith("real_"):
                gbest_pos.extend(decoded_gbest[key].tolist())
        gbest_pos_pca = pca.transform([gbest_pos])[0]
        ax.scatter(gbest_pos_pca[0], gbest_pos_pca[1],
                   c='red', s=150, marker='*', label='全局最优')
        # 样式设置
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('迭代代数')
        ax.set_xlabel('PCA 维度1')
        ax.set_ylabel('PCA 维度2')
        ax.set_title(f'粒子群位置变化（PCA降维，原始维度={positions.shape[1]}）')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
if __name__ == "__main__":
    # 初始化工具和随机种子（与GA示例一致）
    fix_random_seed()
    init_mlp()
    # 设置中文字体
    plt.rcParams["font.family"] = ["SimHei", "sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

    # 1. 定义变量类型（2个实数变量，范围[-2, 2]）
    var_types = [("real", (2, -2, 2))]

    # 2. 定义适应度函数（Rosenbrock函数变种，最大化问题）
    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return -((1 - x) **2 + 100 * (y - x** 2) **2)  # 转为最大化问题

    # 3. 定义约束条件（与GA示例中的“敌对”约束完全一致）
    # (a) x + y <= 0
    def ineq1(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return x + y  # <= 0
    # (b) x^2 + y^2 <= 0.5
    def ineq2(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return x**2 + y**2 - 0.5  # <= 0
    # (c) y >= x + 0.3 → x - y + 0.3 <= 0
    def ineq3(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return x - y + 0.3  # <= 0

    # 4. 初始化带约束的PSO（参数与GA对齐）
    pso = PSO(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=100,
        max_gen=150,
        w=0.7,
        c1=1.5,
        c2=1.5,
        mutation_prob=0.08,
        visualize_gens=5,
        maximize=True,  # 与目标函数一致（最大化）
        eq_constraints=[],  # 无等式约束
        ineq_constraints=[ineq1, ineq2, ineq3],  # 应用不等式约束
        penalty_coeff=1e3  # 惩罚系数
    )

    # 5. 运行优化
    best_particle = pso.run()

    # 6. 输出结果（与GA示例格式一致）
    best_decoded = decode(best_particle.chrom, var_types)
    print("\n最优解：")
    print(f"x = {best_decoded['real_0'][0]:.6f}, y = {best_decoded['real_0'][1]:.6f}")
    print(f"原始目标值：{best_particle.raw_fitness:.6f}")
    print(f"惩罚后适应度：{best_particle.fitness:.6f}")
    print(f"违反量：{best_particle.violation:.6f}")

    # 7. 修复违反约束的解（与GA示例逻辑一致）
    best_decoded_repaired = pso.repair_solution(best_decoded)
    if best_particle.violation > 1e-6:
        print("\n修复后：")
        print(f"x = {best_decoded_repaired['real_0'][0]:.6f}, y = {best_decoded_repaired['real_0'][1]:.6f}")
        new_fitness = evaluate(best_decoded_repaired)
        print(f"修复后目标值：{new_fitness:.6f}")
        if pso.is_decoded_feasible(best_decoded_repaired):
            print('修复后满足约束')
        else:
            print('仍不满足约束')
