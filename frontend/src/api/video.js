import { post } from '@/utils/request'

export default {
  getVideoPageList: query => post('/api/admin/video/page/list', query),
  createVideo: query => post('/api/admin/video/create', query),
  editVideo: query => post('/api/admin/video/edit', query),
  selectVideo: id => post('/api/admin/video/select/' + id),
  deleteVideo: id => post('/api/admin/video/delete/' + id),
  selectByVideoName: query => post('/api/admin/video/selectByVideoName', query),
  getVideoDetailByVideoId: id => post('/api/admin/video/getVideoDetailByVideoId/' + id),
  userAnalysis: id => post('/api/admin/video/userAnalysis/' + id)
}
