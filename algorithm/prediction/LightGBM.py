# 1. 导入依赖库
import os
import pandas as pd
import numpy as np
import lightgbm as lgb
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import LabelEncoder
import warnings

SYSTEM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 系统工程根目录 movie-system/
DATA_DIR = os.path.join(SYSTEM_ROOT, 'data')  # 统一数据目录

warnings.filterwarnings('ignore')  # 忽略警告


# 2. 数据分析代码（探索数据特征、分布、缺失值等）
def analyze_data(df):
    """数据探索分析：输出基本信息、统计特征、缺失值、关键特征分布"""
    print("=" * 50)
    print("1. 数据基本信息")
    print("=" * 50)
    df.info()  # 数据类型、非空值数量

    print("\n" + "=" * 50)
    print("2. 数值型特征统计描述")
    print("=" * 50)
    print(df.describe().round(2))  # 均值、标准差、分位数等

    print("\n" + "=" * 50)
    print("3. 缺失值统计（按列）")
    print("=" * 50)
    missing_info = df.isnull().sum().sort_values(ascending=False)
    missing_rate = (missing_info / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        "缺失数量": missing_info,
        "缺失率(%)": missing_rate
    }).query("缺失数量 > 0")
    print(missing_df if not missing_df.empty else "无缺失值")

    print("\n" + "=" * 50)
    print("4. 目标变量（票房revenue）分布")
    print("=" * 50)
    print(f"票房均值：{df['revenue'].mean():.2f}")
    print(f"票房中位数：{df['revenue'].median():.2f}")
    print(f"票房最大值：{df['revenue'].max():.2f}")
    print(f"票房最小值：{df['revenue'].min():.2f}")

    print("\n" + "=" * 50)
    print("5. 电影语言（original_language）分布")
    print("=" * 50)
    lang_count = df['original_language'].value_counts()
    print(lang_count.head(10))  # 输出前10种语言的电影数量


# 3. 数据预处理代码（缺失值处理、特征编码、特征筛选）
def preprocess_data(df):
    """数据预处理：处理缺失值、编码类别特征、筛选有效特征"""
    # 3.1 筛选核心特征（排除无关列，保留对票房有影响的特征）
    useful_features = [
        'original_language', 'budget', 'popularity', 'runtime',
        'status', 'revenue'  # revenue为目标变量
    ]
    df_processed = df[useful_features].copy()

    # 3.2 处理缺失值
    # - 数值型特征：用中位数填充（避免异常值影响）
    numeric_cols = ['budget', 'popularity', 'runtime']
    for col in numeric_cols:
        df_processed[col].fillna(df_processed[col].median(), inplace=True)

    # - 类别特征：用最频繁值填充
    cat_cols = ['original_language', 'status']
    for col in cat_cols:
        df_processed[col].fillna(df_processed[col].mode()[0], inplace=True)

    # 3.3 类别特征编码（LightGBM支持类别特征，但编码后更稳定）
    # - 电影语言编码（保留原始映射关系，用于后续可视化）
    lang_encoder = LabelEncoder()
    df_processed['original_language_encoded'] = lang_encoder.fit_transform(
        df_processed['original_language']
    )

    # - 电影状态编码（如"Released"编码为1，其他为0）
    status_encoder = LabelEncoder()
    df_processed['status_encoded'] = status_encoder.fit_transform(
        df_processed['status']
    )

    # 3.4 特征与目标变量分离
    X = df_processed.drop(['revenue', 'original_language', 'status'], axis=1)  # 特征（排除原始类别列）
    y = df_processed['revenue']  # 目标变量（票房）

    # 3.5 划分训练集与测试集（8:2，固定随机种子确保可复现）
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 返回预处理结果（含编码器，用于后续语言标签还原）
    return (X_train, X_test, y_train, y_test,
            lang_encoder, df_processed[['original_language', 'original_language_encoded']])


# 4. LightGBM模型训练代码
def train_lgb_model(X_train, X_test, y_train, y_test):
    """训练LightGBM回归模型（预测票房）"""
    # 构建LightGBM专用数据集
    lgb_train = lgb.Dataset(X_train, label=y_train, free_raw_data=False)
    lgb_test = lgb.Dataset(X_test, label=y_test, reference=lgb_train, free_raw_data=False)

    # 设置模型参数
    params = {
        "objective": "regression",
        "metric": "rmse",
        "boosting_type": "gbdt",
        "learning_rate": 0.05,
        "num_leaves": 31,
        "max_depth": -1,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "verbose": 0
    }

    # 训练模型（移除early_stopping_rounds，通过valid_sets和num_boost_round配合实现早停逻辑）
    model = lgb.train(
        params,
        train_set=lgb_train,
        num_boost_round=1000,
        valid_sets=[lgb_test]  # 验证集
        #verbose_eval=10  # 每10轮输出一次验证集指标
    )

    # 输出特征重要性
    print("\n" + "=" * 50)
    print("模型特征重要性")
    print("=" * 50)
    feature_importance = pd.DataFrame({
        "特征": X_train.columns,
        "重要性": model.feature_importance()  # 修改为 feature_importance()
    }).sort_values("重要性", ascending=False)
    print(feature_importance)

    return model

# 5. 模型评估代码（多指标评估预测效果）
def evaluate_model(model, X_test, y_test):
    """评估模型性能：RMSE、MAE、R²"""
    # 5.1 测试集预测
    y_pred = model.predict(X_test, num_iteration=model.best_iteration)  # 使用早停后的最优迭代次数

    # 5.2 计算评估指标
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))  # 均方根误差（越小越好）
    mae = mean_absolute_error(y_test, y_pred)  # 平均绝对误差（越小越好）
    r2 = r2_score(y_test, y_pred)  # 决定系数（越接近1越好）

    # 5.3 输出评估结果
    print("\n" + "=" * 50)
    print("模型评估结果（测试集）")
    print("=" * 50)
    print(f"RMSE（均方根误差）：{rmse:.2f}")
    print(f"MAE（平均绝对误差）：{mae:.2f}")
    print(f"R²（决定系数）：{r2:.4f}")

    return y_pred  # 返回预测值，用于后续可视化对比


# 6. 可视化代码（生成“电影语言-票房分布箱线图”）
def plot_lang_revenue_boxplot(X_test, y_test, y_pred, lang_encoder, lang_mapping_df):
    """绘制电影原始语言与票房的箱线图（与目标图一致）"""
    # 6.1 还原测试集的电影语言标签（从编码值映射回原始语言代码）
    X_test_with_lang = X_test.copy()
    # 合并语言编码与原始标签的映射关系
    lang_mapping = lang_mapping_df.drop_duplicates().set_index('original_language_encoded')[
        'original_language'].to_dict()
    X_test_with_lang['original_language'] = X_test_with_lang['original_language_encoded'].map(lang_mapping)

    # 6.2 合并真实票房与预测票房（可选：可同时展示真实/预测分布）
    plot_df = X_test_with_lang[['original_language']].copy()
    plot_df['revenue_true'] = y_test.values  # 真实票房
    plot_df['revenue_pred'] = y_pred  # 预测票房（可选展示）

    # 6.3 筛选样本量≥3的语言（避免单一样本导致箱线图无意义）
    lang_sample_count = plot_df['original_language'].value_counts()
    valid_langs = lang_sample_count[lang_sample_count >= 3].index
    plot_df = plot_df[plot_df['original_language'].isin(valid_langs)]

    # 6.4 绘制箱线图（适配票房长尾分布，用对数刻度）
    plt.figure(figsize=(12, 8))  # 图大小与目标图匹配
    sns.boxplot(
        x='original_language',
        y='revenue_true',
        data=plot_df,
        palette='Set2',  # 配色方案
        showfliers=True  # 显示异常值（票房中的高收入电影）
    )

    # 6.5 图表美化（与目标图标题、轴标签一致）
    plt.title('Revenue by original language\'s movies', fontsize=16, pad=20)
    plt.xlabel('Original language', fontsize=12, labelpad=10)
    plt.ylabel('Revenue', fontsize=12, labelpad=10)
    plt.yscale('symlog')  # 对称对数刻度（适配票房长尾分布，避免高收入电影掩盖其他分布）
    plt.xticks(rotation=45)  # 语言标签旋转45度，避免重叠
    plt.grid(axis='y', alpha=0.3)  # 纵轴网格线，便于读取数值
    plt.tight_layout()  # 自动调整布局，防止标签截断
    plt.show()


# 7. 主函数（串联所有流程）
def main():
    # 7.1 读取数据（train.csv 位于 data 目录下，需在项目根目录运行）
    print("正在读取数据...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'train.csv'))

    # 7.2 数据分析
    analyze_data(df)

    # 7.3 数据预处理
    print("\n" + "=" * 50)
    print("开始数据预处理...")
    X_train, X_test, y_train, y_test, lang_encoder, lang_mapping_df = preprocess_data(df)
    print("数据预处理完成！")

    # 7.4 模型训练
    print("\n" + "=" * 50)
    print("开始训练LightGBM模型...")
    model = train_lgb_model(X_train, X_test, y_train, y_test)
    print("模型训练完成！")

    # 7.5 模型评估
    y_pred = evaluate_model(model, X_test, y_test)

    # 7.6 生成可视化图表（电影语言-票房箱线图）
    print("\n" + "=" * 50)
    print("生成票房分布箱线图...")
    plot_lang_revenue_boxplot(X_test, y_test, y_pred, lang_encoder, lang_mapping_df)


# 8. 执行主函数
if __name__ == "__main__":
    main()