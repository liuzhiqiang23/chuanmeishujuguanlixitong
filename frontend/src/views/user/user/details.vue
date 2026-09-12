<template>
  <div class="app-container">

    <el-form :model="form" ref="form" label-width="100px" v-loading="formLoading" >
      <el-form-item label="用户名："  prop="userName" >
        <el-input v-model="form.userName" style="width: 80%"></el-input>
      </el-form-item>
      <el-form-item :key="index" :label="'用户喜好'+(index+1)+'：'" required v-for="(titleItem,index) in form.userTagList">
        <el-input v-model="titleItem.tagName" style="width: 80%"/>
      </el-form-item>
      <el-form-item :key="index" :label="'播放记录'+(index+1)+'：'" required v-for="(titleItem,index) in form.userPlayList">
        <el-input v-model="titleItem.videoName" style="width: 80%"/>
      </el-form-item>
      <el-form-item :key="index" :label="'视频操作'+(index+1)+'：'" required v-for="(titleItem,index) in form.userOperationList">
        <el-input v-model="titleItem.videoName" style="width: 80%"/>
      </el-form-item>
      <el-form-item :key="index" :label="'视频推荐'+(index+1)+'：'" required v-for="(titleItem,index) in form.userRecommendList">
        <el-input v-model="titleItem.title" style="width: 80%"/>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { mapGetters, mapState, mapActions } from 'vuex'
import userApi from '@/api/user'

export default {
  data () {
    return {
      form: {
        id: null,
        userName: '',
        userPlayList: [],
        userOperationList: [],
        userTagList: [],
        userRecommendList: [],
        subscription: null
      },
      formLoading: false
    }
  },
  created () {
    let id = this.$route.query.id
    let _this = this
    if (id && parseInt(id) !== 0) {
      _this.formLoading = true
      userApi.getUserDetailByUserId(id).then(re => {
        _this.form = re.response
        _this.formLoading = false
      })
    }
  },
  methods: {
    // submitForm () {
    //   let _this = this
    //   this.$refs.form.validate((valid) => {
    //     if (valid) {
    //       this.formLoading = true
    //       userApi.createUser(this.form).then(data => {
    //         if (data.code === 1) {
    //           _this.$message.success(data.message)
    //           _this.delCurrentView(_this).then(() => {
    //             _this.$router.push('/user/student/list')
    //           })
    //         } else {
    //           _this.$message.error(data.message)
    //           _this.formLoading = false
    //         }
    //       }).catch(e => {
    //         _this.formLoading = false
    //       })
    //     } else {
    //       return false
    //     }
    //   })
    // },
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
      sexEnum: state => state.user.sexEnum,
      roleEnum: state => state.user.roleEnum,
      statusEnum: state => state.user.statusEnum,
      levelEnum: state => state.user.levelEnum
    })
  }
}
</script>
