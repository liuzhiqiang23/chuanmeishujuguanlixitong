<template>
  <div class="app-container">
    <el-alert type="success" :closable="false" show-icon style="margin-bottom:14px"
              title="视频属性分析：统计电影/视频的内容属性（数据源 t_video_info，共 4808 部，来自 TMDB5000 影片库）。配套底层算法：LightGBM/RandomForest 等票房预测的特征正是取自这些视频属性（语言、预算、热度、时长等）。"/>

    <el-row :gutter="16" class="stat-row">
      <el-col :span="4" v-for="c in statCards" :key="c.label">
        <div class="stat-card">
          <div class="stat-num">{{ c.value }}</div>
          <div class="stat-label">{{ c.label }}</div>
        </div>
      </el-col>
    </el-row>

    <div class="chart-grid">
      <div class="chart-box">
        <div class="chart-title">电影类型分布（标签 TOP12）</div>
        <div ref="genreChart" class="chart"></div>
      </div>
      <div class="chart-box">
        <div class="chart-title">发行年份分布</div>
        <div ref="yearChart" class="chart"></div>
      </div>
      <div class="chart-box">
        <div class="chart-title">预算 - 票房散点关系（$）</div>
        <div ref="budgetChart" class="chart"></div>
      </div>
      <div class="chart-box">
        <div class="chart-title">影片时长分段分布</div>
        <div ref="runtimeChart" class="chart"></div>
      </div>
      <div class="chart-box">
        <div class="chart-title">主要语言分布 TOP10</div>
        <div ref="langChart" class="chart"></div>
      </div>
      <div class="chart-box">
        <div class="chart-title">票房 TOP10 影片</div>
        <el-table :data="topRevenue" size="small" height="340" border style="width:100%">
          <el-table-column prop="videoName" label="片名" min-width="150" show-overflow-tooltip/>
          <el-table-column label="票房($)" width="110">
            <template v-slot="{ row }">{{ fmtUsd(row.revenue) }}</template>
          </el-table-column>
          <el-table-column label="预算($)" width="100">
            <template v-slot="{ row }">{{ fmtUsd(row.budget) }}</template>
          </el-table-column>
          <el-table-column prop="voteAverage" label="评分" width="70"/>
          <el-table-column prop="runtime" label="时长" width="70"/>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import analysisApi from '@/api/analysis'

const PALETTE = ['#38bdf8', '#22d3ee', '#4f8cff', '#34d399', '#fbbf24', '#f472b6']

const LANG_MAP = {
  en: '英语', zh: '中文', ja: '日语', fr: '法语', de: '德语', es: '西班牙语',
  it: '意大利语', ko: '韩语', hi: '印地语', ru: '俄语', pt: '葡萄牙语',
  sv: '瑞典语', da: '丹麦语', ar: '阿拉伯语', nl: '荷兰语', no: '挪威语', pl: '波兰语'
}

export default {
  name: 'VideoAttrAnalysis',
  data () {
    return {
      stats: {},
      genreDist: [],
      yearDist: [],
      budgetRevenue: [],
      runtimeDist: [],
      langDist: [],
      topRevenue: [],
      statCards: [],
      charts: []
    }
  },
  mounted () {
    this.loadData()
    window.addEventListener('resize', this.resizeCharts)
  },
  beforeDestroy () {
    window.removeEventListener('resize', this.resizeCharts)
    this.charts.forEach(c => c.dispose())
  },
  methods: {
    loadData () {
      analysisApi.videoOverview().then(re => {
        const d = re.response || {}
        this.stats = d.stats || {}
        this.genreDist = d.genreDistribution || []
        this.yearDist = d.yearDistribution || []
        this.budgetRevenue = d.budgetRevenue || []
        this.runtimeDist = d.runtimeDistribution || []
        this.langDist = d.languageDistribution || []
        this.topRevenue = d.topRevenue || []
        this.buildStatCards()
        this.$nextTick(() => {
          this.renderGenre()
          this.renderYear()
          this.renderBudget()
          this.renderRuntime()
          this.renderLang()
        })
      }).catch(() => {})
    },
    buildStatCards () {
      const s = this.stats
      this.statCards = [
        { label: '影片总数', value: this.fmt(Number(s.video_count || 0)) },
        { label: '平均预算($)', value: this.fmtUsd(Number(s.avg_budget || 0)) },
        { label: '平均票房($)', value: this.fmtUsd(Number(s.avg_revenue || 0)) },
        { label: '平均评分', value: Number(s.avg_vote || 0).toFixed(1) },
        { label: '平均时长(分钟)', value: this.fmt(Number(s.avg_runtime || 0)) },
        { label: '平均热度', value: this.fmt(Number(s.avg_popularity || 0)) }
      ]
    },
    initChart (ref) {
      const dom = this.$refs[ref]
      if (!dom) return null
      const chart = echarts.init(dom)
      this.charts.push(chart)
      return chart
    },
    renderGenre () {
      const chart = this.initChart('genreChart')
      if (!chart) return
      const rows = this.genreDist.slice(0, 12)
      const names = rows.map(i => i.name)
      const values = rows.map(i => i.value)
      chart.setOption({
      color: PALETTE,
        tooltip: { trigger: 'item' },
        legend: { type: 'scroll', bottom: 0, textStyle: { fontSize: 10 } },
        series: [{
          type: 'pie', radius: ['25%', '68%'], center: ['50%', '45%'],
          itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 1 },
          label: { fontSize: 10 },
          data: names.map((n, idx) => ({ name: n, value: values[idx] }))
        }]
      })
    },
    renderYear () {
      const chart = this.initChart('yearChart')
      if (!chart) return
      chart.setOption({
      color: PALETTE,
        grid: { left: 50, right: 20, top: 30, bottom: 70 },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: this.yearDist.map(i => i.name), axisLabel: { rotate: 45, fontSize: 10 } },
        yAxis: { type: 'value' },
        dataZoom: [{ type: 'inside' }],
        series: [{ type: 'bar', data: this.yearDist.map(i => i.value),
          itemStyle: { color: '#38bdf8' }, barMaxWidth: 10 }]
      })
    },
    renderBudget () {
      const chart = this.initChart('budgetChart')
      if (!chart) return
      const m = 1000000
      const data = this.budgetRevenue.map(i => [Number(i.budget) / m, Number(i.revenue) / m])
      chart.setOption({
      color: PALETTE,
        tooltip: {
          trigger: 'item',
          formatter: p => {
            const v = p.value
            return '预算: $' + (v[0] * m / 100000000).toFixed(1) + ' 亿<br/>票房: $' + (v[1] * m / 100000000).toFixed(1) + ' 亿'
          }
        },
        grid: { left: 60, right: 30, top: 30, bottom: 50 },
        xAxis: { type: 'value', name: '预算(百万$)' },
        yAxis: { type: 'value', name: '票房(百万$)' },
        series: [{
          type: 'scatter', symbolSize: 5, data: data,
          itemStyle: { color: 'rgba(56,189,248,0.55)' },
          markLine: { silent: true, lineStyle: { type: 'dashed', color: '#ccc' },
            label: { show: false },
            data: [{ yAxis: 0 }] }
        }]
      })
    },
    renderRuntime () {
      const chart = this.initChart('runtimeChart')
      if (!chart) return
      const names = this.runtimeDist.map(i => i.name)
      const values = this.runtimeDist.map(i => i.value)
      chart.setOption({
      color: PALETTE,
        grid: { left: 60, right: 20, top: 30, bottom: 80 },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: names, axisLabel: { fontSize: 11, rotate: 25 } },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: values, barWidth: '45%',
          itemStyle: { color: '#34d399', borderRadius: [4, 4, 0, 0] },
          label: { show: true, position: 'top' } }]
      })
    },
    renderLang () {
      const chart = this.initChart('langChart')
      if (!chart) return
      const rows = this.langDist.slice(0, 10)
      const names = rows.map(i => LANG_MAP[i.name] || i.name)
      const values = rows.map(i => i.value)
      chart.setOption({
      color: PALETTE,
        tooltip: { trigger: 'axis' },
        grid: { left: 90, right: 40, top: 20, bottom: 40 },
        xAxis: { type: 'value' },
        yAxis: { type: 'category', data: names.reverse() },
        series: [{ type: 'bar', data: values.reverse(), barWidth: '55%',
          itemStyle: { color: '#fbbf24', borderRadius: [0, 4, 4, 0] },
          label: { show: true, position: 'right' } }]
      })
    },
    resizeCharts () {
      this.charts.forEach(c => c.resize())
    },
    fmt (n) {
      if (n >= 10000) return (n / 10000).toFixed(1) + ' 万'
      return String(n)
    },
    fmtUsd (n) {
      if (!n) return '-'
      if (n >= 100000000) return (n / 100000000).toFixed(1) + '亿'
      if (n >= 10000) return (n / 10000).toFixed(0) + '万'
      return String(n)
    }
  }
}
</script>

<style scoped>
.stat-card {
  background: #fff;
  border-radius: 6px;
  padding: 14px 16px;
  margin-bottom: 14px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}
.stat-num {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
}
.stat-label {
  margin-top: 6px;
  font-size: 13px;
  color: #909399;
}
.chart-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}
.chart-box {
  width: 49%;
  background: #fff;
  border-radius: 6px;
  padding: 12px;
  box-sizing: border-box;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  margin-bottom: 14px;
}
.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}
.chart {
  width: 100%;
  height: 330px;
}
</style>
