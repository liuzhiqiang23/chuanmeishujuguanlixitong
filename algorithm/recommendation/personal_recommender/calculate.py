import csv
import pandas as pd
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
# test.csv 在当前 personal_recommender 目录
test_path = os.path.join(base_dir, "test.csv")
# result.csv 在上层ensemble_recommender
result_path = os.path.join(base_dir, "..", "ensemble_recommender", "result.csv")

test = pd.read_csv(test_path)

usrid = []
movieid = []
for i in range(len(test['userId'])):
    if test['userId'][i] not in usrid:
        usrid.append(test['userId'][i])
    if test['movieId'][i] not in movieid:
        movieid.append(test['movieId'][i])

data_all = []
# 修复：按user分组获取该用户真实测试集电影列表，废弃原来index错位的while循环
for user in usrid:
    user_items = test[test["userId"] == user]["movieId"].tolist()
    data_all.append(user_items)
    print(f"user {user} test movies count: {len(user_items)}")

print('data all user count', len(data_all))

result = pd.read_csv(result_path)
print('pred user count', len(result['userId']))

posi = 0
neg = 0
for i in range(len(result['userId'])):
    temp = result['result'][i]
    # 去掉[]，分割转int
    temp = temp[1:-1].split(',')
    temp = [int(x.strip()) for x in temp]

    if i >= len(data_all):
        continue
    ground_truth = data_all[i]
    for mid in temp:
        if mid in ground_truth:
            posi += 1
        else:
            neg += 1

total = posi + neg
if total > 0:
    print(f"命中:{posi}, 未命中:{neg}, 准确率={posi / total:.4f}")
else:
    print("无统计数据")
