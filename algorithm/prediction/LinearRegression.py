import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

SYSTEM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 系统工程根目录 movie-system/
DATA_DIR = os.path.join(SYSTEM_ROOT, 'data')  # 统一数据目录


sys.stdout.reconfigure(encoding='utf-8')

# 1. 数据加载与分析
def load_and_analyze():
    # 加载数据
    df = pd.read_csv(os.path.join(DATA_DIR, 'train.csv'))
    print("数据集基本信息：")
    print(f"形状：{df.shape}")
    print("前5行数据：")
    print(df[['budget', 'revenue']].head())

    # 筛选有效数据（预算和票房均为正数）
    valid_df = df[(df['budget'] > 0) & (df['revenue'] > 0)].copy()
    print(f"\n有效样本数：{len(valid_df)}/{len(df)}")

    # 基本统计分析
    print("\n预算统计（美元）：")
    print(valid_df['budget'].describe().apply(lambda x: f"{x:,.0f}"))
    print("\n票房统计（美元）：")
    print(valid_df['revenue'].describe().apply(lambda x: f"{x:,.0f}"))

    return valid_df


# 2. 数据预处理
def preprocess_data(valid_df):
    # 特征与目标变量（转换单位：预算→千万美元，票房→亿美元）
    X = valid_df[['budget']] / 1e8  # 预算单位：千万美元
    y = valid_df['revenue'] / 1e9  # 票房单位：亿美元

    # 划分训练集和测试集（8:2）
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test


# 3. 模型训练
def train_model(X_train, y_train):
    model = LinearRegression()
    model.fit(X_train, y_train)
    print(f"\n线性回归方程：票房 = {model.coef_[0]:.2f}×预算 + {model.intercept_:.2f}")
    return model


# 4. 模型评估
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


# 5. 可视化（生成image.png）
def visualize(X, y, model, y_pred, X_test):
    # 设置中文字体，解决乱码问题
    plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

    plt.figure(figsize=(10, 6))

    # 绘制散点图（原始数据）
    plt.scatter(X, y, alpha=0.6, color='blue', label='实际数据')

    # 绘制回归线
    plt.plot(X, model.predict(X), color='red', linewidth=2, label='线性回归')

    # 标注测试集预测点
    plt.scatter(X_test, y_pred, color='green', marker='x', s=100, label='测试集预测')

    # 设置坐标轴标签和标题（此时中文可正常显示）
    plt.xlabel('电影预算（千万美元）', fontsize=12)
    plt.ylabel('电影票房（亿美元）', fontsize=12)
    plt.title('电影预算与票房关系及线性回归预测', fontsize=14)
    plt.legend()
    plt.grid(alpha=0.3)

    # 保存图像
    plt.savefig('image.png', dpi=300, bbox_inches='tight')
    print("\n可视化结果已保存为image.png")
    plt.show()


# 主函数
def main():
    valid_df = load_and_analyze()
    X_train, X_test, y_train, y_test = preprocess_data(valid_df)
    model = train_model(X_train, y_train)
    y_pred = evaluate_model(model, X_test, y_test)
       # 合并特征数据（X_train和X_test）
    X_combined = pd.concat([X_train, X_test], ignore_index=True)
    # 合并标签数据（y_train和y_test）
    y_combined = pd.concat([y_train, y_test], ignore_index=True)
    # 调用visualize函数
    visualize(X_combined, y_combined, model, y_pred, X_test)

if __name__ == "__main__":
    main()