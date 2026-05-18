
<template>
  <div id="topic-result">
    <div class="bg-color-black" >
		
		<!--标题与下拉框-->
    <div class="d-flex pt-2 pl-2">
        <span style="color: #5cd9e8">
          <icon name="chart-bar"></icon>
        </span>
        <div class="d-flex">
			<span style="color: #5cd9e8;">
				<icon name="chart-bar"></icon>
			</span>
          <span class="fs-xl text mx-2" style="font-size: medium">课题结果图表</span>
		<!--原有历史、预测勾选框
		<el-radio-group class="fs-xl text mx-2" v-model="radioValue" size="small" @input="refreshDataInfo">
            <el-radio label="history">历史</el-radio>
            <el-radio label="prediction">预测</el-radio>
        </el-radio-group>-->
        </div>
		<!-- 两个联动下拉框 -->
		<div class="d-flex">
		<!-- 课题选择下拉框 -->
			<el-select 
				v-model="currentTopic" 
				size="small" 
				placeholder="请选择课题" 
				style="width: 120px; margin-right: 10px;"
				@change="onTopicChange"
			>
				<el-option
				v-for="topic in topics"
				:key="topic.id"
				:label="topic.name"
				:value="topic.id"
				></el-option>
			</el-select>
		<!-- 图表选择下拉框（根据课题联动） -->
			<el-select 
				v-model="currentChart" 
				size="small" 
				placeholder="请选择图表" 
				style="width: 120px;"
				@change="onChartChange"
			>
				<el-option
				v-for="chart in currentChartOptions"
				:key="chart.value"
				:label="chart.label"
				:value="chart.value"
				></el-option>
			</el-select>
		</div>
    </div>
        <!-- 图表/表格展示区域 -->
        <div class="chart-display-area">
            <!-- 图表容器（仅当有图表配置时显示） -->
            <div 
				v-show="currentView === 'chart'" 
				ref="chartContainer" 
				class="chart-container"
			></div>
          
			<!-- 表格容器 -->
			<div v-show="currentView === 'table'" class="table-container">
				<table class="data-table">
				<thead>
					<tr>
						<th v-for="col in currentTableColumns" :key="col">{{ col }}</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="(row, index) in currentTableData" :key="index">
						<td v-for="col in currentTableColumns" :key="col">{{ row[col] }}</td>
					</tr>
				</tbody>
				</table>
			</div>
        </div>
		<!--原有数据历史图
		<div>
			<bottomLeftChart ref="bottomLeftChart"/>
		</div>-->
    </div>
  </div>
</template>


<script>
import echarts from 'echarts';

export default {
  name: 'TopicResult',
  data() {
    return {
		// 当前选中的值
		currentTopic: 1,
		currentChart: '',
		chartInstance: null,
	
		// 课题列表
		topics: [
			{ id: 1, name: '课题一' },
			{ id: 2, name: '课题二' },
			{ id: 3, name: '课题三' },
			{ id: 4, name: '课题四' },
		],
	
		// 每个课题对应的图表选项
		chartOptionsMap: {
			1: [
			{ label: '图1：趋势图', value: 'chart1'},
			{ label: '图2：柱状图', value: 'chart2' },
			{ label: '表格：明细数据', value: 'table' },
			],
			2: [
			{ label: '图1：趋势图', value: 'chart1' },
			{ label: '表格：明细数据', value: 'table' },
			],
			3: [
			{ label: '图1：饼图', value: 'chart1' },
			{ label: '图2：趋势图', value: 'chart2' },
			{ label: '表格：明细数据', value: 'table' },
			],
			4: [
			{ label: '图1：柱状图', value: 'chart1' },
			{ label: '表格：明细数据', value: 'table' },
			],
		},

		// 课题预设数据（在此处替换为真实数据）
		topicData: {
			1: {
			//chart1: { /* 折线图数据 */ },
			chart1: {
				name: 'CPU使用率',
				type: 'line',
				categories: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
				values: [45, 52, 48, 60, 55, 70]
			},
			chart2: { /* 柱状图数据 */ },
			table: [ /* 表格数据 */ ],
			},
			// ... 其他课题数据见下文说明
		}
    };
  },
  computed: {
    // 当前课题对应的图表选项
    currentChartOptions() {
        return this.chartOptionsMap[this.currentTopic] || [];
    },
    // 当前视图类型（图表或表格）
    currentView() {
        if (this.currentChart === 'table') return 'table';
        if (this.currentChart && this.currentChart.startsWith('chart')) return 'chart';
        return 'chart'; // 默认图表
    },
    // 当前表格列名
    currentTableColumns() {
        const tableData = this.topicData[this.currentTopic]?.table;
        if (tableData && tableData.length > 0) {
          return Object.keys(tableData[0]);
        }
        return [];
    },
    // 当前表格数据
    currentTableData() {
        return this.topicData[this.currentTopic]?.table || [];
    },
  },
  watch: {
    // 当表格视图显示时，无需特殊处理
    currentView(newVal) {
        if (newVal === 'chart') {
            this.$nextTick(() => {
                this.renderChart();
            });
        }
    }
  },
  mounted() {
    this.initDefaultSelection();
    this.$nextTick(() => {
        this.renderChart();
    });
    window.addEventListener('resize', this.handleResize);
  },
  beforeDestroy() {
        window.removeEventListener('resize', this.handleResize);
        if (this.chartInstance) {
            this.chartInstance.dispose();
            this.chartInstance = null;
        }
  },
  methods: {
    // 初始化默认选中
    initDefaultSelection() {
        const options = this.chartOptionsMap[this.currentTopic];
        if (options && options.length > 0) {
            this.currentChart = options[0].value;
        }
    },
    // 课题下拉框变化
    onTopicChange(topicId) {
        // 重置为该课题的第一个图表选项
        const options = this.chartOptionsMap[topicId];
        if (options && options.length > 0) {
            this.currentChart = options[0].value;
        }
        this.renderChart();
    },
    // 图表下拉框变化
    onChartChange() {
        this.renderChart();
    },
    // 渲染图表
    renderChart() {
        if (this.currentView !== 'chart') return;
        
        const container = this.$refs.chartContainer;
        if (!container) return;
  
        // 销毁旧实例
        if (this.chartInstance) {
            this.chartInstance.dispose();
            this.chartInstance = null;
        }
  
        // 创建新实例
        this.chartInstance = echarts.init(container);
        
        // 获取当前图表配置
        const chartData = this.topicData[this.currentTopic]?.[this.currentChart];
        if (!chartData) return;
  
        const option = this.buildChartOption(chartData);
        if (option) {
            this.chartInstance.setOption(option);
        }
    },
    // 根据图表数据构建 ECharts 配置
    buildChartOption(chartData) {
        // 根据图表类型构建不同的配置
        if (!chartData) return null;
  
        // 通用暗色主题配置
        const baseOption = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(15, 19, 37, 0.9)',
                borderColor: '#00f0ff',
                textStyle: { color: '#d3d6dd' }
            },
            grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
        };
  
        // 如果是折线图类型
        if (chartData.type === 'line' || chartData.categories) {
            return {
                ...baseOption,
                xAxis: {
                    type: 'category',
                    data: chartData.categories || [],
                    axisLabel: { color: '#d3d6dd' },
                    axisLine: { lineStyle: { color: 'rgba(0, 240, 255, 0.3)' } },
                },
            yAxis: {
                type: 'value',
                axisLabel: { color: '#d3d6dd' },
                splitLine: { lineStyle: { color: 'rgba(0, 240, 255, 0.1)' } },
            },
            series: [{
                name: chartData.name || '指标',
                type: chartData.type || 'line',
                data: chartData.values || [],
                smooth: true,
                itemStyle: { color: '#00f0ff' },
                lineStyle: { color: '#00f0ff', width: 2 },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(0, 240, 255, 0.3)' },
                        { offset: 1, color: 'rgba(0, 240, 255, 0.02)' }
                    ])
                }
            }]
            };
        }
  
        // 如果是饼图类型
        if (chartData.type === 'pie') {
          return {
            ...baseOption,
            tooltip: { trigger: 'item' },
            series: [{
              name: chartData.name || '指标',
              type: 'pie',
              radius: ['40%', '70%'],
              data: chartData.data || [],
              label: { color: '#d3d6dd' },
              itemStyle: {
                borderColor: '#0f1325',
                borderWidth: 2
              }
            }]
          };
        }
  
        return null;
    },
    handleResize() {
        if (this.chartInstance) {
            this.chartInstance.resize();
        }
    }
  }
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


<!--<style lang="scss">
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
</style>-->
<style lang="scss">
#topic-result {
  padding: 0.15rem;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  
  .bg-color-black {
    flex: 1;
    display: flex;
    flex-direction: column;
    border-radius: 0.125rem;
  }
  
  .text {
    color: #c3cbde;
  }
  
  .chart-display-area {
    flex: 1;
    margin-top: 0.1rem;
    padding: 0 0.15rem 0.15rem;
    min-height: 400px; // 确保图表有足够空间
  }
  
  .chart-container {
    width: 100%;
    height: 100%;
    min-height: 400px;
  }
  
  .table-container {
    width: 100%;
    height: 100%;
    overflow-y: auto;
  }
}
</style>