<template>
  <div class="app-container">
    <el-upload style="margin-left:14%;margin-top:5%"
      class="avatar-uploader el-upload--text"
      :drag="{Plus}"
      action="/api/admin/upload/uploadVidoe"
      multiple
      :show-file-list="false"
      :data="{SavePath: this.Path.url}"
      :on-success="handleVideoSuccess"
      :before-upload="beforeUploadVideo"
      :on-progress="uploadVideoProcess">
      <i v-if="Plus" class="el-icon-upload"></i>
      <div v-if="Plus" class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
      <el-progress v-if="videoFlag == true" type="circle" :percentage="videoUploadPercent" style="margin-top:30px;"></el-progress>
      <template #tip>
        <div class="el-upload__tip">只能上传mp4/flv/avi文件，且不超过300M</div>
      </template>
    </el-upload>
    <el-form :model="form" ref="form" label-width="100px" v-loading="formLoading" :rules="rules">
      <el-form-item label="视频文件名：" >
        <el-input v-model="form.videoFileName" :disabled="true"></el-input>
      </el-form-item>
            <el-form-item label="视频路径：" >
      <el-input v-model="form.videoUrl" :disabled="true"></el-input>
      </el-form-item>
            <el-form-item label="视频名：" >
        <el-input v-model="form.videoName" ></el-input>
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
        videoFileName: '',
        videoCategory: null,
        videoUrl: '',
        videoFilePath: '',
        videoName: '',
        videoTagList: []
      },
      formLoading: false,
      rules: {
        videoCategory: [
          { required: true, message: '请选择分类', trigger: 'change' }
        ]
      },
      videoForm: {
        videoId: '',
        videoUrl: ''
      },
      videoFlag: false,
      Plus: true,
      Path: {
        url: 'D:/video/videoUpload'
      },
      videoUploadPercent: 0
    }
  },
  created () {
    // let videoId = this.$route.query.videoId
    // let _this = this
  },
  mounted: function () {
  },
  methods: {
    submitForm () {
      let _this = this
      this.$refs.form.validate((valid) => {
        if (valid) {
          this.formLoading = true
          videoApi.createVideo(this.form).then(data => {
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
    // 视频上传前执行
    beforeUploadVideo (file) {
      const isLt300M = file.size / 1024 / 1024 < 300
      if (['video/mp4', 'video/ogg', 'video/flv', 'video/avi', 'video/wmv', 'video/rmvb'].indexOf(file.type) === -1) {
        this.$message.error('请上传正确的视频格式')
        return false
      }
      if (!isLt300M) {
        this.$message.error('上传视频大小不能超过300MB哦!')
        return false
      }
    },
    // 视频上传过程中执行
    uploadVideoProcess (event, file, fileList) {
      this.Plus = false
      this.videoFlag = true
      this.videoUploadPercent = file.percentage.toFixed(0)
    },
    // 视频上传成功是执行
    handleVideoSuccess (res, file) {
      this.Plus = false
      this.videoUploadPercent = 100
      console.log(res)
      // 如果为200代表视频保存成功
      if (res.resCode === '200') {
        // 接收视频传回来的名称和保存地址
        // 至于怎么使用看你啦~
        this.form.videoFileName = res.newVidoeName
        this.form.videoUrl = res.VideoUrl
        this.videoForm.videoId = res.newVidoeName
        this.form.videoUrl = res.VideoUrl
        this.$message.success('视频上传成功！')
      } else {
        this.$message.error('视频上传失败，请重新上传！')
      }
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
