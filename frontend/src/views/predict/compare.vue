<template>
  <div class="app-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">多算法对比（8 种机器学习 / 深度学习）</span>
          <el-tag v-if="best" type="success" size="small">最佳模型：{{ best }}</el-tag>
          <el-button type="text" @click="$router.push('/predict/index')">← 回到票房预测</el-button>
        </div>
      </template>

      <el-alert type="info" :closable="false" show-icon class="mt8"
                title="训练数据：新数据集清洗产物 train_clean.csv（5000 行 × 48 列）；按 8:2 切分，随机种子 42；目标为 log10(票房)；
                       需要标准化的模型（KNN/SVR/MLP）统一封装 StandardScaler 流水线，保证训练与推理一致。" />

      <el-table v-loading="loading" :data="algoList" border fit class="mt12"
                :row-class-name="rowClass">
        <el-table-column label="排名" width="80" align="center">
          <template #default="{ row }">{{ row.rank }}</template>
        </el-table-column>
        <el-table-column prop="name" label="算法" min-width="220"/>
        <el-table-column label="RMSE ↓" width="120" align="center">
          <template #default="{ row }">{{ fmt(row.rmse) }}</template>
        </el-table-column>
        <el-table-column label="MAE ↓" width="120" align="center">
          <template #default="{ row }">{{ fmt(row.mae) }}</template>
        </el-table-column>
        <el-table-column label="R² ↑" width="120" align="center">
          <template #default="{ row }">{{ fmt(row.r2) }}</template>
        </el-table-column>
        <el-table-column label="训练耗时(秒)" width="140" align="center">
          <template #default="{ row }">{{ row.fitSeconds == null ? '-' : Number(row.fitSeconds).toFixed(2) }}</template>
        </el-table-column>
      </el-table>

      <div v-if="!loading && !algoList.length" class="empty-tip">
        暂无对比数据：请先在后端就绪后调用 /api/predict/algo-compare（第六步），或直接查看算法目录下的 metrics.json。
      </div>

      <div class="figure-block" v-if="figure">
        <div class="figure-title">算法对比图（RMSE / R²）</div>
        <el-image :src="figure" :preview-src-list="[figure]" fit="contain" class="figure-img">
          <template #error>
            <div class="figure-error">对比图暂不可用（后端静态映射 /algo-figures/** 于第六步接入）</div>
          </template>
        </el-image>
      </div>

      <div class="conclusion">
        <div class="conclusion-title">结论</div>
        <p v-if="best">
          8 种算法中 <b>{{ best }}</b> 的验证集 RMSE 最小（{{ fmt(bestRow.rmse) }}），故作为在线预测的服务模型；
          树模型（随机森林 / LightGBM / 梯度提升）整体优于线性与 KNN，说明票房与特征之间存在明显非线性；
          MLP 作为深度学习基线表现居中，训练耗时最长。
        </p>
        <p v-else>等待接口返回后自动生成结论。</p>
      </div>
    </el-card>
  </div>
</template>

<script>
import predictApi from '@/api/predict'

export default {
  name: 'PredictCompare',
  data () {
    return {
      loading: false,
      best: '',
      algoList: [],
      figure: '/algo-figures/algo_comparison.png'
    }
  },
  computed: {
    bestRow () {
      return this.algoList.find(a => a.name === this.best) || {}
    }
  },
  created () {
    this.load()
  },
  methods: {
    load () {
      this.loading = true
      predictApi.algoCompare().then(re => {
        const d = re.response || {}
        this.best = d.best || ''
        const list = (d.algorithms || []).slice().sort((a, b) => a.rmse - b.rmse)
        this.algoList = list.map((a, i) => Object.assign({}, a, { rank: i + 1 }))
        if (d.figure) this.figure = d.figure
        this.loading = false
      }).catch(() => { this.loading = false })
    },
    rowClass ({ row }) {
      return row.name === this.best ? 'best-row' : ''
    },
    fmt (v) {
      return v == null ? '-' : Number(v).toFixed(4)
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
  margin-right: 8px;
}
.mt8 {
  margin-top: 8px;
}
.mt12 {
  margin-top: 12px;
}
::v-deep .best-row {
  background: #f0f9eb;
  font-weight: 600;
}
.figure-block {
  margin-top: 20px;
}
.figure-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}
.figure-img {
  width: 100%;
  max-height: 520px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}
.figure-error {
  color: #909399;
  font-size: 13px;
  padding: 40px;
  text-align: center;
}
.empty-tip {
  color: #909399;
  font-size: 13px;
  padding: 16px 0;
}
.conclusion {
  margin-top: 20px;
  background: #fafafa;
  border-left: 4px solid #409eff;
  padding: 12px 16px;
  border-radius: 2px;
}
.conclusion-title {
  font-weight: 600;
  margin-bottom: 6px;
}
.conclusion p {
  margin: 0;
  color: #606266;
  line-height: 1.8;
}
</style>
