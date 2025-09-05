#粒子群算法
import random
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from typing import List, Tuple, Callable
from .operators import decode


class Particle:
    """粒子类（适配单目标优化）"""
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 粒子位置（染色体）
        self.fitness = None  # 适应度值（单目标）
        self.pbest_chrom = None  # 个体最优位置
        self.pbest_fitness = None  # 个体最优适应度

    def __str__(self, maximize: bool = False) -> str:
        if self.fitness is None:
            return "fitness=None"
        val = -self.fitness if maximize else self.fitness
        return f"fitness={val:.6f}"

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
            visualize_gens: int = 5  # 要可视化的代数
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.mutation_prob = mutation_prob
        self.visualize_gens = visualize_gens  # 控制最终可视化的代数

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
        self.gbest_fitness = None

        # 变量边界
        self.lb, self.ub = self._get_bounds()
        self.vmax = 0.1 * (self.ub - self.lb)
        self.vmin = -self.vmax

        # 记录可视化数据（粒子位置历史）
        self.position_history = []  # 存储不同代的粒子位置
        self.best_fitness_history = []  # 收敛曲线数据

    def _get_bounds(self) -> Tuple[np.ndarray, np.ndarray]:
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

    def init_particles(self):
        self.particles = [self._init_particle() for _ in range(self.pop_size)]
        self.velocities = [
            np.random.uniform(self.vmin, self.vmax, size=self.chrom_length)
            for _ in range(self.pop_size)
        ]
        self._update_pbest()
        self._update_gbest()

    def _init_particle(self) -> Particle:
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
        decoded = decode(particle.chrom, self.var_types)
        particle.fitness = self.evaluate(decoded)
        return particle

    def _update_pbest(self):
        for particle in self.particles:
            if particle.pbest_fitness is None:
                particle.pbest_chrom = particle.chrom.copy()
                particle.pbest_fitness = particle.fitness
            else:
                if particle.fitness < particle.pbest_fitness:
                    particle.pbest_chrom = particle.chrom.copy()
                    particle.pbest_fitness = particle.fitness

    def _update_gbest(self):
        current_best = min(self.particles, key=lambda p: p.pbest_fitness)
        if self.gbest_fitness is None:
            self.gbest_chrom = current_best.pbest_chrom.copy()
            self.gbest_fitness = current_best.pbest_fitness
        else:
            if current_best.pbest_fitness < self.gbest_fitness:
                self.gbest_chrom = current_best.pbest_chrom.copy()
                self.gbest_fitness = current_best.pbest_fitness

    def _update_velocity(self, idx: int):
        particle = self.particles[idx]
        r1 = np.random.random(size=self.chrom_length)
        r2 = np.random.random(size=self.chrom_length)
        vel = self.w * self.velocities[idx] + \
              self.c1 * r1 * (particle.pbest_chrom - particle.chrom) + \
              self.c2 * r2 * (self.gbest_chrom - particle.chrom)
        self.velocities[idx] = np.clip(vel, self.vmin, self.vmax)

    def _update_position(self, idx: int):
        particle = self.particles[idx]
        new_chrom = particle.chrom + self.velocities[idx]

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

        if random.random() < self.mutation_prob:
            new_chrom = self._mutate(new_chrom)

        particle.chrom = new_chrom
        decoded = decode(particle.chrom, self.var_types)
        particle.fitness = self.evaluate(decoded)

    def _mutate(self, chrom: np.ndarray) -> np.ndarray:
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
        """记录当前代的粒子位置（用于可视化）"""
        # 仅记录实数变量（二进制/整数可视化为离散点）
        real_positions = []
        for particle in self.particles:
            decoded = decode(particle.chrom, self.var_types)
            # 提取所有实数变量并拼接
            real_vars = []
            for key in decoded:
                if key.startswith("real_"):
                    real_vars.extend(decoded[key].tolist())
            real_positions.append(real_vars)
        self.position_history.append({
            "gen": gen,
            "positions": np.array(real_positions)
        })

    def run(self) -> Tuple[np.ndarray, float]:
        self.init_particles()
        self.best_fitness_history = [self.gbest_fitness]

        # 计算每代的间隔，确保最终只保留5代
        interval = max(1, self.max_gen // (self.visualize_gens - 1))

        for gen in range(self.max_gen):
            for i in range(self.pop_size):
                self._update_velocity(i)
                self._update_position(i)
            self._update_pbest()
            self._update_gbest()
            self.best_fitness_history.append(self.gbest_fitness)

            # 按间隔记录粒子位置
            if (gen + 1) % interval == 0 or gen == self.max_gen - 1:
                self._record_positions(gen + 1)
                print(f"第{gen+1}代，当前最优适应度：{self.gbest_fitness:.6f}")

        # 确保最终只保留5代（若记录过多，截取前5代）
        if len(self.position_history) > self.visualize_gens:
            self.position_history = self.position_history[:self.visualize_gens]

        # 运行结束后可视化
        self.visualize()
        return self.gbest_chrom, self.gbest_fitness

    def visualize(self):
        """可视化函数：固定输出3幅图，2维变量时为收敛曲线+粒子分布+3D曲面，等高线作为第4幅补充"""
        # 1. 绘制收敛曲线（第一幅图）
        self._visualize_convergence()

        # 2. 提取实数变量维度和位置
        if not self.position_history:
            return
        real_dim = self.position_history[0]["positions"].shape[1]
        all_positions = np.vstack([data["positions"] for data in self.position_history])

        # 3. 根据维度绘制后续图
        if real_dim == 2:
            # 2维变量：第二幅=2D粒子分布，第三幅=3D曲面，额外补充等高线图
            self._visualize_particles_2d(all_positions)
            self._visualize_3d_surface()  # 独立3D曲面图
            self._visualize_contour()  # 独立等高线图
        else:
            # 多维变量：第二幅=PCA降维粒子分布，第三幅=3D粒子图（≥3维）或1D图
            self._visualize_particles_pca(all_positions)
            if real_dim >= 3:
                self._visualize_particles_3d(all_positions)
            else:
                self._visualize_particles_1d(all_positions)

    def _visualize_convergence(self):
        """绘制收敛曲线（第一幅图）"""
        plt.figure(figsize=(10, 6))
        plt.plot(range(len(self.best_fitness_history)), self.best_fitness_history,
                 c='blue', linewidth=2, marker='o', markersize=4)
        plt.xlabel('迭代次数')
        plt.ylabel('最优适应度')
        plt.title('PSO算法收敛曲线')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def _visualize_particles_2d(self, positions: np.ndarray):
        """2D粒子位置静态图（第二幅图）"""
        fig, ax = plt.subplots(figsize=(10, 6))
        gen_indices = []
        for i, data in enumerate(self.position_history):
            gen_indices.extend([i] * self.pop_size)
        colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))
        scatter = ax.scatter(positions[:, 0], positions[:, 1], c=colors, alpha=0.6, s=50)
        # 全局最优标记
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
        """独立绘制3D曲面图（第三幅图）"""
        # 生成网格数据
        x = np.linspace(-5.12, 5.12, 100)
        y = np.linspace(-5.12, 5.12, 100)
        X, Y = np.meshgrid(x, y)
        Z = 20 + X ** 2 + Y ** 2 - 10 * np.cos(2 * np.pi * X) - 10 * np.cos(2 * np.pi * Y)

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        # 绘制3D曲面
        surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8, edgecolor='none')
        # 标记全局最优
        decoded_gbest = decode(self.gbest_chrom, self.var_types)
        gbest_pos = decoded_gbest["real_0"]
        gbest_value = self.evaluate(decoded_gbest)
        ax.scatter(gbest_pos[0], gbest_pos[1], gbest_value,
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
        """独立绘制等高线图（第四幅补充图）"""
        # 生成网格数据
        x = np.linspace(-5.12, 5.12, 100)
        y = np.linspace(-5.12, 5.12, 100)
        X, Y = np.meshgrid(x, y)
        Z = 20 + X ** 2 + Y ** 2 - 10 * np.cos(2 * np.pi * X) - 10 * np.cos(2 * np.pi * Y)

        fig, ax = plt.subplots(figsize=(10, 8))
        # 绘制等高线
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
        """3D粒子位置静态图（第三幅图）"""
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        gen_indices = []
        for i, data in enumerate(self.position_history):
            gen_indices.extend([i] * self.pop_size)
        colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))
        scatter = ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2],
                             c=colors, alpha=0.6, s=50)
        # 全局最优标记
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
        """1D粒子位置静态图（第三幅图）"""
        fig, ax = plt.subplots(figsize=(10, 6))
        gen_indices = []
        for i, data in enumerate(self.position_history):
            gen_indices.extend([i] * self.pop_size)
        colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))
        y = np.random.normal(0, 0.1, size=len(positions))  # 随机扰动避免重叠
        scatter = ax.scatter(positions[:, 0], y, c=colors, alpha=0.6, s=50)
        # 全局最优标记
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
        """PCA降维粒子位置图（第二幅图）"""
        pca = PCA(n_components=2)
        positions_pca = pca.fit_transform(positions)
        fig, ax = plt.subplots(figsize=(10, 6))
        gen_indices = []
        for i, data in enumerate(self.position_history):
            gen_indices.extend([i] * self.pop_size)
        colors = plt.cm.viridis(np.array(gen_indices) / len(self.position_history))
        scatter = ax.scatter(positions_pca[:, 0], positions_pca[:, 1],
                             c=colors, alpha=0.6, s=50)
        # 全局最优标记（PCA降维后）
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


# ================= 使用示例 =================
if __name__ == "__main__":
    # ================= 1. 定义优化问题 =================
    # 变量类型：2个实数变量，范围[-5.12, 5.12]（Rastrigin函数经典范围）
    plt.rcParams["font.family"] = ["SimHei", "sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
    var_types = [("real", (2, -5.12, 5.12))]  # 可修改为多维变量，如("real", (3, -5.12, 5.12))
    # 目标函数：Rastrigin函数（带多个局部最优的经典测试函数）
    def evaluate(decoded: dict) -> float:
        # 解析实数变量（支持2维或多维）
        vars_real = decoded["real_0"]  # 例如2维时为[x, y]，3维时为[x, y, z]
        A = 20
        result = A * len(vars_real)
        for xi in vars_real:
            result += xi**2 - A * np.cos(2 * np.pi * xi)
        return result  # 最小化目标，理论最小值为0（所有变量为0时）

    pso = PSO(
        var_types=var_types,       # 变量类型定义
        evaluate=evaluate,         # 目标函数
        pop_size=50,               # 粒子数量
        max_gen=100,               # 迭代次数
        w=0.7,                     # 惯性权重
        c1=1.5,                    # 认知系数（自我学习）
        c2=1.5,                    # 社会系数（群体学习）
        mutation_prob=0.05,        # 变异概率（增加多样性）
        visualize_gens=5           # 可视化的代数（平均分布在迭代过程中）
    )

    # ================= 3. 运行优化并获取结果 =================
    try:
        best_chrom, best_fitness = pso.run()
    except Exception as e:
        print(f"优化过程出错：{e}")
        exit(1)

    # ================= 4. 解析并输出最优结果 =================
    try:
        best_decoded = decode(best_chrom, var_types)
        # 提取实数变量结果（根据维度动态处理）
        real_vars = best_decoded["real_0"]
        print("\n================= 优化结果 ==================")
        print(f"最优变量值：{[f'{x:.6f}' for x in real_vars]}")
        print(f"最优目标函数值：{best_fitness:.6f}")
        print(f"理论最优值：0.0（当所有变量为0时）")
        print("=============================================")
    except Exception as e:
        print(f"结果解析出错：{e}")