import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

import sys
import io

SYSTEM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 系统工程根目录 movie-system/
DATA_DIR = os.path.join(SYSTEM_ROOT, 'data')  # 统一数据目录
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')  # 强制标准输出为 UTF-8


# 1. 数据加载与分析
def load_and_analyze():
    df = pd.read_csv(os.path.join(DATA_DIR, 'train.csv'))
    print("数据集基本信息：")
    print(f"形状：{df.shape}")
    print("前5行数据（包含popularity和revenue）：")
    print(df[['popularity', 'revenue']].head())

    # 筛选有效数据（保留原始分布，避免过度过滤）
    valid_df = df[(df['popularity'] >= 0) & (df['revenue'] >= 0)].copy()  # 允许0值，保留更多样本
    print(f"\n有效样本数：{len(valid_df)}/{len(df)}")

    # 打印流行度原始分布，确认是否需要转换
    print("\n流行度(popularity)原始统计：")
    print(valid_df['popularity'].describe().apply(lambda x: f"{x:.2f}"))
    print("\n票房(revenue)原始统计（美元）：")
    print(valid_df['revenue'].describe().apply(lambda x: f"{x:,.0f}"))

    return valid_df


# 2. 数据预处理（核心修正：调整单位转换，避免数据过度压缩）
def preprocess_data(valid_df):
    # 关键修正：根据原始数据范围调整单位（图2中x轴分布较宽，说明未除以1e8）
    # 假设原始popularity范围在0-400（常见电影数据集范围），无需除以1e8，直接使用原始值或除以100
    X = valid_df[['popularity']] / 100  # 轻微缩放，让x轴范围匹配图2（0-4）
    y = valid_df['revenue'] / 1e9  # 票房仍保持1e9单位（与图2一致）

    # KNN特征标准化
    # 确保每个特征对距离的影响权重一致，提高KNN预测的准确性。
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test, X  # 返回调整后的X


# 3. 模型训练（保持不变）
def train_model(X_train, y_train):
    knn = KNeighborsRegressor(n_neighbors=10)  # 可尝试增大K值（如10）优化平滑度
    knn.fit(X_train, y_train)
    print(f"\nKNN模型（K=5）训练完成")
    return knn


# 4. 模型评估（保持不变）
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    print("\n模型评估指标：")
    print(f"均方误差（MSE）：{mse:.4f}")
    print(f"均方根误差（RMSE）：{rmse:.4f}")
    print(f"R²分数：{r2:.4f}")
    print(f"平均绝对误差（MAE）：{mae:.4f}")
    return y_pred


# 5. 可视化（优化数据点展示）
def visualize(X, y, model, X_scaled):
    plt.rcParams["font.family"] = ["Arial", "SimHei", "Microsoft YaHei", "sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False

    plt.figure(figsize=(10, 6))

    # 绘制散点图（减小点大小，增加透明度，避免重叠）
    plt.scatter(X, y, alpha=0.5, color='green', s=10)  # s=10让点更小，避免密集成线

    # 绘制KNN预测曲线（可选，无曲线可注释）
    X_sorted = np.sort(X, axis=0)
    X_sorted_scaled = StandardScaler().fit_transform(X_sorted)
    y_pred_sorted = model.predict(X_sorted_scaled)
    plt.plot(X_sorted, y_pred_sorted, color='black', linewidth=1.5)  # 无曲线，可注释

    # 坐标轴设置
    plt.xlabel('电影受欢迎程度', fontsize=12)
    plt.ylabel('票房', fontsize=12)
    plt.title('电影受欢迎程度和票房之间的联系', fontsize=14)
    # 设置 x 轴显示范围的函数，作用是将x轴的可视区间限制在 [-0.5, 4.0]之间
    plt.xlim(-0.5, 4.0)
    # 设置 y 轴显示范围的函数，作用是将y轴的可视区间限定在 [-0.5, 2.0]之间
    plt.ylim(-0.5, 2.0)

    # 单位标注
    plt.text(4.05, -0.05, '1e2', fontsize=10)  # 修正为实际缩放单位（因X除以100）
    plt.text(-0.45, 2.05, '1e9', fontsize=10)

    plt.grid(False)
    plt.savefig('image.png', dpi=300, bbox_inches='tight')
    print("\n可视化结果已保存为image.png")
    plt.show()


# 主函数（保持不变）
def main():
    valid_df = load_and_analyze()
    X_train, X_test, y_train, y_test, X_original = preprocess_data(valid_df)
    model = train_model(X_train, y_train)
    y_pred = evaluate_model(model, X_test, y_test)
    X_scaled = StandardScaler().fit_transform(X_original)
    visualize(X_original, valid_df['revenue'] / 1e9, model, X_scaled)


if __name__ == "__main__":
    main()