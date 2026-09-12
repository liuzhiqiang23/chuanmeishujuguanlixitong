#-*-coding:utf-8-*-
# 在评分矩阵中使用kNN去度量用户之间的相似度

import pandas as pd
import numpy as np
import os
from surprise import Reader, Dataset, SVD, model_selection, accuracy
from surprise import KNNBaseline
from surprise import KNNWithMeans
from surprise import KNNBasic
import csv

SYSTEM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # 系统工程根目录 movie-system/
DATA_DIR = os.path.join(SYSTEM_ROOT, "data", "recommendation")  # 统一数据目录


class Personal_KNN_recommender:
    def __init__(self, mode=0):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # movies/train/test 统一放 data/recommendation/personal
        movies_path = os.path.join(DATA_DIR, "personal", "movies.csv")
        train_path = os.path.join(DATA_DIR, "personal", "train.csv")
        test_path = os.path.join(DATA_DIR, "personal", "test.csv")

        for fpath in [movies_path, train_path, test_path]:
            if not os.path.exists(fpath):
                raise FileNotFoundError(f"数据文件不存在：{fpath}\n提示：train.csv/test.csv需要先运行personal_recommender/test.py生成划分数据集")

        self.index = pd.read_csv(movies_path)
        self.reader = Reader()
        self.ratings = pd.read_csv(train_path)
        self.testings = pd.read_csv(test_path)

        data = Dataset.load_from_df(self.ratings[['userId', 'movieId', 'rating']], self.reader)
        trainset = data.build_full_trainset()
        sim_options = {'name': 'pearson_baseline', 'user_based': True}
        if mode == 0:
            self.algo = KNNBaseline(sim_options=sim_options)
        elif mode == 1:
            self.algo = KNNWithMeans(sim_options=sim_options)
        elif mode == 2:
            self.algo = KNNBasic(sim_options=sim_options)
        else:
            exit(0)
        self.userid = []
        for i in range(len(self.testings['userId'])):
            if not self.testings['userId'][i] in self.userid:
                self.userid.append(self.testings['userId'][i])
        self.algo.fit(trainset)


    def get_similar_users(self, usrID, num=10):
        user_inner_id = self.algo.trainset.to_inner_uid(usrID)
        user_neighbors = self.algo.get_neighbors(user_inner_id, k=num)
        user_neighbors = [self.algo.trainset.to_raw_uid(inner_id) for inner_id in user_neighbors]
        return user_neighbors


    def debug(self):
        similar_users = self.get_similar_users(1, 1)
        print(self.ratings[self.ratings.userId == 1].head())
        for i in similar_users:
            print(list(self.ratings[self.ratings.userId == i]['movieId']))


    def recommend(self, usrID, num=5):
        existed_movie = list(self.ratings[self.ratings.userId==usrID]['movieId'])
        similar_users = self.get_similar_users(usrID, num)
        movies_dict = {}
        for i in similar_users:
            movie = list(self.ratings[self.ratings.userId == i]['movieId'])
            vote = list(self.ratings[self.ratings.userId == i]['rating'])
            for j in range(len(vote)):
                if not (movie[j] in existed_movie):
                    if movie[j] in movies_dict.keys():
                        movies_dict[movie[j]] += vote[j]
                    else:
                        movies_dict[movie[j]] = vote[j]
        result = sorted(movies_dict.items(), key=lambda x: x[1], reverse=True)
        result = result[:num]
        recommending = []
        recommending_id = []
        for i in result:
            recommending.append(self.index[self.index.movieId==i[0]]['title'].values[0])
            recommending_id.append(i[0])
        return recommending, recommending_id


    def test(self, num = 10):
        result = []
        for user in self.userid:
            _, ids = self.recommend(user, num)
            result.append(ids)

        out_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result.csv")
        with open(out_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['userId', 'result'])
            for i,row in enumerate(result):
                writer.writerow([self.userid[i], row])
        print(f"测试输出结果保存至：{out_csv}")


if __name__ == "__main__":
    test = Personal_KNN_recommender()
    # result = test.recommend(6, 10)
    # for i in result:
    #     print(i)
    test.test(10)
