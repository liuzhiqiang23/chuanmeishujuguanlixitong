<template>
  <div class="app-container" v-loading="loading">
    <el-card v-if="m" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">影片详情</span>
          <el-button size="small" type="primary" plain @click="goRecommend">看相似影片 →</el-button>
          <el-button size="small" @click="$router.back()">返回</el-button>
        </div>
      </template>

      <div class="detail-top">
        <el-image :src="posterUrl(m.posterPath)" fit="cover" class="detail-poster">
          <template #error>
            <div class="poster-holder">无海报</div>
          </template>
        </el-image>

        <div class="detail-info">
          <div class="title-line">
            <span class="title">{{ m.title }}</span>
            <span v-if="m.originalTitle && m.originalTitle !== m.title" class="subtitle">{{ m.originalTitle }}</span>
          </div>

          <div class="meta-grid">
            <div class="meta-item"><span class="k">年份</span><span class="v">{{ m.year || '-' }}</span></div>
            <div class="meta-item"><span class="k">片长</span><span class="v">{{ m.runtime ? m.runtime + ' 分钟' : '-' }}</span></div>
            <div class="meta-item"><span class="k">预算</span><span class="v">{{ formatMoney(m.budget) }}</span></div>
            <div class="meta-item"><span class="k">票房</span><span class="v revenue">{{ m.revenue > 0 ? formatMoney(m.revenue) : '（测试集，无票房）' }}</span></div>
            <div class="meta-item"><span class="k">热度</span><span class="v">{{ m.popularity == null ? '-' : Number(m.popularity).toFixed(1) }}</span></div>
            <div class="meta-item"><span class="k">评分 / 人数</span><span class="v">{{ m.voteAverage == null ? '-' : Number(m.voteAverage).toFixed(1) }} / {{ m.voteCount || 0 }}</span></div>
            <div class="meta-item"><span class="k">语言</span><span class="v">{{ m.originalLanguage || '-' }}</span></div>
            <div class="meta-item"><span class="k">系列片</span><span class="v">{{ m.isCollection ? '是' : '否' }}</span></div>
          </div>

          <div class="tag-row" v-if="(m.genres || []).length">
            <span class="tag-label">类型</span>
            <el-tag v-for="g in m.genres" :key="g" size="small" class="tag-item">{{ g }}</el-tag>
          </div>
          <div class="tag-row" v-if="(m.countries || []).length">
            <span class="tag-label">国家/地区</span>
            <el-tag v-for="c in m.countries" :key="c" size="small" type="info" class="tag-item">{{ c }}</el-tag>
          </div>
          <div class="tag-row" v-if="(m.companies || []).length">
            <span class="tag-label">制作公司</span>
            <el-tag v-for="c in m.companies" :key="c" size="small" type="warning" class="tag-item">{{ c }}</el-tag>
          </div>
          <div class="tag-row" v-if="(m.keywords || []).length">
            <span class="tag-label">关键词</span>
            <el-tag v-for="k in m.keywords" :key="k" size="small" type="success" class="tag-item">{{ k }}</el-tag>
          </div>

          <div class="overview" v-if="m.overview">{{ m.overview }}</div>
        </div>
      </div>

      <el-divider content-position="left">演职人员</el-divider>
      <div class="people">
        <div class="people-col">
          <div class="people-title">导演</div>
          <div class="people-list">
            <el-tag v-for="p in (m.director ? [m.director] : [])" :key="p" size="small">{{ p }}</el-tag>
            <span v-if="!m.director" class="muted">-</span>
          </div>
        </div>
        <div class="people-col">
          <div class="people-title">主演（前 10）</div>
          <div class="people-list">
            <el-tag v-for="p in (m.cast || [])" :key="p" size="small" type="info">{{ p }}</el-tag>
            <span v-if="!(m.cast || []).length" class="muted">-</span>
          </div>
        </div>
      </div>

      <el-divider content-position="left">票房预测记录（本站）</el-divider>
      <el-table :data="m.predictionLog || []" size="small" border fit>
        <el-table-column prop="modelName" label="模型" width="180"/>
        <el-table-column label="预测票房" width="180">
          <template #default="{ row }">{{ formatMoney(row.predictedRevenue) }}</template>
        </el-table-column>
        <el-table-column prop="createdAt" label="时间" width="200"/>
      </el-table>
      <div v-if="!(m.predictionLog || []).length" class="muted mt8">暂无预测记录</div>
    </el-card>

    <el-card v-else-if="!loading" shadow="never">
      <div class="muted">未找到该影片（id={{ $route.query.id }}）</div>
    </el-card>
  </div>
</template>

<script>
import movieApi from '@/api/movie'
import { posterUrl, formatMoney } from '@/utils/media'

export default {
  name: 'MovieDetail',
  data () {
    return { loading: false, m: null }
  },
  created () {
    this.load()
  },
  methods: {
    posterUrl,
    formatMoney,
    load () {
      const id = this.$route.query.id
      if (!id) return
      this.loading = true
      movieApi.detail(id).then(re => {
        this.m = re.response || null
        this.loading = false
      }).catch(() => { this.loading = false })
    },
    goRecommend () {
      this.$router.push({ path: '/recommend/UserList', query: { movieId: this.m.id } })
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-right: auto;
}
.detail-top {
  display: flex;
  gap: 24px;
}
.detail-poster {
  width: 240px;
  height: 350px;
  flex: 0 0 240px;
  border-radius: 6px;
  background: #f5f7fa;
}
.poster-holder {
  height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  font-size: 13px;
  background: #f5f7fa;
}
.detail-info {
  flex: 1;
  min-width: 0;
}
.title-line {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 14px;
}
.title {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
}
.subtitle {
  color: #909399;
  font-size: 14px;
}
.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 8px 20px;
  margin-bottom: 14px;
}
.meta-item {
  font-size: 13px;
}
.meta-item .k {
  color: #909399;
  margin-right: 8px;
}
.meta-item .v {
  color: #303133;
  font-weight: 500;
}
.meta-item .v.revenue {
  color: #f56c6c;
}
.tag-row {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.tag-label {
  color: #909399;
  font-size: 13px;
  line-height: 24px;
  flex: 0 0 68px;
}
.tag-item {
  margin-right: 4px;
}
.overview {
  margin-top: 12px;
  color: #606266;
  font-size: 13px;
  line-height: 1.9;
  background: #fafafa;
  padding: 12px;
  border-radius: 4px;
}
.people {
  display: flex;
  gap: 40px;
}
.people-col {
  flex: 1;
}
.people-title {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}
.people-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.muted {
  color: #c0c4cc;
  font-size: 13px;
}
.mt8 {
  margin-top: 8px;
}
</style>
