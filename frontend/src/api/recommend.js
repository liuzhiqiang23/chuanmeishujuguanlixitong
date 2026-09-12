import { post } from '@/utils/request'

export default {
  recommend: query => post('/api/recommend', query)
}
