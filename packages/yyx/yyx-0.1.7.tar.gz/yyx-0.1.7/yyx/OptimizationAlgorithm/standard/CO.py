# 猎豹优化算法（Cheetah Optimization Algorithm, CO）
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from utils import decode, init_mlp  # 复用解析函数和中文设置


# ================= 猎豹个体类（单目标场景）=================
class Cheetah:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体（位置向量）
        self.fitness = None  # 适应度值（越大越好）
        self.speed = 0.0  # 移动速度
        self.stamina = 0.0  # 耐力（影响行为模式）

    def __str__(self) -> str:
        if self.fitness is None:
            return "fitness=None"
        return f"fitness={self.fitness:.6f}, speed={self.speed:.6f}, stamina={self.stamina:.6f}"


# ================= 猎豹优化算法（CO）类 =================
class CO:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标评估函数
            pop_size: int = 30,
            max_gen: int = 100,
            speed_init: float = 1.0,  # 初始速度
            speed_decay: float = 0.97,  # 速度衰减系数
            stamina_init: float = 1.0,  # 初始耐力
            stamina_recovery: float = 0.05  # 耐力恢复系数
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.speed_init = speed_init
        self.speed_decay = speed_decay
        self.stamina_init = stamina_init
        self.stamina_recovery = stamina_recovery

        # 解析变量范围
        self.var_ranges = []  # 存储每个变量的(类型, 下界, 上界)
        self.dim = 0  # 变量维度
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

        # 迭代记录
        self.best_fitness_history = []  # 每代最优适应度
        self.avg_fitness_history = []  # 每代平均适应度

    def _init_cheetah(self) -> Cheetah:
        """初始化猎豹个体，确保所有属性都有明确值"""
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

        cheetah = Cheetah(np.array(chrom, dtype=float))
        # 明确初始化速度和耐力
        cheetah.speed = self.speed_init * np.random.random()
        cheetah.stamina = self.stamina_init
        return cheetah

    def _bound_position(self, chrom: np.ndarray) -> np.ndarray:
        """位置边界处理"""
        bounded = chrom.copy()
        for i in range(self.dim):
            vtype, low, high = self.var_ranges[i]
            # 边界截断
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

    def _stalk_behavior(self, cheetah: Cheetah, prey_pos: np.ndarray) -> np.ndarray:
        """潜伏行为：缓慢靠近最优解，小范围探索"""
        direction = prey_pos - cheetah.chrom
        move = 0.1 * cheetah.speed * cheetah.stamina * direction
        noise = 0.05 * (self.high - self.low) * np.random.randn(self.dim)
        return cheetah.chrom + move + noise

    def _chase_behavior(self, cheetah: Cheetah, prey_pos: np.ndarray) -> np.ndarray:
        """追捕行为：快速冲向最优解，大步长移动"""
        direction = prey_pos - cheetah.chrom
        move = cheetah.speed * cheetah.stamina * direction
        dir_noise = (np.random.rand(self.dim) - 0.5) * 2 * 0.1  # [-0.1, 0.1]
        return cheetah.chrom + move * (1 + dir_noise)

    def _ambush_behavior(self, cheetah: Cheetah) -> np.ndarray:
        """突袭行为：大范围随机搜索新区域"""
        jump = cheetah.speed * (np.random.rand(self.dim) - 0.5) * (self.high - self.low)
        return cheetah.chrom + jump

    def run(self) -> Cheetah:
        """运行优化算法"""
        # 初始化种群
        population = [self._init_cheetah() for _ in range(self.pop_size)]
        for cheetah in population:
            decoded = decode(cheetah.chrom, self.var_types)
            cheetah.fitness = self.evaluate(decoded)

        # 记录初始状态
        self._record_fitness(population)

        # 迭代优化
        for gen in range(self.max_gen):
            # 确定当前最优个体（猎物位置）
            best_cheetah = max(population, key=lambda x: x.fitness)
            prey_pos = best_cheetah.chrom.copy()

            # 个体行为更新
            for i in range(self.pop_size):
                cheetah = population[i]

                # 耐力恢复（每代少量恢复，不超过最大值1.0）
                cheetah.stamina = min(1.0, cheetah.stamina + self.stamina_recovery)

                # 根据适应度和耐力选择行为模式
                if cheetah.fitness > 0.8 * best_cheetah.fitness and cheetah.stamina > 0.7:
                    # 高适应度+高耐力 → 潜伏（局部开发）
                    new_chrom = self._stalk_behavior(cheetah, prey_pos)
                elif cheetah.fitness > 0.3 * best_cheetah.fitness and cheetah.stamina > 0.3:
                    # 中等适应度+中等耐力 → 追捕（向优解聚集）
                    new_chrom = self._chase_behavior(cheetah, prey_pos)
                    cheetah.stamina *= 0.8  # 追捕消耗耐力
                else:
                    # 低适应度或低耐力 → 突袭（全局探索）
                    new_chrom = self._ambush_behavior(cheetah)
                    cheetah.stamina = 0.5  # 突袭后耐力重置

                # 边界处理与评估
                new_chrom = self._bound_position(new_chrom)
                new_cheetah = Cheetah(new_chrom)
                decoded = decode(new_cheetah.chrom, self.var_types)
                new_cheetah.fitness = self.evaluate(decoded)
                new_cheetah.speed = cheetah.speed * self.speed_decay  # 速度衰减

                # 贪婪选择
                if new_cheetah.fitness > cheetah.fitness:
                    population[i] = new_cheetah

            # 记录当前代信息
            self._record_fitness(population)

            # 打印进度（中文显示）
            if (gen + 1) % 10 == 0:
                best_fitness = self.best_fitness_history[-1]
                avg_fitness = self.avg_fitness_history[-1]
                print(f"第{gen + 1}/{self.max_gen}代 | 最优适应度: {best_fitness:.6f} | 平均适应度: {avg_fitness:.6f}")

        # 返回最优个体
        return max(population, key=lambda x: x.fitness)

    def _record_fitness(self, population: List[Cheetah]):
        """记录适应度统计信息"""
        fitness_values = [cheetah.fitness for cheetah in population]
        self.best_fitness_history.append(max(fitness_values))
        self.avg_fitness_history.append(np.mean(fitness_values))

    def plot_fitness_curve(self):
        """绘制适应度变化曲线（中文显示）"""
        plt.figure(figsize=(10, 6))
        # 最优适应度曲线
        plt.plot(
            range(1, len(self.best_fitness_history) + 1),
            self.best_fitness_history,
            c='red',
            linewidth=2,
            label='每代最优适应度'
        )
        # 平均适应度曲线
        plt.plot(
            range(1, len(self.avg_fitness_history) + 1),
            self.avg_fitness_history,
            c='blue',
            linewidth=2,
            linestyle='--',
            label='每代平均适应度'
        )
        # 图表设置（中文显示）
        plt.xlabel('迭代次数', fontsize=12)
        plt.ylabel('适应度值', fontsize=12)
        plt.title('猎豹优化算法适应度变化曲线', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=10)
        plt.tight_layout()
        plt.show()


# ================= 统一问题测试 =================
if __name__ == "__main__":
    # 初始化中文显示（已封装）
    init_mlp()

    # 1. 变量定义（统一问题：2个实数变量，范围[-5.12, 5.12]）
    var_types = [("real", (2, -5.12, 5.12))]


    # 2. 目标函数（Rastrigin函数，求最小值，转为适应度越大越好）
    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]
        # 原始函数：20 + x² + y² - 10cos(2πx) - 10cos(2πy)，最小值0
        return -(20 + x ** 2 + y ** 2 - 10 * np.cos(2 * np.pi * x) - 10 * np.cos(2 * np.pi * y))


    # 3. 初始化CO算法
    co = CO(
        var_types=var_types,
        evaluate=evaluate,
        pop_size=30,
        max_gen=100,
        speed_init=0.8,
        speed_decay=0.97,
        stamina_init=1.0,
        stamina_recovery=0.05
    )

    # 4. 运行算法
    best_cheetah = co.run()

    # 5. 解析并输出结果（中文显示）
    best_decoded = decode(best_cheetah.chrom, var_types)
    x_opt, y_opt = best_decoded["real_0"]
    # 转换为原始函数的最小值
    min_value = -(best_cheetah.fitness)

    print("\n========== 优化结果 ==========")
    print(f"最优变量值：x = {x_opt:.6f}, y = {y_opt:.6f}")
    print(f"Rastrigin函数最小值：{min_value:.6f}")  # 理论最小值为0

    # 6. 绘制适应度曲线
    co.plot_fitness_curve()
