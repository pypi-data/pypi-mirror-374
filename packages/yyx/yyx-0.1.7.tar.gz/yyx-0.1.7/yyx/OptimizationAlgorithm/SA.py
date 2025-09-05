import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, Tuple, Callable
from utils import universal_mutate, decode, init_mlp, fix_random_seed, repair_solution, is_decoded_feasible, penalty_fun

plt.rcParams["font.family"] = ["SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


# ================= 个体类（增强约束相关属性）=================
class Solution:
    def __init__(self, chrom: np.ndarray):
        self.chrom = chrom  # 染色体
        self.fitness = None  # 惩罚后适应度
        self.raw_fitness = None  # 原始目标值
        self.violation = 0.0  # 约束违反量

    def __eq__(self, other):
        return np.array_equal(self.chrom, other.chrom)

    def __str__(self) -> str:
        if self.fitness is None:
            return "fitness=None"
        return (f"raw={self.raw_fitness:.6f}, fitness={self.fitness:.6f}, "
                f"violation={self.violation:.6f}")


# ================= 带约束的模拟退火算法（SA）类 =================
class SA:
    def __init__(
            self,
            var_types: List[Tuple[str, Tuple]],
            evaluate: Callable[[dict], float],  # 单目标函数，返回原始目标值
            init_temp: float = 100.0,  # 初始温度
            cooling_rate: float = 0.95,  # 冷却速率（每次迭代降温比例）
            max_iter: int = 1000,  # 总迭代次数
            max_stay: int = 100,  # 连续未改进的最大迭代次数（提前终止）
            mutate_prob: float = 0.1,  # 变异概率（用于生成邻域解）
            maximize: bool = True,  # 目标方向（最大化/最小化）
            eq_constraints: List[Callable[[dict], float]] = None,  # 等式约束
            ineq_constraints: List[Callable[[dict], float]] = None,  # 不等式约束
            penalty_coeff: float = 1e3  # 惩罚系数
    ):
        self.var_types = var_types
        self.evaluate = evaluate
        self.init_temp = init_temp
        self.cooling_rate = cooling_rate
        self.max_iter = max_iter
        self.max_stay = max_stay
        self.mutate_prob = mutate_prob

        # 约束相关参数（与GA/PSO保持一致）
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

        # 记录迭代过程（新增约束违反量记录）
        self.best_fitness_history = []  # 每步最优惩罚适应度
        self.best_raw_history = []  # 每步最优原始目标值
        self.avg_violation_history = []  # 平均约束违反量
        self.current_temp_history = []  # 温度变化记录
        self.current_violations = []  # 当前代的约束违反量（用于计算平均值）

    def _penalized_fitness(self, decoded: dict, iter: int) -> Tuple[float, float, float]:
        """计算惩罚后适应度、原始目标值、约束违反量（与GA/PSO一致）"""
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
        # 3. 调用外部自适应惩罚函数（与GA/PSO复用）
        # 模拟退火中用迭代次数代替代数计算自适应惩罚
        adaptive_coeff = penalty_fun(iter, self.penalty_coeff, self.max_iter)
        # 4. 计算惩罚后适应度（根据目标方向调整）
        if self.maximize:
            penalized = raw_val - adaptive_coeff * violation  # 最大化：惩罚项递减
        else:
            penalized = raw_val + adaptive_coeff * violation  # 最小化：惩罚项递增
        # 调试输出（每100次迭代打印一次）
        if iter % 100 == 0:
            print(f"调试: raw_val={raw_val:.4f}, violation={violation:.4f}, "
                  f"coeff={adaptive_coeff:.4f}, 惩罚项={adaptive_coeff * violation:.4f}")
        return penalized, raw_val, violation

    def init_solution(self) -> Solution:
        """初始化一个随机解（新增约束属性计算）"""
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
        solution = Solution(np.array(chrom, dtype=float))
        # 计算初始解的约束相关属性
        decoded = decode(solution.chrom, self.var_types)
        solution.fitness, solution.raw_fitness, solution.violation = self._penalized_fitness(decoded, 0)
        return solution

    def generate_neighbor(self, current: Solution, iter: int) -> Solution:
        """生成邻域解（新增约束属性计算）"""
        new_chrom = universal_mutate(
            current.chrom.copy(),
            self.var_types,
            self.mutate_prob
        )
        neighbor = Solution(new_chrom)
        # 计算邻域解的约束相关属性
        decoded = decode(neighbor.chrom, self.var_types)
        neighbor.fitness, neighbor.raw_fitness, neighbor.violation = self._penalized_fitness(decoded, iter)
        return neighbor

    def accept_probability(self, current_fitness: float, new_fitness: float, temp: float) -> float:
        """计算接受新解的概率（基于惩罚后适应度）"""
        if self.maximize:
            # 最大化问题：新解更好则接受
            if new_fitness > current_fitness:
                return 1.0
            else:
                return np.exp((new_fitness - current_fitness) / temp)
        else:
            # 最小化问题：新解更好则接受
            if new_fitness < current_fitness:
                return 1.0
            else:
                return np.exp((current_fitness - new_fitness) / temp)

    def run(self) -> Solution:
        """运行带约束的模拟退火算法"""
        # 初始化
        current = self.init_solution()
        best = current  # 记录全局最优

        # 初始化记录列表
        self.current_violations.append(current.violation)
        self.best_fitness_history.append(best.fitness)
        self.best_raw_history.append(best.raw_fitness)
        self.avg_violation_history.append(np.mean(self.current_violations))
        self.current_temp_history.append(self.init_temp)

        temp = self.init_temp
        no_improve_cnt = 0  # 连续未改进计数器

        # 迭代退火过程
        for iter in range(self.max_iter):
            # 生成邻域解（传入当前迭代次数用于计算惩罚）
            neighbor = self.generate_neighbor(current, iter)

            # 记录当前解的违反量（用于计算平均值）
            self.current_violations.append(neighbor.violation)
            # 只保留最近的pop_size个值用于计算平均违反量
            if len(self.current_violations) > 100:  # 用100近似种群规模
                self.current_violations.pop(0)

            # 计算接受概率并决定是否接受
            prob = self.accept_probability(current.fitness, neighbor.fitness, temp)
            if random.random() < prob:
                current = neighbor  # 接受新解

            # 更新全局最优（基于惩罚后适应度）
            improved = False
            if self.maximize:
                if current.fitness > best.fitness:
                    best = current
                    improved = True
            else:
                if current.fitness < best.fitness:
                    best = current
                    improved = True

            if improved:
                no_improve_cnt = 0  # 重置未改进计数器
            else:
                no_improve_cnt += 1

            # 记录历史数据
            self.best_fitness_history.append(best.fitness)
            self.best_raw_history.append(best.raw_fitness)
            self.avg_violation_history.append(np.mean(self.current_violations))
            self.current_temp_history.append(temp)

            # 打印进度（每100次迭代）
            if (iter + 1) % 100 == 0:
                print(f"迭代 {iter + 1}/{self.max_iter} | 温度: {temp:.2f} | "
                      f"最优惩罚适应度: {best.fitness:.6f} | "
                      f"平均违反量: {self.avg_violation_history[-1]:.6f}")

            # 提前终止条件（连续多次未改进）
            if no_improve_cnt >= self.max_stay:
                print(f"提前终止：连续{self.max_stay}次迭代未改进")
                break

            # 降温
            temp *= self.cooling_rate
            if temp < 1e-8:  # 温度过低时强制终止
                print("温度过低，停止迭代")
                break

        return best

    def repair_solution(self, decoded: dict, max_time: float = 1.0, step: float = 0.01) -> dict:
        """修复违反约束的解（与GA/PSO接口一致）"""
        return repair_solution(self, decoded, max_time, step)

    def is_decoded_feasible(self, decoded, tol=1e-6) -> bool:
        """检查解是否可行（与GA/PSO接口一致）"""
        return is_decoded_feasible(self, decoded, tol)

    def plot_process(self):
        """绘制退火过程曲线（纯线性坐标轴，优化温度衰减展示）"""
        # 1. 绘制适应度与温度双轴曲线（核心图表）
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # 左轴：适应度曲线（惩罚后+原始目标值）
        ax1.plot(
            range(len(self.best_fitness_history)),
            self.best_fitness_history,
            c='red',
            linewidth=2,
            label='最优惩罚适应度'
        )
        ax1.plot(
            range(len(self.best_raw_history)),
            self.best_raw_history,
            c='green',
            linewidth=2,
            linestyle='--',
            label='最优原始目标值'
        )
        ax1.set_xlabel('迭代次数', fontsize=11)
        ax1.set_ylabel('适应度/目标值', fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='lower right', fontsize=10)

        # 右轴：温度曲线（线性坐标轴，优化视觉效果）
        ax2 = ax1.twinx()
        # 温度曲线加粗+间隔标记点，凸显指数衰减趋势
        ax2.plot(
            range(len(self.current_temp_history)),
            self.current_temp_history,
            c='blue',
            linewidth=2.5,
            marker='o',
            markersize=2.5,
            markevery=5,  # 每5步1个标记点，平衡细节与简洁
            label=f'温度（冷却率={self.cooling_rate}）'
        )
        # 温度轴范围优化：下限0，上限留10%余量，避免曲线贴边
        max_temp = max(self.current_temp_history)
        ax2.set_ylim(bottom=0, top=max_temp * 1.1)
        ax2.set_ylabel('温度（线性尺度）', fontsize=11)
        ax2.legend(loc='upper right', fontsize=10)
        ax2.grid(True, alpha=0.3, linestyle=':')  # 细网格辅助观察

        # 图表标题：包含关键参数，方便实验追溯
        plt.title(
            f'模拟退火过程 | 初始温度={self.init_temp} | 冷却率={self.cooling_rate}',
            fontsize=12
        )
        plt.tight_layout()
        plt.show()


        # 3. 约束违反量曲线（仅当有约束时展示，与原逻辑一致）
        if self.eq_constraints or self.ineq_constraints:
            plt.figure(figsize=(10, 6))
            plt.plot(
                range(len(self.avg_violation_history)),
                self.avg_violation_history,
                c='purple',
                linewidth=2,
                label='平均约束违反量'
            )
            # 添加“约束满足线”（违反量=0），直观判断可行性
            plt.axhline(y=0, c='black', linestyle='--', alpha=0.5, label='约束满足线（违反量=0）')
            plt.xlabel('迭代次数', fontsize=11)
            plt.ylabel('平均约束违反量', fontsize=11)
            plt.title('约束违反量变化曲线', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend(fontsize=10)
            plt.tight_layout()
            plt.show()


# ================= 使用示例（与GA/PSO完全对齐） =================
if __name__ == "__main__":
    # 初始化工具和随机种子（与GA/PSO示例一致）
    fix_random_seed()
    init_mlp()

    # 1. 变量定义（与其他算法保持一致）
    var_types = [("real", (2, -2, 2))]  # 2个实数变量


    # 2. 目标函数（与GA/PSO示例一致）
    def evaluate(decoded: dict) -> float:
        x, y = decoded["real_0"]
        # Rosenbrock函数变种（转为最大化问题）
        return -((1 - x) ** 2 + 100 * (y - x ** 2) ** 2)


    # 3. 定义约束条件（与GA/PSO示例中的“敌对”约束完全一致）
    # (a) x + y <= 0
    def ineq1(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return x + y  # <= 0


    # (b) x^2 + y^2 <= 0.5
    def ineq2(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return x ** 2 + y ** 2 - 0.5  # <= 0


    # (c) y >= x + 0.3 → x - y + 0.3 <= 0
    def ineq3(decoded: dict) -> float:
        x, y = decoded["real_0"]
        return x - y + 0.3  # <= 0


    # 4. 初始化带约束的SA（参数与其他算法对齐）
    sa = SA(
        var_types=var_types,
        evaluate=evaluate,
        init_temp=100.0,
        cooling_rate=0.95,
        max_iter=1000,
        max_stay=100,
        mutate_prob=0.1,
        maximize=True,  # 与目标函数一致（最大化）
        eq_constraints=[],  # 无等式约束
        ineq_constraints=[ineq1, ineq2, ineq3],  # 应用不等式约束
        penalty_coeff=1e3  # 惩罚系数
    )

    # 5. 运行算法
    best_solution = sa.run()

    # 6. 输出结果（与GA/PSO示例格式一致）
    best_decoded = decode(best_solution.chrom, var_types)
    print("\n最优解：")
    print(f"变量值：x={best_decoded['real_0'][0]:.6f}, y={best_decoded['real_0'][1]:.6f}")
    print(f"原始目标值：{best_solution.raw_fitness:.6f}")
    print(f"惩罚后适应度：{best_solution.fitness:.6f}")
    print(f"违反量：{best_solution.violation:.6f}")

    # 7. 修复违反约束的解（与其他算法逻辑一致）
    best_decoded_repaired = sa.repair_solution(best_decoded)
    if best_solution.violation > 1e-6:
        print("\n修复后：")
        print(f"变量值：x={best_decoded_repaired['real_0'][0]:.6f}, y={best_decoded_repaired['real_0'][1]:.6f}")
        new_fitness = evaluate(best_decoded_repaired)
        print(f"修复后目标值：{new_fitness:.6f}")
        if sa.is_decoded_feasible(best_decoded_repaired):
            print('修复后满足约束')
        else:
            print('仍不满足约束')

    # 8. 绘制过程曲线
    sa.plot_process()
