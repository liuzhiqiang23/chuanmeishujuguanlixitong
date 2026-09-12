#-*-coding:utf-8-*-

import pandas as pd
import sys
import os
import csv
sys.path.insert(0, '..')
from personal_recommender.KNN_movie import Movie_KNN_recommender
from personal_recommender.KNN_user import Personal_KNN_recommender
from personal_recommender.Personal_SVD import Personal_SVD_recommender

SYSTEM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # 系统工程根目录 movie-system/
DATA_DIR = os.path.join(SYSTEM_ROOT, 'data', 'recommendation')  # 统一数据目录

# 首先用KNN对输入的用户进行相似度匹配，然后挑选出最接近的10个其他用户
# 之后对于选出的电影，根据SVD计算用户对电影的模拟评分来进行排序

class KNN_SVD_ensemble:
    def __init__(self):
        self.user = Personal_KNN_recommender()
        self.movie = Personal_SVD_recommender()

    def _ensure_testings(self):
        # test.csv 仅在离线评测（test）时需要，初始化时不读取，避免缺少该文件导致服务不可用
        if not hasattr(self, "testings"):
            self.testings = pd.read_csv(os.path.join(DATA_DIR, 'personal', 'test.csv'))
            self.userid = []
            for i in range(len(self.testings['userId'])):
                if not self.testings['userId'][i] in self.userid:
                    self.userid.append(self.testings['userId'][i])

    def recommend(self, usrID, num=10):
        _, first_ids = self.user.recommend(usrID, 50)
        # print(first_ids)
        second_ids, movie_id = self.movie.recommend(usrID, first_ids, num)
        # print(second_ids)
        return movie_id

    def test(self, num):
        self._ensure_testings()
        result = []
        for user in self.userid:
            print(user)
            ids = self.recommend(user)
            print(ids)
            result.append(ids)

        with open("./result.csv", "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['userId', 'result'])
            for i, row in enumerate(result):
                writer.writerow([self.userid[i], row])


if __name__ == "__main__":
    test = KNN_SVD_ensemble()
    test.test(10)