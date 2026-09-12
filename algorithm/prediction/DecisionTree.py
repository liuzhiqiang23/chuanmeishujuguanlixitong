import pandas as pd
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.tree import export_graphviz
import graphviz


# --------------------------
# 1. 数据加载与预处理（优化版）
# --------------------------
wine = load_wine()
df = pd.DataFrame(wine.data, columns=wine.feature_names)
df['target'] = wine.target
df['target_name'] = [wine.target_names[i] for i in wine.target]

print("===== 数据基本信息 =====")
df.info()
print("\n===== 数据前5行 =====")
print(df.head())
print("\n===== 数据统计描述 =====")
print(df.describe())

print("\n===== 缺失值统计 =====")
print(df.isnull().sum())
df = df.dropna()

X = df.drop(['target', 'target_name'], axis=1)
y = df['target']
print("\n===== 数据集维度 =====")
print(f"特征矩阵形状: {X.shape}, 目标变量形状: {y.shape}")


# --------------------------
# 2. 划分训练集和测试集（必须在模型训练前执行）
# --------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)


# --------------------------
# 3. 模型训练（优化：控制过拟合）
# --------------------------
clf = DecisionTreeClassifier(
    max_depth=5,
    min_samples_leaf=5,
    random_state=42
)
clf.fit(X_train, y_train)  # 现在X_train和y_train已定义


# --------------------------
# 4. 模型评估（优化：增加可读性）
# --------------------------
y_pred = clf.predict(X_test)

print("\n===== 模型评估结果 =====")
print(f"准确率: {accuracy_score(y_test, y_pred):.4f}")

print("\n分类报告（精确率/召回率/F1）:")
print(classification_report(
    y_test, y_pred,
    target_names=wine.target_names
))

print("混淆矩阵:")
conf_matrix = pd.DataFrame(
    confusion_matrix(y_test, y_pred),
    index=wine.target_names,
    columns=wine.target_names
)
print(conf_matrix)


# --------------------------
# 5. 决策树可视化（带箭头，每个子节点唯一父箭头）
# --------------------------
dot_data = export_graphviz(
    clf,
    out_file=None,
    feature_names=X.columns,
    class_names=wine.target_names,
    filled=True,
    rounded=True,
    special_characters=True,
    proportion=True
)

graph = graphviz.Source(dot_data)
graph.render("wine_decision_tree", format="png", cleanup=True)
print("\n决策树已保存为 'wine_decision_tree.png'，包含自动生成的箭头")
graph.view()


# --------------------------
# 6. 模型解释（新增：特征重要性分析）
# --------------------------
print("\n===== 特征重要性 =====")
feature_importance = pd.DataFrame({
    '特征名称': X.columns,
    '重要性': clf.feature_importances_
}).sort_values(by='重要性', ascending=False)
print(feature_importance)