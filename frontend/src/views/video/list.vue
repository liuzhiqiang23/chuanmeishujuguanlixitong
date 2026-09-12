<template>
  <div class="app-container">
    <el-form :model="queryParam" ref="queryForm" :inline="true">
      <el-form-item label="视频名：">
        <el-input v-model="queryParam.videoName"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm">查询</el-button>
      </el-form-item>
    </el-form>

    <el-table v-loading="listLoading" :data="tableData" border fit highlight-current-row style="width: 100%">
      <el-table-column width="90px" label="海报">
        <template #default="{row}">
          <el-image style="width:56px;height:84px;border-radius:6px;display:block" fit="cover"
                    :src="'/posters/' + row.videoId + '.jpg'"
                    :preview-src-list="['/posters/' + row.videoId + '.jpg']"
                    hide-on-click-modal preview-teleported>
            <template #error>
              <img :src="'/posters/placeholder.svg'" style="width:56px;height:84px;border-radius:6px;display:block" />
            </template>
          </el-image>
        </template>
      </el-table-column>
      <el-table-column width="80px" prop="videoId" label="videoId" />
      <!-- <el-table-column width="100px" prop="userName" label="用户名"/> -->
      <el-table-column width="200px" prop="videoName" label="视频名字"/>
      <el-table-column width="100px" prop="videoCategory" label="视频分类"  :formatter="categoryFormatter"/>
      <el-table-column width="120px" prop="budget" label="预算" />
      <el-table-column width="120px" prop="revenue" label="票房" />
      <el-table-column width="100px" prop="popularity" label="受欢迎度" />
      <el-table-column width="80px" prop="voteAverage" label="评分" />
      <el-table-column width="160px" prop="createTime" label="创建时间" />
      <el-table-column  prop="videoUrl" label="地址" />
      <el-table-column width="350px" label="操作" align="center">
        <template #default="{row}">
          <router-link :to="{path:'/video/edit', query:{id:row.videoId}}" class="link-left">
            <el-button size="small" >编辑</el-button>
          </router-link>
          <router-link :to="{path:'/video/details', query:{id:row.videoId}}" class="link-left">
            <el-button size="small" >详情</el-button>
          </router-link>
          <router-link :to="{path:'/video/play', query:{id:row.videoId}}" class="link-left">
            <el-button size="small" >播放</el-button>
          </router-link>
          <el-button  size="small" type="danger" @click="deleteVideo(row)" class="link-left">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" v-model:page="queryParam.pageIndex" v-model:limit="queryParam.pageSize"
                @pagination="search"/>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex'
import Pagination from '@/components/Pagination'
import videoApi from '@/api/video'

export default {
  components: { Pagination },
  data () {
    return {
      queryParam: {
        videoName: '',
        role: 1,
        pageIndex: 1,
        pageSize: 10
      },
      listLoading: true,
      tableData: [],
      total: 0
    }
  },
  created () {
    this.search()
  },
  methods: {
    search () {
      this.listLoading = true
      videoApi.getVideoPageList(this.queryParam).then(data => {
        const re = data.response
        this.tableData = re.list
        this.total = re.total
        this.queryParam.pageIndex = re.pageNum
        this.listLoading = false
      })
    },
    deleteVideo (row) {
      let _this = this
      videoApi.deleteVideo(row.videoId).then(re => {
        if (re.code === 1) {
          _this.search()
          _this.$message.success(re.message)
        } else {
          _this.$message.error(re.message)
        }
      })
    },
    submitForm () {
      this.queryParam.pageIndex = 1
      this.search()
    },
    categoryFormatter  (row, column, cellValue, index) {
      return this.enumFormat(this.categoryEnum, cellValue)
    }
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
