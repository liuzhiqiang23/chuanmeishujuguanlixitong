import { post } from '@/utils/request'

export default {
  predict: query => post('/api/predict', query)
}
