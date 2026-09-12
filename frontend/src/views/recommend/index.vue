<template>
  <div class="app-container">
    <el-alert type="primary" :closable="false" show-icon class="mode-tip" :title="modeTip"/>

    <el-form :inline="true">
      <el-form-item label="推荐算法">
        <el-select v-model="query.algo" style="width:300px">
          <el-option v-for="a in algos" :key="a.value" :label="a.label" :value="a.value"/>
        </el-select>
      </el-form-item>
      <el-form-item v-if="mode === 'user'" label="用户ID">
        <el-input v-model="query.userId" placeholder="如 11（=MovieLens 用户1）" style="width:150px"/>
      </el-form-item>
      <el-form-item v-if="needMovie" label="电影名">
        <el-input v-model="query.movieTitle" placeholder="如 The Dark Knight" style="width:220px"/>
      </el-form-item>
      <el-form-item v-if="query.algo === 'usr_keywords'" label="关键词">
        <el-input v-model="query.keywords" placeholder="空格分隔，如 spy hero war army" style="width:220px"/>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="search">生成推荐</el-button>
      </el-form-item>
    </el-form>

    <el-alert type="info" :closable="false" show-icon class="algo-tip" :title="tipText"/>

    <el-table v-loading="loading" :data="list" border fit style="width:100%">
      <el-table-column prop="movieId" label="电影ID" width="120"/>
      <el-table-column prop="title" label="电影名称"/>
      <el-table-column prop="popularity" label="热度" width="100"/>
      <el-table-column prop="voteAverage" label="均分" width="90"/>
      <el-table-column prop="score" label="算法得分" width="120">
        <template v-slot="{ row }">{{ row.score === null || row.score === undefined ? '-' : Number(row.score).toFixed(4) }}</template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import recommendApi from '@/api/recommend'

// 按“用户属性 / 视频属性”划分的算法清单（与 Movie-Analysis-master/recommend_api.py 一一对应）
const USER_ALGOS = [
  { label: '① 人口统计热门（IMDB 加权）', value: 'demographic', user: false, movie: false },
  { label: '② 用户协同过滤 KNN', value: 'user_knn', user: true, movie: false },
  { label: '③ SVD 评分矩阵分解', value: 'svd', user: true, movie: false },
  { label: '④ 集成：用户KNN + SVD', value: 'knn_svd', user: true, movie: false },
  { label: '⑤ 集成：用户KNN + 关键词', value: 'usr_keywords', user: true, movie: false },
  { label: '⑥ 集成：用户KNN + 电影KNN', value: 'usr_movie_knn', user: true, movie: true }
]
const VIDEO_ALGOS = [
  { label: '① 基于电影简介（内容相似）', value: 'content', user: false, movie: true },
  { label: '② 基于电影关键词（TF-IDF）', value: 'keyword', user: false, movie: true },
  { label: '③ 电影相似度协同 KNN', value: 'movie_knn', user: false, movie: true }
]

export default {
  name: 'RecommendIndex',
  data () {
    return {
      query: { algo: '', userId: '11', movieTitle: 'The Dark Knight', keywords: '', top: 10 },
      list: [],
      loading: false
    }
  },
  computed: {
    // 由路由 meta.mode 区分：user=用户属性推荐 / video=视频属性推荐
    mode () {
      return this.$route.meta && this.$route.meta.mode === 'video' ? 'video' : 'user'
    },
    algos () {
      return this.mode === 'video' ? VIDEO_ALGOS : USER_ALGOS
    },
    currentAlgo () {
      return this.algos.find(a => a.value === this.query.algo)
    },
    needUser () {
      return !!(this.currentAlgo && this.currentAlgo.user)
    },
    needMovie () {
      return !!(this.currentAlgo && this.currentAlgo.movie)
    },
    modeTip () {
      if (this.mode === 'video') {
        return '本页为「视频属性推荐」：从某部电影/视频的内容属性出发（简介、关键词、协同相似度），找出与之相似的影片。只需提供电影名，无需用户ID。'
      }
      return '本页为「用户属性推荐」：从观影用户的属性与行为出发（热门兜底、相似用户、评分矩阵等），为该用户生成个性化推荐。请填写 MovieLens 用户ID（页面中 11 = MovieLens 用户1）。'
    },
    tipText () {
      const algo = this.query.algo
      if (algo.startsWith('usr_') || algo === 'knn_svd') {
        return '当前为集成/混合算法：先基于用户KNN生成候选电影，再结合第二种算法精排。服务端需训练多个协同过滤模型，耗时较长，请耐心等待。'
      }
      if (algo === 'user_knn' || algo === 'svd' || algo === 'movie_knn') {
        return '提示：该算法需在服务端训练协同过滤模型，耗时较长，请耐心等待。'
      }
      return 'demographic 为全局热门榜（无需用户ID），content/keyword 为基于电影内容的相似推荐。'
    }
  },
  watch: {
    '$route.meta.mode' () {
      this.query.algo = ''
      this.list = []
    }
  },
  mounted () {
    this.resetAlgo()
  },
  methods: {
    resetAlgo () {
      // 默认算法：用户模式=热门兜底；视频模式=内容相似
      this.query.algo = this.mode === 'video' ? 'content' : 'demographic'
      this.list = []
    },
    search () {
      const algo = this.query.algo
      if (!algo) {
        this.$message.warning('请先选择推荐算法')
        return
      }
      if (this.needUser && (this.query.userId === '' || this.query.userId == null)) {
        this.$message.error('算法「' + this.algoLabel(algo) + '」需要填写用户ID（如 11 = MovieLens 用户1）')
        return
      }
      if (this.needMovie && (this.query.movieTitle === '' || this.query.movieTitle == null)) {
        this.$message.error('算法「' + this.algoLabel(algo) + '」需要填写电影名（如 The Dark Knight）')
        return
      }
      if (algo === 'usr_keywords' && (this.query.keywords === '' || this.query.keywords == null)) {
        this.$message.error('算法「' + this.algoLabel(algo) + '」需要填写关键词（空格分隔，如 spy hero war army）')
        return
      }
      this.loading = true
      const q = { algo: algo, top: this.query.top }
      if (this.needUser) q.userId = Number(this.query.userId)
      if (this.needMovie) q.movieTitle = this.query.movieTitle.trim()
      if (algo === 'usr_keywords') q.keywords = this.query.keywords.trim()
      recommendApi.recommend(q).then(re => {
        this.list = re.response || []
        this.loading = false
      }).catch(() => { this.loading = false })
    },
    algoLabel (value) {
      const all = USER_ALGOS.concat(VIDEO_ALGOS)
      const hit = all.find(a => a.value === value)
      return hit ? hit.label : value
    }
  }
}
</script>

<style scoped>
.mode-tip {
  margin-bottom: 14px;
}
.algo-tip {
  margin-bottom: 12px;
}
</style>
