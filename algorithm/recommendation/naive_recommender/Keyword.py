import os
import pandas as pd
import numpy as np
from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SYSTEM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # 系统工程根目录 movie-system/
DATA_DIR = os.path.join(SYSTEM_ROOT, 'data', 'recommendation')  # 统一数据目录


class Keyword_recommender:
    def __init__(self):
        # 注意：如果运行报文件找不到，改成绝对路径
        df1 = pd.read_csv(os.path.join(DATA_DIR, 'tmdb_5000_credits.csv'))
        df2 = pd.read_csv(os.path.join(DATA_DIR, 'tmdb_5000_movies.csv'))
        df1.columns = ['id', 'tittle', 'cast', 'crew']
        self.movies = df2.merge(df1, on='id')
        features = ['cast', 'crew', 'keywords', 'genres']
        for feature in features:
            self.movies[feature] = self.movies[feature].apply(literal_eval)

        # 初始化就预处理，不要每次recommend都重复跑
        self.process_data()
        self.movies['soup'] = self.movies.apply(self.create_soup, axis=1)
        count = CountVectorizer(stop_words='english')
        count_matrix = count.fit_transform(self.movies['soup'])
        self.cosine_sim = cosine_similarity(count_matrix, count_matrix)
        self.movies = self.movies.reset_index()
        self.indices = pd.Series(self.movies.index, index=self.movies['title'])

    def get_director(self, x):
        for i in x:
            if i['job'] == 'Director':
                return i['name']
        return np.nan

    def get_list(self, x):
        if isinstance(x, list):
            names = [i['name'] for i in x]
            if len(names) > 3:
                names = names[:3]
            return names
        return []

    def clean_data(self, x):
        if isinstance(x, list):
            return [str.lower(i.replace(" ", "")) for i in x]
        else:
            if isinstance(x, str):
                return str.lower(x.replace(" ", ""))
            else:
                return ''

    def process_data(self):
        self.movies['director'] = self.movies['crew'].apply(self.get_director)
        features = ['cast', 'keywords', 'genres']
        for feature in features:
            self.movies[feature] = self.movies[feature].apply(self.get_list)
        features = ['cast', 'keywords', 'director', 'genres']
        for feature in features:
            self.movies[feature] = self.movies[feature].apply(self.clean_data)

    def create_soup(self, x):
        return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + x['director'] + ' ' + ' '.join(x['genres'])

    def recommend(self, title):
        idx = self.indices[title]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:11]
        movie_indices = [i[0] for i in sim_scores]
        return self.movies['title'].iloc[movie_indices]


if __name__ == "__main__":
    test = Keyword_recommender()
    res = test.recommend('The Dark Knight Rises')
    print("=====关键词组合特征推荐结果=====")
    print(res)
