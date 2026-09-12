import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

SYSTEM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # 系统工程根目录 movie-system/
DATA_DIR = os.path.join(SYSTEM_ROOT, 'data', 'recommendation')  # 统一数据目录


class Content_recommender:
    def __init__(self):
        df1 = pd.read_csv(os.path.join(DATA_DIR, 'tmdb_5000_credits.csv'))
        df2 = pd.read_csv(os.path.join(DATA_DIR, 'tmdb_5000_movies.csv'))
        df1.columns = ['id', 'tittle', 'cast', 'crew']
        self.movies = df2.merge(df1, on='id')

        self.tfidf = TfidfVectorizer(stop_words='english')
        self.movies['overview'] = self.movies['overview'].fillna('')
        tfidf_matrix = self.tfidf.fit_transform(self.movies['overview'])
        self.cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        self.indices = pd.Series(self.movies.index, index=self.movies['title']).drop_duplicates()

    def recommend(self, title):
        idx = self.indices[title]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:11]
        movie_indices = [i[0] for i in sim_scores]
        return self.movies['title'].iloc[movie_indices]


if __name__ == "__main__":
    test = Content_recommender()
    res = test.recommend('The Dark Knight Rises')
    print("\n=====TF‑IDF简介内容推荐结果=====")
    print(res)
