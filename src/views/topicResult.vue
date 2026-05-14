
<template>
  <div id="topic-result">
    <div class="bg-color-black" >
      <div class="d-flex pt-2 pl-2">
        <span style="color: #5cd9e8">
          <icon name="chart-bar"></icon>
        </span>
        <div class="d-flex">
          <span class="fs-xl text mx-2" style="font-size: medium">课题结果图表</span>
          <el-radio-group class="fs-xl text mx-2" v-model="radioValue" size="small" @input="refreshDataInfo">
            <el-radio label="history">历史</el-radio>
            <el-radio label="prediction">预测</el-radio>
          </el-radio-group>
        </div>
      </div>
      <div>
        <bottomLeftChart ref="bottomLeftChart"/>
      </div>
    </div>
  </div>
</template>


<script>
import echarts from 'echarts';

export default {
  name: 'TopicResult',
  data() {
    return {
      chart: null,
      currentTopic: 1, // 当前展示的课题ID
    };
  },
  mounted() {
    this.initChart();
    // 监听课题切换事件
    this.$root.$bus.$on('topic-change', (topicId) => {
      this.currentTopic = topicId;
      this.updateChartByTopic(topicId);
    });
  },
  beforeDestroy() {
    // 移除事件监听
    if (this.$root.$bus) {
      this.$root.$bus.$off('topic-change');
    }
    if (this.chart) {
      this.chart.dispose();
    }
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.chart);
      this.updateChartByTopic(this.currentTopic);
      // 监听窗口大小变化，自适应
      window.addEventListener('resize', () => {
        if (this.chart) {
          this.chart.resize();
        }
      });
    },
    updateChartByTopic(topicId) {
      if (!this.chart) return;
      // 根据课题ID模拟不同的图表数据
      const option = this.getChartOption(topicId);
      this.chart.setOption(option, true);
    },
    getChartOption(topicId) {
      // 这里根据课题返回不同的ECharts配置，示例为折线图
      const baseOption = {
        tooltip: { trigger: 'axis' },
        legend: { data: ['结果指标'], textStyle: { color: '#d3d6dd' } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: {
          type: 'category',
          data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
          axisLabel: { color: '#d3d6dd' },
        },
        yAxis: {
          type: 'value',
          axisLabel: { color: '#d3d6dd' },
        },
        series: [
          {
            name: '结果指标',
            type: 'line',
            data: this.getTopicData(topicId),
            itemStyle: { color: '#00f0ff' },
          },
        ],
      };
      return baseOption;
    },
    getTopicData(topicId) {
      // 模拟不同课题的数据
      const dataMap = {
        1: [120, 200, 150, 80, 70, 110, 130],
        2: [220, 182, 191, 234, 290, 330, 310],
        3: [150, 232, 201, 154, 190, 330, 410],
        4: [320, 332, 301, 334, 390, 330, 320],
      };
      return dataMap[topicId] || dataMap[1];
    },
  },
};
</script>

<!--
<style scoped>
.module-title {
  font-size: 0.2rem;
  color: #00f0ff;
  margin-bottom: 0.1rem;
}
.chart-container {
  width: 100%;
  height: calc(100% - 0.4rem);
  min-height: 2rem;
}
</style>-->


<style lang="scss">
#topic-result {
  padding: 0.3rem 0.2rem;
  height: 7rem;
  min-width: 3.75rem;
  border-radius: 0.0625rem;
  .bg-color-black {
    height: 6.0625rem;
    border-radius: 0.125rem;
  }
  .text {
    color: #c3cbde;
  }
  .chart-box {
    margin-top: 0.2rem;
    width: 2.125rem;
    height: 2.125rem;
    .active-ring-name {
      padding-top: 0.125rem;
    }
  }
}
</style>