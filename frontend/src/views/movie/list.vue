<template>
  <div class="app-container">
    <el-card shadow="never" class="filter-card">
      <el-form inline>
        <el-form-item label="关键词">
          <el-input v-model="query.keyword" placeholder="片名 / 原始片名" clearable style="width:200px"
                    @keyup.enter="search"/>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="query.genre" clearable placeholder="全部" style="width:170px">
            <el-option v-for="g in genres" :key="g.name" :label="g.name + '（' + g.count + '）'" :value="g.name"/>
          </el-select>
        </el-form-item>
        <el-form-item label="年份">
          <el-input-number v-model="query.yearFrom" :min="1880" :max="2030" :controls="false"
                           placeholder="起" style="width:90px"/>
          <span class="dash">—</span>
          <el-input-number v-model="query.yearTo" :min="1880" :max="2030" :controls="false"
                           placeholder="止" style="width:90px"/>
        </el-form-item>
        <el-form-item label="排序">
          <el-select v-model="query.sortBy" style="width:150px">
            <el-option label="热度 popularity" value="popularity"/>
            <el-option label="票房 revenue" value="revenue"/>
            <el-option label="评分人数 vote_count" value="vote_count"/>
            <el-option label="上映年份 year" value="year"/>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="search">检索</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>

      <div v-if="stats" class="stats-bar">
        <span>新数据集影片：<b>{{ stats.total }}</b> 部</span>
        <span>其中有票房记录：<b>{{ stats.withRevenue }}</b> 部</span>
        <span>年份跨度：<b>{{ (stats.yearRange || [])[0] }} – {{ (stats.yearRange || [])[1] }}</b></span>
        <span>当前筛选结果：<b>{{ total }}</b> 部</span>
      </div>
    </el-card>

    <div v-loading="loading" class="poster-grid">
      <div v-for="m in list" :key="m.id" class="poster-card" @click="goDetail(m.id)">
        <el-image :src="posterUrl(m.posterPath)" fit="cover" class="poster-img" lazy>
          <template #error>
            <div class="poster-holder">无海报</div>
          </template>
        </el-image>
        <div class="poster-body">
          <div class="poster-name" :title="m.title">{{ m.title }}</div>
          <div class="poster-sub">
            <span>{{ m.year || '-' }}</span>
            <span v-if="m.mainGenre" class="genre">{{ m.mainGenre }}</span>
          </div>
          <div class="poster-meta">
            <span>热度 {{ m.popularity == null ? '-' : Number(m.popularity).toFixed(1) }}</span>
            <span>评分 {{ m.voteAverage == null ? '-' : Number(m.voteAverage).toFixed(1) }}</span>
          </div>
          <div class="poster-revenue">
            <template v-if="m.revenue > 0">票房 {{ formatYi(m.revenue) }}</template>
            <template v-else><span class="no-revenue">测试集（无票房）</span></template>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && !list.length" class="empty-tip">没有符合条件的影片</div>

    <el-pagination
      v-if="total > 0"
      class="pager"
      background
      layout="total, sizes, prev, pager, next"
      :total="total"
      :current-page="query.pageIndex"
      :page-size="query.pageSize"
      :page-sizes="[12, 24, 48]"
      @current-change="onPage"
      @size-change="onSize"/>

    <el-alert type="info" :closable="false" show-icon class="mt12"
              title="影片数据来自新数据集（movie_analytics_db.t_movie）：5000 部训练集含票房、5000 部测试集无票房；海报取自 TMDB 图片 CDN。" />
  </div>
</template>

<script>
import movieApi from '@/api/movie'
import { posterUrl, formatYi } from '@/utils/media'

export default {
  name: 'MovieList',
  data () {
    return {
      loading: false,
      list: [],
      total: 0,
      stats: null,
      genres: [],
      query: {
        pageIndex: 1,
        pageSize: 12,
        keyword: '',
        genre: '',
        yearFrom: undefined,
        yearTo: undefined,
        sortBy: 'popularity',
        sortOrder: 'desc'
      }
    }
  },
  created () {
    this.loadStats()
    this.load()
  },
  methods: {
    posterUrl,
    formatYi,
    loadStats () {
      movieApi.stats().then(re => {
        const d = re.response || {}
        this.stats = d
        this.genres = (d.genreTop || []).slice(0, 15)
      }).catch(() => {})
    },
    load () {
      this.loading = true
      movieApi.page(this.query).then(re => {
        const d = re.response || {}
        this.list = d.list || []
        this.total = d.total || 0
        this.loading = false
      }).catch(() => { this.loading = false })
    },
    search () {
      this.query.pageIndex = 1
      this.load()
    },
    reset () {
      this.query.keyword = ''
      this.query.genre = ''
      this.query.yearFrom = undefined
      this.query.yearTo = undefined
      this.query.sortBy = 'popularity'
      this.search()
    },
    onPage (p) {
      this.query.pageIndex = p
      this.load()
    },
    onSize (s) {
      this.query.pageSize = s
      this.search()
    },
    goDetail (id) {
      this.$router.push({ path: '/movie/detail', query: { id } })
    }
  }
}
</script>

<style scoped>
.filter-card {
  margin-bottom: 16px;
}
.dash {
  margin: 0 6px;
  color: #909399;
}
.stats-bar {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  color: #606266;
  font-size: 13px;
  border-top: 1px dashed #ebeef5;
  padding-top: 12px;
}
.stats-bar b {
  color: #409eff;
}
.poster-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 16px;
  min-height: 200px;
}
.poster-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow .2s, transform .2s;
}
.poster-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, .12);
  transform: translateY(-2px);
}
.poster-img {
  width: 100%;
  height: 270px;
  display: block;
  background: #f5f7fa;
}
.poster-holder {
  height: 270px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  font-size: 13px;
  background: #f5f7fa;
}
.poster-body {
  padding: 10px 12px 12px;
}
.poster-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.poster-sub {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 8px;
  align-items: center;
}
.genre {
  background: #ecf5ff;
  color: #409eff;
  border-radius: 3px;
  padding: 0 6px;
}
.poster-meta {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 10px;
}
.poster-revenue {
  margin-top: 6px;
  font-size: 12px;
  color: #f56c6c;
  font-weight: 600;
}
.no-revenue {
  color: #c0c4cc;
  font-weight: 400;
}
.pager {
  margin-top: 16px;
  text-align: right;
}
.empty-tip {
  color: #909399;
  text-align: center;
  padding: 40px 0;
}
.mt12 {
  margin-top: 12px;
}
</style>
