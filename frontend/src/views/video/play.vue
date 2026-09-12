<template>
  <div class="app-container">
    <video v-if="playable" controls autoplay :src="form.videoUrl"/>
    <div v-else-if="!formLoading" class="no-video-tip">
      <p>该影片为元数据条目（用于推荐与分析），暂无可播放的视频文件。</p>
      <p>可播放的影片需先在「视频上传」中上传视频文件并关联。</p>
    </div>
  </div>
</template>
<script>
import videoApi from '@/api/video'
export default {
  data () {
    return {
      form: {
        videoId: null,
        userName: '',
        videoName: '',
        videoCategory: null,
        videoUrl: '',
        videoTagList: []
      },
      formLoading: false
    }
  },
  computed: {
    playable () {
      const u = this.form.videoUrl || ''
      return u !== '' && u.indexOf('/null') === -1
    }
  },
  created () {
    let id = this.$route.query.id
    let _this = this
    if (id && parseInt(id) !== 0) {
      _this.formLoading = true
      videoApi.selectVideo(id).then(re => {
        _this.form = re.response || {}
        _this.formLoading = false
      }).catch(() => {
        _this.formLoading = false
      })
    }
  }
}
</script>
<style scoped>
.no-video-tip {
  padding: 60px 20px;
  text-align: center;
  color: #5a7396;
  background: #f5f8fc;
  border: 1px dashed #c3d4e8;
  border-radius: 10px;
}
</style>
