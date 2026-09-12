import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.impute import SimpleImputer

SYSTEM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 系统工程根目录 movie-system/
DATA_DIR = os.path.join(SYSTEM_ROOT, 'data')  # 统一数据目录


# 1. 数据分析代码
def data_analysis(df):
    print('数据基本信息：')
    df.info()

    # Windows只保留SimHei，删除不存在字体，消除findfont警告
    plt.rcParams["font.family"] = ["SimHei"]
    plt.rcParams["axes.unicode_minus"] = False

    # 提取特征和目标变量
    features = df[['budget', 'popularity', 'runtime']]
    target = df['revenue']

    # 计算相关性并绘制热力图
    correlation_matrix = features.corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('特征间相关性热力图')
    plt.savefig('image.png')
    plt.show()

    return features, target


# 2. 数据预处理代码：增加缺失值填充，解决SVR不能接受NaN
def data_preprocessing(features, target):
    # 中位数填充缺失值
    imputer = SimpleImputer(strategy='median')
    features_fill = imputer.fit_transform(features)

    X_train, X_test, y_train, y_test = train_test_split(
        features_fill, target, test_size=0.2, random_state=42
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled, y_train, y_test


# 3. 模型训练代码
def train_model(X_train_scaled, y_train):
    svm_model = SVR(kernel='rbf')
    svm_model.fit(X_train_scaled, y_train)
    return svm_model


# 4. 模型评估代码
def evaluate_model(svm_model, X_test_scaled, y_test):
    y_pred = svm_model.predict(X_test_scaled)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f'均方误差 (MSE): {mse:.2f}')
    print(f'决定系数 (R2): {r2:.4f}')
    return y_pred


# 5. 结果可视化代码
def visualize_results(y_test, y_pred):
    plt.rcParams["font.family"] = ["SimHei"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.5)
    plt.xlabel('真实值')
    plt.ylabel('预测值')
    plt.title('SVM 模型预测结果可视化')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
    plt.show()


if __name__ == '__main__':
    df = pd.read_csv(os.path.join(DATA_DIR, 'train.csv'))
    features, target = data_analysis(df)
    X_train_scaled, X_test_scaled, y_train, y_test = data_preprocessing(features, target)
    svm_model = train_model(X_train_scaled, y_train)
    y_pred = evaluate_model(svm_model, X_test_scaled, y_test)
    visualize_results(y_test, y_pred)
