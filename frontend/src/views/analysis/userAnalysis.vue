<template>
  <div class="app-container">
    <el-form :model="form" ref="form" label-width="100px" v-loading="formLoading" >
      <el-form-item :key="index" :label="'推荐视频'+(index+1)+'：'" required v-for="(titleItem,index) in form.videoRecommendList">
        <el-input v-model="titleItem.videoName" style="width: 80%"/>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import videoApi from '@/api/video'

export default {
  data () {
    return {
      form: {
        id: null,
        videoRecommendList: []
      },
      formLoading: false
    }
  },
  created () {
    let id = this.$route.query.id
    let _this = this
    if (id && parseInt(id) !== 0) {
      _this.formLoading = true
      videoApi.userAnalysis(id).then(re => {
        _this.form.videoRecommendList = (re.response && re.response.videoRecommendList) || []
        _this.formLoading = false
      }).catch(() => {
        _this.formLoading = false
      })
    }
  }
}
</script>
