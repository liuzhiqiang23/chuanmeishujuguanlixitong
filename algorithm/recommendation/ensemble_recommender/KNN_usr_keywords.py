#-*-coding:utf-8-*-

import pandas as pd
import numpy as np
import os
from surprise import Reader, Dataset, SVD, model_selection, accuracy
from surprise import KNNBaseline
from surprise import KNNWithMeans
from surprise import KNNBasic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import sys

sys.path.insert(0, '..')
from personal_recommender.KNN_movie import Movie_KNN_recommender
from personal_recommender.KNN_user import Personal_KNN_recommender
from personal_recommender.Personal_SVD import Personal_SVD_recommender

SYSTEM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # 系统工程根目录 movie-system/
DATA_DIR = os.path.join(SYSTEM_ROOT, "data", "recommendation")  # 统一数据目录


# 首先用KNN对输入的用户进行相似度匹配，然后挑选出最接近的10个其他用户
# 之后对于选出的电影，根据与用户给出的关键词提取词向量，由相似度推荐靠前的十部电影
# 接受的输入为用户ID以及关键词什么的

class KNN_usr_keywords_ensemble:
    def __init__(self, mode=0):
        personal_data = os.path.join(DATA_DIR, "personal")

        # 【修复】实例化用户协同过滤对象，之前丢失此行！
        print("正在加载用户KNN协同过滤模型...")
        self.user = Personal_KNN_recommender()

        self.map = pd.read_csv(os.path.join(personal_data, "links.csv"))
        self.index = pd.read_csv(os.path.join(personal_data, "movies.csv"))
        self.reader = Reader()
        self.ratings = pd.read_csv(os.path.join(personal_data, "ratings.csv"))

        data = Dataset.load_from_df(self.ratings[['userId', 'movieId', 'rating']], self.reader)
        trainset = data.build_full_trainset()
        sim_options = {'name': 'pearson_baseline', 'user_based': False}
        if mode == 0:
            self.algo = KNNBaseline(sim_options=sim_options)
        elif mode == 1:
            self.algo = KNNWithMeans(sim_options=sim_options)
        elif mode == 2:
            self.algo = KNNBasic(sim_options=sim_options)
        else:
            exit(0)
        self.algo.fit(trainset)
        print("集成模型初始化完成")

    def showSeenMovies(self, usrID):
        print("\n\nThe user has seen movies below: ")
        movie_records = self.ratings[self.ratings['userId'] == usrID]
        for _, row in movie_records.iterrows():
            title_df = self.index[self.index.movieId == row['movieId']]
            if not title_df.empty:
                print(title_df['title'].values[0])

    def handle_keywords(self, keywords):
        tmdb_path = os.path.join(DATA_DIR, "tmdb_5000_movies.csv")
        self.movies = pd.read_csv(tmdb_path)
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.search_id = self.movies['overview'].shape[0]

        self.overview = self.movies['overview'].fillna('').copy()
        new_row = pd.Series([keywords])
        self.overview = pd.concat([self.overview, new_row], ignore_index=True)
        tfidf_matrix = self.tfidf.fit_transform(self.overview)
        self.cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        # 【修复】必须按 index(电影标题) 去重，而非默认按值去重，
        # 否则重名电影会令 self.indices[title] 返回多个索引(数组)
        self.indices = pd.Series(self.movies.index, index=self.movies['title'])
        self.indices = self.indices[~self.indices.index.duplicated(keep='first')]

    def convert_id2tmdbid(self, idlist):
        ids = []
        for mid in idlist:
            res = self.map[self.map['movieId'] == mid]['tmdbId']
            if not res.empty and pd.notna(res.values[0]):
                ids.append(int(res.values[0]))
        return ids

    def convert_id2title(self, idlist):
        titles = []
        for tid in idlist:
            df = self.movies[self.movies['id'] == tid]
            if not df.empty:
                titles.append(df['title'])
        return titles

    def cal_similarity(self, titles):
        similarity = {}
        for title_series in titles:
            temp = title_series.to_dict().values()
            temp_list = list(temp)
            if len(temp_list) == 0:
                print("skip empty title")
                continue
            temp0 = temp_list[0]
            if temp0 not in self.indices:
                continue
            idx = self.indices[temp0]
            sim_val = self.cosine_sim[idx, self.search_id]
            # 【修复】防御：万一 idx 仍为数组(如索引异常)，取最大值转标量，
            # 避免 sorted 比较 numpy 数组时报错
            if isinstance(sim_val, np.ndarray):
                sim_val = float(np.max(sim_val)) if sim_val.size else 0.0
            else:
                sim_val = float(sim_val)
            similarity[temp0] = sim_val
        return similarity

    def recommend(self, usrID, keywords, num=10):
        self.handle_keywords(keywords)
        self.showSeenMovies(usrID)
        print("\n\nThe user input the keywords: ")
        print(keywords)
        _, first_ids = self.user.recommend(usrID, 50)

        if len(first_ids) == 0:
            print("警告：没有得到候选电影ID")
            return []

        tmdb_id = self.convert_id2tmdbid(first_ids)
        if len(tmdb_id) == 0:
            print("警告：没有匹配到tmdbId")
            return []

        titles = self.convert_id2title(tmdb_id)
        similarity = self.cal_similarity(titles)
        result = sorted(similarity.items(), key=lambda x: x[1], reverse=True)
        result = result[:num]
        return result


if __name__ == "__main__":
    test = KNN_usr_keywords_ensemble()
    result = test.recommend(1,'spy hit strike hero war death soldier army')
    print("\n=====推荐结果(电影名,相似度)=====")
    if len(result) ==0:
        print("无推荐结果")
    for item in result:
        print(item)
