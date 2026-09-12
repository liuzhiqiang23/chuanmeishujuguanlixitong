#-*-coding:utf-8-*-
# implement the Collaborative Filtering for recommending

import pandas as pd
import numpy as np
import os
from surprise import Reader, Dataset, SVD
from surprise.model_selection import cross_validate

SYSTEM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # 系统工程根目录 movie-system/
DATA_DIR = os.path.join(SYSTEM_ROOT, "data", "recommendation")  # 统一数据目录


class Personal_SVD_recommender:
    def __init__(self):
        # movies/train 统一放 data/recommendation/personal
        movies_path = os.path.join(DATA_DIR, "personal", "movies.csv")
        train_path = os.path.join(DATA_DIR, "personal", "train.csv")

        for fpath in [movies_path, train_path]:
            if not os.path.exists(fpath):
                raise FileNotFoundError(f"文件不存在：{fpath}\n提示：请先运行 test.py 生成 train.csv")

        self.reader = Reader()
        self.ratings = pd.read_csv(train_path)
        data = Dataset.load_from_df(self.ratings[['userId', 'movieId', 'rating']], self.reader)

        self.svd = SVD(n_epochs=20, n_factors=100, verbose=True)
        results = cross_validate(self.svd, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
        trainset = data.build_full_trainset()
        self.svd.fit(trainset)

        self.index = pd.read_csv(movies_path)

    def rating(self, usrID, movieID):
        rate = self.svd.predict(usrID, movieID)
        return rate.est

    def sample_movies(self, n):
        pass

    # 主要用于对给定的列表，进行用户模拟评分，之后进一步挑选，属于二阶步骤
    def recommend(self, usrID, movies, num=10):
        dic = {}
        for i in movies:
            dic[i] = self.rating(usrID, i)
        result = sorted(dic.items(), key=lambda x: x[1], reverse=True)
        result = result[:num]
        movie = []
        rates = []
        ids = []
        for i in result:
            title_series = self.index[self.index.movieId==i[0]]['title']
            movie.append(title_series.values[0])
            rates.append(i[1])
            ids.append(i[0])
        return movie, ids


if __name__ == "__main__":
    test = Personal_SVD_recommender()
    movie_names, movie_ids = test.recommend(2, [1,2,3,4,5,6,7,8,9,10,11,12,13,14])
    print("推荐电影名称：")
    print(movie_names)
    print("对应movieId：")
    print(movie_ids)
