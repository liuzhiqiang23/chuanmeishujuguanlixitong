import { post, get } from '@/utils/request'

// 影片库（新数据集 movie_analytics_db.t_movie 及其关联表）
export default {
  page: query => post('/api/movie/page', query),
  detail: id => get('/api/movie/detail/' + id),
  stats: () => get('/api/movie/stats')
}
