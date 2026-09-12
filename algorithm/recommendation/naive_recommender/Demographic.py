# This function is for Demographic recommender.
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

SYSTEM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # 系统工程根目录 movie-system/
DATA_DIR = os.path.join(SYSTEM_ROOT, 'data', 'recommendation')  # 统一数据目录


# a general recommender method, not sensitive to the interests and tastes of a particular user
class Demographic_recommender:
    def __init__(self):
        df1 = pd.read_csv(os.path.join(DATA_DIR, 'tmdb_5000_credits.csv'))
        df2 = pd.read_csv(os.path.join(DATA_DIR, 'tmdb_5000_movies.csv'))
        df1.columns = ['id', 'tittle', 'cast', 'crew']
        df2 = df2.merge(df1, on='id')
        self.average_vote = df2['vote_average'].mean()
        self.average_count = df2['vote_count'].quantile(0.9)
        # choose more votes than at least 90% of the movies in the list
        self.movies = df2.copy().loc[df2['vote_count'] >= self.average_count]

    def weighted_rating(self, x):
        m = self.average_count
        c = self.average_vote
        v = x['vote_count']
        r = x['vote_average']
        # Calculation based on the IMDB formula
        return (v / (v + m) * r) + (m / (m + v) * c)

    def recommend(self, n=10):
        self.movies['score'] = self.movies.apply(self.weighted_rating, axis=1)
        self.movies = self.movies.sort_values('score', ascending=False)
        print('Using the Demographic recommending method, followings are the top %d score movies' % n)
        res_df = self.movies[['title', 'vote_count', 'vote_average', 'score']].head(n)
        print(res_df)
        return res_df


if __name__ == "__main__":
    # 实例化并调用
    test = Demographic_recommender()
    top10_df = test.recommend(n=10)

    # --------可选：绘制top10加权得分柱状图，输出图片 demographic_top10.png --------
    plt.figure(figsize=(11, 6))
    plt.barh(top10_df['title'], top10_df['score'])
    plt.xlabel("IMDB加权得分 weighted score")
    plt.title("Demographic 基于流行度的全局推荐 Top10")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig("demographic_top10.png")
    plt.show()
