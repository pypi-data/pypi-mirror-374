import numpy as np
import matplotlib.pyplot as plt
import yyx
# 1. 构造模拟数据（如：含日周期、周周期的用电量数据）
t = np.linspace(0, 7*24, 7*24*60)  # 7天，每分钟一个数据点（时间轴）
freq1 = 1/24  # 日周期（24小时）
freq2 = 1/(24*7)  # 周周期（168小时）
data = 100 + 20*np.sin(2*np.pi*freq1*t) + 10*np.sin(2*np.pi*freq2*t) + 5*np.random.randn(len(t))  # 带噪声的用电量数据

# 2. 傅里叶变换
n = len(data)
fft_result = np.fft.fft(data)  # 傅里叶变换结果（复数）
freq = np.fft.fftfreq(n, d=t[1]-t[0])  # 频率轴（d为时间间隔）
amplitude = np.abs(fft_result) / n  # 振幅（归一化）

# 3. 绘图：频域结果（找周期）
plt.figure(figsize=(10,4))
plt.plot(freq[freq>0], amplitude[freq>0])  # 只看正频率
plt.xlabel('频率 (1/小时)')
plt.ylabel('振幅')
plt.title('用电量数据的傅里叶变换结果')
plt.axvline(x=freq1, color='r', linestyle='--', label=f'日周期频率={freq1:.4f}')
plt.axvline(x=freq2, color='g', linestyle='--', label=f'周周期频率={freq2:.4f}')
plt.ylim(0,0.2)
plt.legend()
plt.show()
# 结果：图中红色、绿色线处会出现峰值，证明数据含日、周周期