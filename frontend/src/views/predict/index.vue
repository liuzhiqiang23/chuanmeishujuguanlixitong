<template>
  <div class="app-container">
    <el-tabs v-model="activeTab">
      <!-- ==================== 单片预测 ==================== -->
      <el-tab-pane label="单片预测" name="single">
        <el-card shadow="never" class="mt-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">电影票房预测</span>
              <el-tag size="small" type="success">服务模型：{{ serveModel }}（离线训练，毫秒级返回）</el-tag>
              <el-button type="text" @click="$router.push('/predict/compare')">查看 8 算法对比 →</el-button>
            </div>
          </template>

          <el-form label-width="120px" class="predict-form">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="制作预算(美元)">
                  <el-input-number v-model="form.budget" :min="0" :step="10000000"
                                   :controls="false" style="width:100%"/>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="热度 popularity">
                  <el-input-number v-model="form.popularity" :min="0" :max="500"
                                   :step="1" style="width:100%"/>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="片长(分钟)">
                  <el-input-number v-model="form.runtime" :min="1" :step="5" style="width:100%"/>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="原始语言">
                  <el-select v-model="form.language" filterable allow-create default-first-option
                             style="width:100%">
                    <el-option v-for="l in languages" :key="l" :label="l" :value="l"/>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="上映月份">
                  <el-select v-model="form.releaseMonth" clearable placeholder="可选" style="width:100%">
                    <el-option v-for="m in 12" :key="m" :label="m + ' 月'" :value="m"/>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="主类型">
                  <el-select v-model="form.genres" clearable placeholder="可选" style="width:100%">
                    <el-option v-for="g in genres" :key="g.name" :label="g.name + '（' + g.count + ' 部）'"
                               :value="g.name"/>
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="16">
                <el-form-item label="参考示例">
                  <div class="example-btns">
                    <el-button size="small" @click="fillExample(0)">高成本科幻（阿凡达型）</el-button>
                    <el-button size="small" @click="fillExample(1)">中成本剧情</el-button>
                    <el-button size="small" @click="fillExample(2)">低成本小片</el-button>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label-width="0">
                  <el-button type="primary" :loading="loading" class="full-btn" @click="predict">
                    开始预测票房
                  </el-button>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>

          <el-alert type="info" :closable="false" show-icon
                    title="预测由新数据集训练的 8 优模型（随机森林）离线完成：预算缺失按历史中位数处理，结果在对数尺度上预测后还原为美元。" />
        </el-card>

        <el-card v-if="result" shadow="never" class="mt-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">预测结果</span>
              <el-tag type="info" size="small">模型：{{ result.model }}</el-tag>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="result-item">
                <div class="result-label">预测全球票房</div>
                <div class="result-value usd">{{ formatMoney(result.prediction) }}</div>
                <div class="result-sub">{{ formatYi(result.prediction) }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="result-item">
                <div class="result-label">参考区间（±1.96·RMSE）</div>
                <div class="result-range">
                  {{ formatMoney(range.low) }} ~ {{ formatMoney(range.high) }}
                </div>
                <div class="result-sub">对数正态近似，仅供参考</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="result-item">
                <div class="result-label">对数票房 log10</div>
                <div class="result-value log">{{ fmt(result.logRevenue) }}</div>
                <div class="result-sub">模型直接输出量</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="result-item">
                <div class="result-label">模型指标（验证集）</div>
                <div v-if="result.metrics" class="result-metrics">
                  <div>R²：<b>{{ fmt(result.metrics.r2) }}</b></div>
                  <div>RMSE：{{ fmt(result.metrics.rmse) }}</div>
                  <div>MAE：{{ fmt(result.metrics.mae) }}</div>
                </div>
                <div v-else class="result-sub">暂无指标</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>

      <!-- ==================== 批量预测 ==================== -->
      <el-tab-pane label="批量预测" name="batch">
        <el-card shadow="never" class="mt-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">批量预测（test 集）</span>
              <el-tag size="small" type="warning">结果逐条写入 t_prediction_log 留痕</el-tag>
            </div>
          </template>
          <el-form inline>
            <el-form-item label="预测条数">
              <el-input-number v-model="batch.limit" :min="1" :max="5000" :step="500"/>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="batchLoading" @click="runBatch">开始批量预测</el-button>
            </el-form-item>
            <el-form-item>
              <el-button :loading="logsLoading" @click="loadLogs">刷新预测记录</el-button>
            </el-form-item>
          </el-form>

          <el-alert v-if="batchResult" type="success" :closable="false" show-icon class="mt8"
                    :title="'本次完成 ' + batchResult.predicted + ' 条，耗时 ' + batchResult.seconds + ' 秒，'
                      + '落库 ' + batchResult.logRows + ' 条；平均预测票房 ' + formatMoney(batchResult.avgRevenue)" />

          <el-table v-loading="logsLoading" :data="logs" border fit size="small" class="mt12">
            <el-table-column prop="id" label="记录号" width="90"/>
            <el-table-column prop="movieId" label="影片ID" width="110"/>
            <el-table-column prop="modelName" label="模型" width="150"/>
            <el-table-column label="预测票房" width="160">
              <template #default="{ row }">{{ formatMoney(row.predictedRevenue) }}</template>
            </el-table-column>
            <el-table-column prop="movieTitle" label="影片名" show-overflow-tooltip/>
            <el-table-column prop="createdAt" label="预测时间" width="180"/>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import predictApi from '@/api/predict'
import movieApi from '@/api/movie'
import { formatMoney, formatYi } from '@/utils/media'

export default {
  name: 'PredictIndex',
  data () {
    return {
      activeTab: 'single',
      loading: false,
      result: null,
      serveModel: '随机森林 RandomForest',
      genres: [],
      languages: ['en', 'zh', 'ja', 'fr', 'de', 'es', 'it', 'ko', 'hi'],
      examples: [
        { budget: 237000000, popularity: 76.9, runtime: 162, language: 'en' },
        { budget: 45000000, popularity: 25.1, runtime: 118, language: 'en' },
        { budget: 3000000, popularity: 4.2, runtime: 95, language: 'zh' }
      ],
      form: {
        model: 'best',
        budget: 150000000,
        popularity: 18.6,
        runtime: 110,
        language: 'en',
        status: 'Released',
        releaseMonth: null,
        genres: ''
      },
      batch: { limit: 1000 },
      batchLoading: false,
      batchResult: null,
      logsLoading: false,
      logs: []
    }
  },
  computed: {
    range () {
      const r = (this.result && this.result.range) || {}
      return { low: r.low, high: r.high }
    }
  },
  created () {
    this.loadServeModel()
    this.loadGenres()
    this.loadLogs()
  },
  methods: {
    formatMoney,
    formatYi,
    loadServeModel () {
      predictApi.algoCompare().then(re => {
        const d = re.response || {}
        if (d.best) this.serveModel = d.best
      }).catch(() => {})
    },
    loadGenres () {
      movieApi.stats().then(re => {
        this.genres = ((re.response || {}).genreTop || []).slice(0, 12)
      }).catch(() => {})
    },
    fillExample (idx) {
      Object.assign(this.form, this.examples[idx])
    },
    predict () {
      const f = this.form
      if (f.budget == null || f.budget < 0) {
        this.$message.error('请填写有效的制作预算（非负数）')
        return
      }
      if (f.runtime == null || f.runtime <= 0) {
        this.$message.error('请填写有效的片长（分钟）')
        return
      }
      this.loading = true
      predictApi.predict({
        model: 'best',
        budget: f.budget,
        popularity: f.popularity == null ? 0 : f.popularity,
        runtime: f.runtime,
        language: f.language,
        status: f.status,
        releaseMonth: f.releaseMonth,
        genres: f.genres
      }).then(re => {
        this.result = re.response || {}
        this.loading = false
        this.loadLogs()
      }).catch(() => { this.loading = false })
    },
    runBatch () {
      this.batchLoading = true
      predictApi.batch({ limit: this.batch.limit }).then(re => {
        this.batchResult = re.response || {}
        this.batchLoading = false
        this.loadLogs()
      }).catch(() => { this.batchLoading = false })
    },
    loadLogs () {
      this.logsLoading = true
      predictApi.logs({ pageIndex: 1, pageSize: 10 }).then(re => {
        const d = re.response || {}
        this.logs = d.list || []
        this.logsLoading = false
      }).catch(() => { this.logsLoading = false })
    },
    fmt (v) {
      return v == null ? '-' : Number(v).toFixed(3)
    }
  }
}
</script>

<style scoped>
.mt-card {
  margin-bottom: 16px;
}
.mt8 {
  margin-top: 8px;
}
.mt12 {
  margin-top: 12px;
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
.predict-form {
  margin-top: 8px;
}
.full-btn {
  width: 100%;
}
.example-btns {
  padding-top: 2px;
}
.result-item {
  text-align: center;
  padding: 16px 0;
}
.result-label {
  color: #909399;
  font-size: 13px;
  margin-bottom: 12px;
}
.result-value {
  font-size: 30px;
  font-weight: 700;
  line-height: 1.2;
}
.result-value.usd {
  color: #409eff;
}
.result-value.log {
  color: #67c23a;
}
.result-range {
  font-size: 16px;
  font-weight: 600;
  color: #e6a23c;
  line-height: 1.8;
}
.result-sub {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}
.result-metrics {
  font-size: 14px;
  color: #606266;
  line-height: 2;
}
.result-metrics b {
  color: #67c23a;
}
</style>
