<template>
  <div class="app-container">
    <el-card shadow="never" class="predict-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">电影票房预测</span>
          <el-tag size="small" type="info">底层 6 算法：LinearRegression / KNN / SVM / DecisionTree / RandomForest / LightGBM</el-tag>
        </div>
      </template>

      <el-form :inline="false" label-width="110px" class="predict-form">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="预测模型">
              <el-select v-model="form.model" style="width:100%">
                <el-option label="LightGBM（推荐，效果最佳）" value="lgbm"/>
                <el-option label="随机森林 RandomForest" value="rf"/>
                <el-option label="线性回归 LinearRegression" value="lr"/>
                <el-option label="K 近邻回归 KNN" value="knn"/>
                <el-option label="支持向量回归 SVM" value="svm"/>
                <el-option label="决策树回归 DecisionTree" value="dt"/>
              </el-select>
            </el-form-item>
          </el-col>
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
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="片长(分钟)">
              <el-input-number v-model="form.runtime" :min="1" :step="5" style="width:100%"/>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="原始语言">
              <el-select v-model="form.language" filterable allow-create default-first-option
                         style="width:100%">
                <el-option v-for="l in languages" :key="l" :label="l" :value="l"/>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="影片状态">
              <el-select v-model="form.status" style="width:100%">
                <el-option v-for="s in statusList" :key="s" :label="s" :value="s"/>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="参考示例">
              <div class="example-btns">
                <el-button size="mini" @click="fillExample(0)">高成本科幻（阿凡达型）</el-button>
                <el-button size="mini" @click="fillExample(1)">中成本剧情</el-button>
                <el-button size="mini" @click="fillExample(2)">低成本小片</el-button>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label-width="0">
              <el-button type="primary" :loading="loading" class="predict-btn" @click="predict">
                开始预测票房
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <el-alert type="warning" :closable="false" show-icon class="predict-tip"
                title="首次预测会自动在 Movie-Analysis-master 中训练所选模型并缓存（约 10~30 秒），之后秒级返回；用户评分/推荐所需的模型不影响此处。" />
    </el-card>

    <el-card v-if="result" shadow="never" class="result-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">预测结果</span>
          <el-tag v-if="result.trainedNow" type="warning" size="small">本次为新训练模型</el-tag>
          <el-tag type="info" size="small">模型：{{ result.model }}</el-tag>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="result-item">
            <div class="result-label">预测全球票房（美元）</div>
            <div class="result-value usd">{{ formatMoney(result.prediction) }}</div>
            <div class="result-sub">≈ {{ formatCompact(result.prediction) }} USD</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="result-item">
            <div class="result-label">折合人民币（汇率 {{ form.rate }}）</div>
            <div class="result-value cny">¥ {{ formatCny(result.prediction) }}</div>
            <div class="result-sub">约 {{ formatYi(result.prediction) }} 亿元</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="result-item">
            <div class="result-label">模型指标（20% 测试集）</div>
            <div v-if="result.metrics" class="result-metrics">
              <div>决定系数 R²：<b>{{ fmt(result.metrics.r2) }}</b></div>
              <div>RMSE：{{ fmt(result.metrics.rmse) }}</div>
              <div>MAE：{{ fmt(result.metrics.mae) }}</div>
            </div>
            <div v-else class="result-sub">暂无指标</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import predictApi from '@/api/predict'

export default {
  name: 'PredictIndex',
  data () {
    return {
      loading: false,
      result: null,
      languages: ['en', 'zh', 'ja', 'fr', 'de', 'es', 'it', 'ko', 'hi'],
      statusList: ['Released', 'Rumored', 'Post Production', 'In Production', 'Planned', 'Canceled'],
      examples: [
        { budget: 237000000, popularity: 76.9, runtime: 162, language: 'en', status: 'Released' },
        { budget: 45000000, popularity: 25.1, runtime: 118, language: 'en', status: 'Released' },
        { budget: 3000000, popularity: 4.2, runtime: 95, language: 'zh', status: 'Released' }
      ],
      form: {
        model: 'lgbm',
        budget: 150000000,
        popularity: 18.6,
        runtime: 110,
        language: 'en',
        status: 'Released',
        rate: 7.2
      }
    }
  },
  methods: {
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
      const q = {
        model: f.model,
        budget: f.budget,
        popularity: f.popularity == null ? 0 : f.popularity,
        runtime: f.runtime,
        language: f.language,
        status: f.status
      }
      predictApi.predict(q).then(re => {
        this.result = re.response || {}
        this.loading = false
      }).catch(() => { this.loading = false })
    },
    fmt (v) {
      return v == null ? '-' : Number(v).toFixed(3)
    },
    formatMoney (v) {
      if (v == null) return '-'
      return '$' + Number(v).toLocaleString('en-US', { maximumFractionDigits: 0 })
    },
    formatCompact (v) {
      if (v == null) return '-'
      if (v >= 1e9) return (v / 1e9).toFixed(2) + ' 亿'
      if (v >= 1e6) return (v / 1e6).toFixed(2) + ' 百万'
      return Number(v).toFixed(0)
    },
    formatCny (v) {
      if (v == null) return '-'
      return '¥' + Number(v * this.form.rate).toLocaleString('en-US', { maximumFractionDigits: 0 })
    },
    formatYi (v) {
      if (v == null) return '-'
      return ((v * this.form.rate) / 1e8).toFixed(2)
    }
  }
}
</script>

<style scoped>
.predict-card {
  margin-bottom: 16px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
}
.predict-form {
  margin-top: 8px;
}
.predict-btn {
  width: 100%;
}
.example-btns {
  padding-top: 2px;
}
.predict-tip {
  margin-top: 4px;
}
.result-card {
  margin-top: 16px;
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
.result-value.cny {
  color: #f56c6c;
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
