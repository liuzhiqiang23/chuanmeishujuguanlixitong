import { post } from '@/utils/request'

export default {
  overview: () => post('/api/admin/analysis/overview'),
  videoOverview: () => post('/api/admin/analysis/video-overview'),
  userOverview: () => post('/api/admin/analysis/user-overview')
}
