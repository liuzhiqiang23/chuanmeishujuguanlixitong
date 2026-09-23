import { post, get } from '@/utils/request'

// 票房预测：单片 / 批量 / 留痕查询 / 算法对比（契约见 docs/04_系统详细设计.md §5.2）
export default {
  predict: query => post('/api/predict', query),
  batch: query => post('/api/predict/batch', query),
  logs: query => post('/api/predict/logs', query),
  algoCompare: () => get('/api/predict/algo-compare')
}
