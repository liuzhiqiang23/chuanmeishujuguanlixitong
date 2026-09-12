<template>
  <div class="app-container">
    <el-alert type="primary" :closable="false" show-icon style="margin-bottom:14px"
              title="特征探索分析（Python EDA）：由 algorithm/FeatureEDA/eda.py 一次生成 21 张统计图（14 张多维度分析图 + 7 张单特征/相关性图）。数据源为统一目录 data/ 下的票房预测训练集（TMDB），后端经 /eda/** 直接映射到 algorithm/FeatureEDA/figures 目录，重跑脚本后刷新页面即可看到最新图。"/>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :md="12" :lg="8" v-for="(item, idx) in images" :key="item.name" style="margin-bottom:16px">
        <el-card :body-style="{ padding: '12px' }" shadow="hover">
          <div class="eda-card">
            <el-image
              :src="'/eda/' + item.name"
              :preview-src-list="['/eda/' + item.name]"
              fit="contain"
              class="eda-img"
              lazy>
              <template #error>
                <div class="eda-img-error">
                  <span>图片缺失</span>
                </div>
              </template>
            </el-image>
            <div class="eda-title">{{ idx + 1 }}. {{ item.title }}</div>
            <div class="eda-desc">{{ item.desc }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'EdaAnalysis',
  data () {
    return {
      // 每张图：脚本生成的 PNG 文件名 + 中文标题/说明。新增图时在此追加即可。
      // 由 algorithm/FeatureEDA/eda.py 一次生成：fig01~fig14 多维度分析图 + 7 张单特征/相关性图
      images: [
        // ---- 多维度分析图（fig01~fig14）----
        { name: 'fig01_revenue_distribution.png', title: '票房收入分布', desc: '直方图与统计：票房高度右偏，绝大多数影片集中在低位，头部大片拉高均值。' },
        { name: 'fig02_budget_distribution.png', title: '制作预算分布', desc: '预算同样呈长尾分布，高投入大片只占少数。' },
        { name: 'fig03_budget_revenue_scatter.png', title: '预算与票房散点', desc: '预算越高票房上限越高，但离散度大，高投入不等于高回报。' },
        { name: 'fig04_movies_by_year.png', title: '各年份影片数量', desc: '按上映年份统计影片产量，近年产出显著上升。' },
        { name: 'fig05_revenue_trend_by_year.png', title: '票房年度趋势', desc: '年度票房的均值/中位数变化，观察市场大盘走势。' },
        { name: 'fig06_top_genres_count.png', title: '影片类型数量排行', desc: '各类型影片数量 Top：剧情、喜剧、动作等类型占据多数。' },
        { name: 'fig07_genre_revenue_box.png', title: '各类型票房箱线图', desc: '不同类型票房分布差异明显，动画/冒险类上限更高。' },
        { name: 'fig08_country_analysis.png', title: '制片国家/地区分析', desc: '主要制片国家/地区的影片数量与票房表现对比。' },
        { name: 'fig09_top_companies.png', title: '高产制作公司 Top', desc: '出品影片数量最多的制作公司排行。' },
        { name: 'fig10_top_directors.png', title: '导演作品 Top', desc: '作品数量/票房表现突出的导演排行。' },
        { name: 'fig11_popularity_revenue.png', title: '热度与票房', desc: 'TMDB 热度与票房的相关性散点，整体呈正相关。' },
        { name: 'fig12_runtime_analysis.png', title: '片长分析', desc: '片长分布及其与票房的关系，常见片长集中在 90~120 分钟。' },
        { name: 'fig13_release_month.png', title: '上映月份分布', desc: '按月份统计上映数量与票房，观察档期效应。' },
        { name: 'fig14_top_keywords.png', title: '高频关键词 Top', desc: '关键词词频排行，反映影片题材偏好。' },
        // ---- 单特征 / 相关性图（固定文件名）----
        { name: 'revenue_budget.png', title: '票房与预算的关系', desc: '散点图：预算（budget）与票房（revenue）呈正相关，大片高投入对应高票房。' },
        { name: 'revenue_popularity.png', title: '票房与热度（popularity2）的关系', desc: '散点图：电影热度越高，票房普遍越高。' },
        { name: 'revenue_theatrical.png', title: '票房与上映规模（theatrical）的关系', desc: '散点图：上映规模越大，票房越高。' },
        { name: 'revenue_language.png', title: '不同语种电影的票房分布', desc: '盒须图：英语片票房显著高于其他语种，呈现明显头部效应。' },
        { name: 'budget_recent_year.png', title: '各主要年份预算分布', desc: 'KDE 曲线：近年来高预算电影增多，预算分布更长尾。' },
        { name: 'revenue_year.png', title: '票房分布直方图（log 归一）', desc: '对数化后接近正态，说明票房分布高度偏斜，绝大多数电影票房较低。' },
        { name: 'corre.png', title: '特征相关性热力图', desc: '票房与 budget、popularity2、theatrical 呈中等正相关，与上映年份相关性弱。' }
      ]
    }
  }
}
</script>

<style scoped>
.eda-card {
  display: flex;
  flex-direction: column;
}
.eda-img {
  width: 100%;
  height: 260px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background: #fafafa;
}
.eda-img-error {
  height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 14px;
}
.eda-title {
  margin-top: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}
.eda-desc {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.6;
  color: #909399;
}
</style>
