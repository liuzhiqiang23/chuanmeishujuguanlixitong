<template>
  <div class="app-container">
    <el-card shadow="never" class="mb16">
      <template #header>
        <div class="card-header">
          <span class="card-title">智能推荐</span>
          <el-tag size="small" type="success">基于新数据集的内容相似（类型 / 关键词 / 演职员 / 公司 / 国家加权）</el-tag>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-click="onTab">
        <!-- ---------- 策略 A：相似影片 ---------- -->
        <el-tab-pane label="按影片相似" name="similar">
          <el-form inline>
            <el-form-item label="参考影片">
              <el-select v-model="similar.movieId" filterable remote reserve-keyword
                         placeholder="输入片名搜索" :remote-method="searchMovies"
                         :loading="movieLoading" style="width:320px">
                <el-option v-for="m in movieOptions" :key="m.id"
                           :label="m.title + '（' + (m.year || '-') + '）'" :value="m.id"/>
              </el-select>
            </el-form-item>
            <el-form-item label="推荐数量">
              <el-select v-model="similar.topN" style="width:110px">
                <el-option v-for="n in [5, 10, 20]" :key="n" :label="n + ' 条'" :value="n"/>
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="runSimilar">生成推荐</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- ---------- 策略 B：类型热门 ---------- -->
        <el-tab-pane label="按类型热门" name="genre">
          <el-form inline>
            <el-form-item label="类型">
              <el-select v-model="genreHot.genre" placeholder="选择类型" style="width:220px">
                <el-option v-for="g in genres" :key="g.name" :label="g.name + '（' + g.count + ' 部）'" :value="g.name"/>
              </el-select>
            </el-form-item>
            <el-form-item label="推荐数量">
              <el-select v-model="genreHot.topN" style="width:110px">
                <el-option v-for="n in [5, 10, 20]" :key="n" :label="n + ' 条'" :value="n"/>
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="runGenreHot">生成推荐</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <el-alert type="info" :closable="false" show-icon class="mt8"
                title="推荐理由一并返回：命中的共同类型 / 共同关键词 / 同导演 / 同主演等；若当前登录用户在站内给影片打过分（t_rating），服务端会自动把高分影片的类型偏好作为加权项（数据不足时自动跳过）。" />
    </el-card>

    <div v-loading="loading" class="rec-grid">
      <div v-for="(item, idx) in items" :key="item.movieId" class="rec-card"
           @click="$router.push({ path: '/movie/detail', query: { id: item.movieId } })">
        <div class="rec-rank">{{ idx + 1 }}</div>
        <el-image :src="posterUrl(item.posterPath)" fit="cover" class="rec-poster" lazy>
          <template #error>
            <div class="rec-holder">无海报</div>
          </template>
        </el-image>
        <div class="rec-body">
          <div class="rec-name" :title="item.title">{{ item.title }}</div>
          <div class="rec-year">{{ item.year || '-' }}</div>
          <div class="rec-score">
            {{ isSimilar ? '相似度' : '热度分' }}
            <b>{{ fmtScore(item.score) }}</b>
          </div>
          <div class="rec-reasons">
            <el-tag v-for="r in (item.reasons || [])" :key="r" size="small" class="reason-tag">{{ r }}</el-tag>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && !items.length" class="empty-tip">
      选择参考影片或类型后点击「生成推荐」：相似影片来自新数据集的内容相似度计算，类型热门按热度与评分人数排序。
    </div>
  </div>
</template>

<script>
import recommendApi from '@/api/recommend'
import movieApi from '@/api/movie'
import { posterUrl } from '@/utils/media'

export default {
  name: 'RecommendIndex',
  data () {
    return {
      activeTab: 'similar',
      strategy: 'similar',
      loading: false,
      items: [],
      movieOptions: [],
      movieLoading: false,
      genres: [],
      similar: { movieId: null, topN: 10 },
      genreHot: { genre: '', topN: 10 }
    }
  },
  computed: {
    isSimilar () {
      return this.strategy !== 'genre_hot'
    }
  },
  created () {
    // 菜单两个入口分别落到两个策略页签（兼容既有路由 /recommend/UserList 与 /recommend/subject/edit）
    const mode = (this.$route.meta && this.$route.meta.mode) || 'user'
    this.activeTab = mode === 'video' ? 'genre' : 'similar'
    movieApi.stats().then(re => {
      this.genres = ((re.response || {}).genreTop || []).slice(0, 15)
    }).catch(() => {})
    // 从影片详情"看相似影片"跳过来时带 movieId，自动跑一次
    const mid = this.$route.query.movieId
    if (mid) {
      this.similar.movieId = Number(mid)
      this.activeTab = 'similar'
      this.searchMovies('')
      this.loadSeedOption(mid)
      this.runSimilar()
    }
  },
  methods: {
    posterUrl,
    /** 种子影片不一定在"热度前 20"里，单独查一次详情，让下拉框显示片名而不是 id */
    loadSeedOption (id) {
      movieApi.detail(id).then(re => {
        const m = re.response
        if (m && !this.movieOptions.some(o => o.id === m.id)) {
          this.movieOptions.unshift({ id: m.id, title: m.title, year: m.year })
        }
      }).catch(() => {})
    },
    onTab () {
      this.items = []
    },
    searchMovies (kw) {
      if (!kw) kw = ''
      this.movieLoading = true
      movieApi.page({ pageIndex: 1, pageSize: 20, keyword: kw, sortBy: 'popularity', sortOrder: 'desc' })
        .then(re => {
          this.movieOptions = ((re.response || {}).list || [])
          this.movieLoading = false
        }).catch(() => { this.movieLoading = false })
    },
    runSimilar () {
      if (!this.similar.movieId) {
        this.$message.warning('请先选择参考影片')
        return
      }
      this.call({ strategy: 'similar', movieId: this.similar.movieId, topN: this.similar.topN })
    },
    runGenreHot () {
      if (!this.genreHot.genre) {
        this.$message.warning('请先选择类型')
        return
      }
      this.call({ strategy: 'genre_hot', genre: this.genreHot.genre, topN: this.genreHot.topN })
    },
    call (q) {
      this.loading = true
      recommendApi.recommend(q).then(re => {
        const d = re.response || {}
        this.items = d.items || []
        this.strategy = d.strategy || q.strategy || 'similar'
        this.loading = false
      }).catch(() => { this.loading = false })
    },
    fmtScore (v) {
      if (v == null) return '-'
      // 相似度是 0~1 的余弦相似度，用百分比更直观；类型热门是 z 分数，保留两位小数
      return this.isSimilar ? (Number(v) * 100).toFixed(1) + '%' : Number(v).toFixed(2)
    }
  }
}
</script>

<style scoped>
.mb16 {
  margin-bottom: 16px;
}
.mt8 {
  margin-top: 8px;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-right: 8px;
}
.rec-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 16px;
  min-height: 120px;
}
.rec-card {
  position: relative;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow .2s, transform .2s;
}
.rec-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, .12);
  transform: translateY(-2px);
}
.rec-rank {
  position: absolute;
  left: 0;
  top: 0;
  z-index: 2;
  background: rgba(64, 158, 255, .92);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  padding: 2px 10px;
  border-bottom-right-radius: 6px;
}
.rec-poster {
  width: 100%;
  height: 260px;
  display: block;
  background: #f5f7fa;
}
.rec-holder {
  height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  font-size: 13px;
  background: #f5f7fa;
}
.rec-body {
  padding: 10px 12px 12px;
}
.rec-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rec-year {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}
.rec-score {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}
.rec-score b {
  color: #67c23a;
  font-size: 14px;
}
.rec-reasons {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.reason-tag {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}
.empty-tip {
  color: #909399;
  text-align: center;
  padding: 40px 0;
}
</style>
