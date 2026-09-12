<template>
  <div class="app-container">

    <el-form :model="form" ref="form" label-width="100px" v-loading="formLoading" :rules="rules">
      <el-form-item label="视频名字："  required>
        <el-input v-model="form.videoName"></el-input>
      </el-form-item>
      <el-form-item label="视频分类：" prop="videoCategory" required>
        <el-select v-model="form.videoCategory" placeholder="视频分类">
          <el-option v-for="item in categoryEnum" :key="item.key" :value="item.key" :label="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item :key="index" :label="'视频标签'+(index+1)+'：'" required v-for="(titleItem,index) in form.videoTagList">
        <el-input v-model="titleItem.tagName" style="width: 80%"/>
        <el-button type="text" class="link-left" size="small" @click="form.videoTagList.splice(index,1)">删除</el-button>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm">提交</el-button>
        <el-button @click="resetForm">重置</el-button>
        <el-button type="success" @click="addTitle">添加标签</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { mapGetters, mapState, mapActions } from 'vuex'
import videoApi from '@/api/video'

export default {
  data () {
    return {
      form: {
        videoId: null,
        videoCategory: null,
        videoUrl: '',
        videoName: '',
        videoTagList: []
      },
      formLoading: false,
      rules: {
        videoCategory: [
          { required: true, message: '请选择分类', trigger: 'change' }
        ]
      }
    }
  },
  created () {
    let id = this.$route.query.id
    let _this = this
    if (id && parseInt(id) !== 0) {
      _this.formLoading = true
      videoApi.getVideoDetailByVideoId(id).then(re => {
        _this.form = re.response
        _this.formLoading = false
      })
    }
  },
  methods: {
    submitForm () {
      let _this = this
      this.$refs.form.validate((valid) => {
        if (valid) {
          this.formLoading = true
          videoApi.editVideo(this.form).then(data => {
            if (data.code === 1) {
              _this.$message.success(data.message)
              _this.delCurrentView(_this).then(() => {
                _this.$router.push('/video/list')
              })
            } else {
              _this.$message.error(data.message)
              _this.formLoading = false
            }
          }).catch(e => {
            _this.formLoading = false
          })
        } else {
          return false
        }
      })
    },
    addTitle () {
      this.form.videoTagList.push({
        userTag: ''
      })
    },
    removeTitleItem (titleItem) {
      this.form.videoTagList.remove(titleItem)
    },
    resetForm () {
      this.$refs['form'].resetFields()
    },
    ...mapActions('tagsView', { delCurrentView: 'delCurrentView' })
  },
  computed: {
    ...mapGetters('enumItem', [
      'enumFormat'
    ]),
    ...mapState('enumItem', {
      categoryEnum: state => state.user.categoryEnum
    })
  }
}
</script>
