<template>
  <div class="dashboard-container">
    <el-row :gutter="40" class="panel-group">
      <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
        <div class="card-panel">
          <div class="card-panel-icon-wrapper icon-people">
            <svg-icon icon-class="exam" class-name="card-panel-icon"/>
          </div>
          <div class="card-panel-description">
            <div class="card-panel-text">
              本月新增用户总数
            </div>
            <count-to :start-val="0" :end-val="newUserCount" :duration="2600" class="card-panel-num" v-loading="loading"/>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
        <div class="card-panel" >
          <div class="card-panel-icon-wrapper icon-message">
            <svg-icon icon-class="question" class-name="card-panel-icon"/>
          </div>
          <div class="card-panel-description">
            <div class="card-panel-text">
              新增视频
            </div>
            <count-to :start-val="0" :end-val="newVideoCount" :duration="3000" class="card-panel-num" v-loading="loading"/>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
        <div class="card-panel">
          <div class="card-panel-icon-wrapper icon-shopping">
            <svg-icon icon-class="doexampaper" class-name="card-panel-icon"/>
          </div>
          <div class="card-panel-description">
            <div class="card-panel-text">
              视频播放次数
            </div>
            <count-to :start-val="0" :end-val="doPlayVideoCount" :duration="3600" class="card-panel-num" v-loading="loading"/>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
        <div class="card-panel">
          <div class="card-panel-icon-wrapper icon-money">
            <svg-icon icon-class="doquestion" class-name="card-panel-icon"/>
          </div>
          <div class="card-panel-description">
            <div class="card-panel-text">
              最佳影片
            </div>
            <div class="card-panel-text">
              {{hotVideoCount}}
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
    <el-row class="echarts-line">
      <div id="echarts-moth-user" style="width: 100%;height:400px;" v-loading="loading"/>
    </el-row>
    <el-row class="echarts-line">
      <div id="echarts-moth-question" style="width: 100%;height:400px;" v-loading="loading"/>
    </el-row>
    <el-row class="echarts-line">
      <div style="font-weight:bold;margin-bottom:12px">视频热度榜单 TOP10</div>
      <el-table :data="heatTopList" border fit style="width:100%">
        <el-table-column type="index" label="排名" width="80" />
        <el-table-column prop="videoName" label="电影名称" />
        <el-table-column prop="voteAverage" label="评分" width="100" />
        <el-table-column prop="popularity" label="受欢迎度" width="120" />
        <el-table-column prop="heatScore" label="热度" width="120" />
      </el-table>
    </el-row>
  </div>
</template>

<script>
import resize from './components/mixins/resize'
import CountTo from '@/components/CountTo'
import dashboardApi from '@/api/dashboard'
export default {
  mixins: [resize],
  components: {
    CountTo
  },
  data () {
    return {
      newUserCount: 0,
      doPlayVideoCount: 0,
      newVideoCount: 0,
      hotVideoCount: '',
      heatTopList: [],
      echartsUserAction: null,
      echartsQuestion: null,
      loading: false
    }
  },
  mounted () {
    // eslint-disable-next-line no-undef
    echarts.registerTheme('movie-cyan', {
      color: ['#38bdf8', '#22d3ee', '#4f8cff', '#34d399', '#fbbf24', '#f472b6'],
      backgroundColor: 'transparent',
      textStyle: { fontFamily: 'Helvetica Neue, PingFang SC, Microsoft YaHei, sans-serif' }
    })
    // eslint-disable-next-line no-undef
    this.echartsUserAction = echarts.init(document.getElementById('echarts-moth-user'), 'movie-cyan')
    // eslint-disable-next-line no-undef
    this.echartsQuestion = echarts.init(document.getElementById('echarts-moth-question'), 'movie-cyan')
    let _this = this
    this.loading = true
    dashboardApi.index().then(re => {
      let response = re.response
      _this.newUserCount = response.newUserCount
      _this.doPlayVideoCount = response.doPlayVideoCount
      _this.newVideoCount = response.newVideoCount
      _this.hotVideoCount = response.hotVideoCount
      _this.heatTopList = response.heatTopList || []
      _this.echartsUserAction.setOption(this.option('用户活跃度', '{b}日{c}度', response.mothDayText, response.mothDayUserActionValue))
      _this.echartsQuestion.setOption(this.option('视频月播放次数', '{b}日{c}题', response.mothDayText, response.mothDayVideoPlayValue))
      this.loading = false
    })
  },
  methods: {
    option (title, formatter, label, vaule) {
      return {
        color: ['#38bdf8', '#22d3ee', '#4f8cff', '#34d399'],
        title: {
          text: title,
          x: 'center',
          textStyle: { color: '#1f3350', fontSize: 15, fontWeight: 600 }
        },
        tooltip: {
          trigger: 'item',
          formatter: formatter
        },
        xAxis: {
          type: 'category',
          data: label
        },
        grid: {
          left: 10,
          right: 10,
          bottom: 20,
          top: 30,
          containLabel: true
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          data: vaule,
          type: 'line',
          smooth: true,
          lineStyle: { width: 3 },
          areaStyle: { opacity: 0.08 }
        }]
      }
    }
  }
}
</script>

<style lang="scss" scoped>

  .dashboard-container {
    padding: 24px 28px;
    background-color: #f2f6fb;
    position: relative;

    .chart-wrapper {
      background: #fff;
      padding: 16px 16px 0;
      margin-bottom: 32px;
    }
  }

  @media (max-width: 1024px) {
    .chart-wrapper {
      padding: 8px;
    }
  }

  .dashboard-editor-container {
    padding: 32px;
    background-color: rgb(240, 242, 245);
    position: relative;

    .github-corner {
      position: absolute;
      top: 0px;
      border: 0;
      right: 0;
    }

    .chart-wrapper {
      background: #fff;
      padding: 16px 16px 0;
      margin-bottom: 32px;
    }
  }

  @media (max-width: 1024px) {
    .chart-wrapper {
      padding: 8px;
    }
  }

  .panel-group {
    margin-top: 18px;

    .card-panel-col {
      margin-bottom: 32px;
    }

    .card-panel {
      height: 112px;
      cursor: pointer;
      font-size: 12px;
      position: relative;
      overflow: hidden;
      color: #666;
      background: #fff;
      border-radius: 14px;
      border: 1px solid #e8eef6;
      box-shadow: 0 2px 14px rgba(24, 48, 84, 0.06);
      transition: transform 0.22s ease, box-shadow 0.22s ease;

      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 28px -10px rgba(24, 48, 84, 0.18);

        .card-panel-icon-wrapper {
          color: #fff;
        }

        .icon-people {
          background: #22d3ee;
        }

        .icon-message {
          background: #38bdf8;
        }

        .icon-money {
          background: #f472b6;
        }

        .icon-shopping {
          background: #34d399;
        }
      }

      .icon-people {
        color: #0ea5c9;
        background: rgba(34, 211, 238, 0.10);
      }

      .icon-message {
        color: #1d8fd1;
        background: rgba(56, 189, 248, 0.10);
      }

      .icon-money {
        color: #db4a97;
        background: rgba(244, 114, 182, 0.10);
      }

      .icon-shopping {
        color: #16a374;
        background: rgba(52, 211, 153, 0.10);
      }

      .card-panel-icon-wrapper {
        float: left;
        margin: 16px 0 0 16px;
        padding: 15px;
        transition: all 0.38s ease-out;
        border-radius: 12px;
      }

      .card-panel-icon {
        float: left;
        font-size: 44px;
      }

      .card-panel-description {
        float: none;
        font-weight: bold;
        margin: 26px;
        margin-left: 0px;

        .card-panel-text {
          line-height: 18px;
          color: rgba(31, 51, 80, 0.55);
          font-size: 13px;
          letter-spacing: 0.5px;
          margin-bottom: 10px;
        }

        .card-panel-num {
          font-size: 26px;
          color: #1f3350;
          font-weight: 700;
        }
      }
    }
  }

  @media (max-width: 550px) {
    .card-panel-description {
      display: none;
    }

    .card-panel-icon-wrapper {
      float: none !important;
      width: 100%;
      height: 100%;
      margin: 0 !important;

      .svg-icon {
        display: block;
        margin: 14px auto !important;
        float: none !important;
      }
    }
  }

  .echarts-line{
    background:#fff;
    padding:16px 16px 4px;
    margin-bottom:20px;
    border-radius:14px;
    border:1px solid #e8eef6;
    box-shadow:0 2px 14px rgba(24,48,84,0.05);
  }
</style>
