import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

SYSTEM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 系统工程根目录 movie-system/
DATA_DIR = os.path.join(SYSTEM_ROOT, 'data')  # 统一数据目录

# 1. 数据加载与分析（假设用`budget`替代，因原数据集无`theatrical`，需选分布合理的特征）
def load_and_analyze():
    df = pd.read_csv(os.path.join(DATA_DIR, 'train.csv'))
    print("数据集基本信息：")
    print(f"形状：{df.shape}")
    print("前5行数据（包含budget和revenue）：")
    print(df[['budget', 'revenue']].head())

    # 筛选有效数据（预算和票房均为正数）
    valid_df = df[(df['budget'] > 0) & (df['revenue'] > 0)].copy()
    print(f"\n有效样本数：{len(valid_df)}/{len(df)}")

    # 基本统计分析
    print("\n预算(budget)统计（美元）：")
    print(valid_df['budget'].describe().apply(lambda x: f"{x:,.0f}"))
    print("\n票房(revenue)统计（美元）：")
    print(valid_df['revenue'].describe().apply(lambda x: f"{x:,.0f}"))

    return valid_df

# 2. 数据预处理（调整单位，匹配图2分布）
def preprocess_data(valid_df):
    # 特征：budget（单位转换为1e8，匹配x轴）
    # 目标：revenue（转换为1e9美元，匹配y轴）
    X = valid_df[['budget']] / 1e8  # 预算除以1e8，使x轴范围接近0-4
    y = valid_df['revenue'] / 1e9    # 票房除以1e9，匹配y轴

    # 划分训练集和测试集（8:2）
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test, X  # 返回原始X用于可视化


# 3. 模型训练（随机森林回归）
def train_model(X_train, y_train):
    rf = RandomForestRegressor(n_estimators=1000, random_state=42)
    rf.fit(X_train, y_train)
    print(f"\n随机森林回归模型（1000棵树）训练完成")
    return rf

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


# 5. 可视化（匹配图2样式）
def visualize(X, y, model):
    plt.rcParams["font.family"] = ["Arial", "Microsoft YaHei", "sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False

    plt.figure(figsize=(10, 6))

    plt.scatter(X, y, alpha=0.6, color='green', s=15)

    # 关键修改：将X_sorted转换为带特征名称的DataFrame
    X_sorted = pd.DataFrame(np.sort(X, axis=0), columns=X.columns)
    y_pred_sorted = model.predict(X_sorted)
    plt.plot(X_sorted, y_pred_sorted, color='black', linewidth=1.5)

    plt.xlabel('theatrical', fontsize=12)
    plt.ylabel('revenue', fontsize=12)
    plt.title('Link between theatrical and revenue', fontsize=14)

    plt.xlim(-0.5, 4.0)
    plt.ylim(-0.5, 2.0)
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.text(4.05, -0.05, '1e8', fontsize=10)
    plt.text(-0.45, 2.05, '1e9', fontsize=10)

    plt.savefig('image.png', dpi=300, bbox_inches='tight')
    print("\n可视化结果已保存为image.png")
    plt.show()

# 主函数
def main():
    valid_df = load_and_analyze()
    X_train, X_test, y_train, y_test, X_original = preprocess_data(valid_df)
    model = train_model(X_train, y_train)
    y_pred = evaluate_model(model, X_test, y_test)
    visualize(X_original, valid_df['revenue'] / 1e9, model)

if __name__ == "__main__":
    main()