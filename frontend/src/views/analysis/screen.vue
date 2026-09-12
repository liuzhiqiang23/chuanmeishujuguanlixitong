<template>
  <div class="container">
    <div class="chart" ref="genreChart"></div>
    <div class="chart" ref="yearChart"></div>
    <div class="chart" ref="budgetChart"></div>
    <div class="chart" ref="ratingChart"></div>
    <div class="chart" ref="activeChart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import analysisApi from '@/api/analysis'

export default {
  name: 'AnalysisScreen',
  data () {
    return {
      genreDistribution: [],
      yearDistribution: [],
      budgetRevenue: [],
      ratingDistribution: [],
      activeUsers: []
    }
  },
  mounted () {
    analysisApi.overview().then(re => {
      const d = re.response || {}
      this.genreDistribution = d.genreDistribution || []
      this.yearDistribution = d.yearDistribution || []
      this.budgetRevenue = d.budgetRevenue || []
      this.ratingDistribution = d.ratingDistribution || []
      this.activeUsers = d.activeUsers || []
      this.renderGenrePie()
      this.renderYearBar()
      this.renderBudgetScatter()
      this.renderRatingBar()
      this.renderActiveBar()
    }).catch(() => {
      // 错误信息已由 request 拦截器统一提示，此处避免未处理的 Promise
    })
  },
  methods: {
    initChart (refName, options) {
      const chart = echarts.init(this.$refs[refName])
      if (!options.color) {
        options.color = ['#38bdf8', '#22d3ee', '#4f8cff', '#34d399', '#fbbf24', '#f472b6', '#a78bfa', '#fb7185']
      }
      chart.setOption(options)
      return chart
    },
    renderGenrePie () {
      const data = this.genreDistribution.slice(0, 10).map(i => ({ name: i.name, value: i.value }))
      this.initChart('genreChart', {
        title: { text: '电影类型分布', left: 'center' },
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        series: [{
          name: '类型', type: 'pie', radius: ['40%', '70%'], roseType: 'area',
          label: { formatter: '{b}: {c}' }, data
        }]
      })
    },
    renderYearBar () {
      const names = this.yearDistribution.map(i => i.name)
      const values = this.yearDistribution.map(i => i.value)
      this.initChart('yearChart', {
        title: { text: '上映年份分布', left: 'center' },
        tooltip: {},
        xAxis: { data: names, axisLabel: { rotate: 45 } },
        yAxis: {},
        series: [{ name: '影片数', type: 'bar', data: values }]
      })
    },
    renderBudgetScatter () {
      const data = this.budgetRevenue
        .filter(i => i.budget != null && i.revenue != null)
        .map(i => [i.budget, i.revenue])
      this.initChart('budgetChart', {
        title: { text: '票房 vs 预算', left: 'center' },
        tooltip: { formatter: p => '预算 ' + p.value[0] + ' / 票房 ' + p.value[1] },
        xAxis: { name: '预算', scale: true },
        yAxis: { name: '票房', scale: true },
        series: [{ type: 'scatter', symbolSize: 6, data }]
      })
    },
    renderRatingBar () {
      const names = this.ratingDistribution.map(i => i.name)
      const values = this.ratingDistribution.map(i => i.value)
      this.initChart('ratingChart', {
        title: { text: '用户评分分布', left: 'center' },
        tooltip: {},
        xAxis: { data: names },
        yAxis: {},
        series: [{ name: '评分人数', type: 'bar', data: values }]
      })
    },
    renderActiveBar () {
      const names = this.activeUsers.map(i => i.name)
      const values = this.activeUsers.map(i => i.value)
      this.initChart('activeChart', {
        title: { text: 'TOP 活跃用户', left: 'center' },
        tooltip: {},
        xAxis: { data: names, axisLabel: { rotate: 45 } },
        yAxis: {},
        series: [{ name: '评分次数', type: 'bar', data: values }]
      })
    }
  }
}
</script>

<style scoped>
.container {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  align-items: center;
}
.chart {
  width: 45%;
  height: 380px;
  margin: 10px 0;
}
</style>
