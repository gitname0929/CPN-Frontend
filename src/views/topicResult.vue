
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
			{ label: '图1：性能对比图', value: 'chart1'},
			{ label: '表1：昇腾测试数据', value: 'table1' },
			{ label: '表2：飞腾测试数据', value: 'table2' },
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
				series:[
				{
					name: '昇腾性能提升比(%)',
					type: 'line',
					data: [
					81.27,
					77.06,
					80.05,
					79.83,
					72.43,
					80.80,
					79.65,
					82.46,
					77.55,
					80.96,
					81.25,
					73.68,
					72.53,
					70.93,
					72.18,
					69.23,
					87.75,
					84.48,
					87.68,
					88.52,
					89.03]
				},
				{
					name: '飞腾性能提升比(%)',
					type: 'line',
					data: [
					70.44,
					65.97,
					73.75,
					73.13,
					63.42,
					69.46,
					68.06,
					73.02,
					67.21,
					67.33,
					73.90,
					64.37,
					69.53,
					61.32,
					64.99,
					61.55,
					80.88,
					81.39,
					81.61,
					80.01,
					78.01					]
				},
				{
					name: 'KPI要求',
					type: 'line',
					data: [40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40]
				}
				],
				categories: [
				'deit_tiny_patch_16_224',
				'levit_128',
				'mobilenet_v2',
				'mobilenet_v3_large',
				'resnet101',
				'resnet18',
				'resnet50',
				'mobilevgg',
				'lightvgg11',
				'yolo5s',
				'yolov8n',
				'sampler_cpu',
				'sampler_ram',
				'sampler_gpu',
				'sampler_internet',
				'sampler_power',
				'plot_cpu',
				'plot_ram',
				'plot_gpu',
				'plot_internet',
				'plot_power'],
				

				/*name: 'CPU使用率',
				type: 'line',
				categories: ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00'],
				values: [45, 52, 48, 60, 55, 70]*/
			},
			chart2: { /* 柱状图数据 */
				series: [
				{
					name: '节点A',
					type: 'bar',
					data: [120, 200, 150, 80]
				},
				{
					name: '节点B',
					type: 'bar',
					data: [90, 180, 130, 110]
				}
				],
				categories: ['CPU', '内存', '磁盘', '网络']
			},
			table1:[ /* 表格数据 */ 
				{ model: 'deit_tiny_patch_16_224', 暖到热: '0.81', 冷到热: '2.76', 性能提升比: '70.44' },
				{ model: 'levit_128', 暖到热: '0.93', 冷到热: '2.75', 性能提升比: '65.97' },
				{ model: 'mobilenet_v2', 暖到热: '0.74', 冷到热: '2.81', 性能提升比: '73.75' },
				{ model: 'mobilenet_v3_large', 暖到热: '0.71', 冷到热: '2.65', 性能提升比: '73.13' },
				{ model: 'resnet101', 暖到热: '1.10', 冷到热: '3.02', 性能提升比: '63.42' },
				{ model: 'resnet18', 暖到热: '0.69', 冷到热: '2.26', 性能提升比: '69.46' },
				{ model: 'resnet50', 暖到热: '0.87', 冷到热: '2.72', 性能提升比: '68.06' },
				{ model: 'mobilevgg', 暖到热: '0.68', 冷到热: '2.51', 性能提升比: '73.02' },
				{ model: 'lightvgg11', 暖到热: '1.04', 冷到热: '3.19', 性能提升比: '67.21' },
				{ model: 'yolo5s', 暖到热: '0.88', 冷到热: '2.69', 性能提升比: '67.33' },
				{ model: 'yolov8n', 暖到热: '0.79', 冷到热: '3.04', 性能提升比: '73.90' },
				{ model: 'sampler_cpu', 暖到热: '1.00', 冷到热: '2.81', 性能提升比: '64.37' },
				{ model: 'sampler_ram', 暖到热: '0.82', 冷到热: '2.68', 性能提升比: '69.53' },
				{ model: 'sampler_gpu', 暖到热: '1.14', 冷到热: '2.95', 性能提升比: '61.32' },
				{ model: 'sampler_internet', 暖到热: '0.97', 冷到热: '2.78', 性能提升比: '64.99' },
				{ model: 'sampler_power', 暖到热: '0.97', 冷到热: '2.52', 性能提升比: '61.55' },
				{ model: 'plot_cpu', 暖到热: '0.50', 冷到热: '2.63', 性能提升比: '80.88' },
				{ model: 'plot_ram', 暖到热: '0.51', 冷到热: '2.75', 性能提升比: '81.39' },
				{ model: 'plot_gpu', 暖到热: '0.48', 冷到热: '2.61', 性能提升比: '81.61' },
				{ model: 'plot_internet', 暖到热: '0.50', 冷到热: '2.52', 性能提升比: '80.01' },
				{ model: 'plot_power', 暖到热: '0.55', 冷到热: '2.52', 性能提升比: '78.01' },
			],
			table2: [ /* 表格数据 */
				{ model: 'deit_tiny_patch_16_224', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'levit_128', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'mobilenet_v2', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'mobilenet_v3_large', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'resnet101', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'resnet18', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'resnet50', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'mobilevgg', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'lightvgg11', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'yolo5s', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'yolov8n', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'sampler_cpu', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'sampler_ram', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'sampler_gpu', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'sampler_internet', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'sampler_power', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'plot_cpu', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'plot_ram', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'plot_gpu', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'plot_internet', 暖到热: '', 冷到热: '', 性能提升比: '' },
				{ model: 'plot_power', 暖到热: '', 冷到热: '', 性能提升比: '' },
			],
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
        // if (this.currentChart === 'table') return 'table';
        // if (this.currentChart && this.currentChart.startsWith('chart')) return 'chart';
		if (!this.currentChart) return 'chart';
		return this.currentChart.startsWith('table') ? 'table' : 'chart';
        //return 'chart'; // 默认图表
    },
	/*
	      重点修改4：新增计算属性 currentTableKey，用于定位当前表格数据。
	      例如 currentChart 为 'table1'，则取 topicData[当前课题].table1
	    */
	currentTableKey() {
		// 如果当前是表格视图，直接返回 currentChart 作为键名
		return this.currentView === 'table' ? this.currentChart : null;
	},
    // 当前表格列名
    currentTableColumns() {
		const key = this.currentTableKey;
		if (!key) return [];
        const tableData = this.topicData[this.currentTopic]?.[key];
        if (tableData && tableData.length > 0) {
          return Object.keys(tableData[0]);
        }
        return [];
    },
    // 当前表格数据
    currentTableData() {
        const key = this.currentTableKey;
        if (!key) return [];
        return this.topicData[this.currentTopic]?.[key] || [];
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
	// 通用图表配置构建（支持 legend）
	buildChartOption(chartData) {
		if (!chartData || !chartData.series) return null;

		const series = chartData.series.map((s, index) => {
		// 为没有指定颜色的系列自动分配颜色（可选）
			const colors = ['#00f0ff', '#ffd700', '#ff6b6b', '#4ecdc4', '#a855f7'];
			return {
			...s,
			itemStyle: s.itemStyle || { color: colors[index % colors.length] },
			// 折线图默认平滑
			smooth: s.type === 'line' ? true : s.smooth,
			};
		});

		// 图例数据（从系列 name 提取）
		const legendData = series.map(s => s.name);

		// 基础配置
		const baseOption = {
			backgroundColor: 'transparent',
			tooltip: {
				trigger: series[0].type === 'pie' ? 'item' : 'axis',
				backgroundColor: 'rgba(15, 19, 37, 0.9)',
				borderColor: '#00f0ff',
				textStyle: { color: '#d3d6dd' }
			},
			legend: {
				data: legendData,
				textStyle: { color: '#d3d6dd' },
				top: 0,
				left: 'center',
			},
			grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
		};

		// 饼图特殊处理
		if (series[0].type === 'pie') {
			return {
			...baseOption,
			legend: {
				...baseOption.legend,
				top: 'middle',
				left: 'left',
				orient: 'vertical',
			},
			series: series,
			};
		}

		// 直角坐标系图表（折线、柱状等）
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
			series: series,
		};
	},
	handleResize() {
		if (this.chartInstance) {
			this.chartInstance.resize();
		}
	}
  }
};
</script>

<!--原上下
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
  height: 100%; //确保撑满父级
  padding: 0.15rem;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  
  .bg-color-black {
    flex: 1;
    display: flex;
    flex-direction: column;
    border-radius: 0.125rem;
	overflow: hidden;//防止内容溢出
  }
  
  .text {
    color: #c3cbde;
  }
  
  .chart-display-area {
    flex: 1;
	padding: 0 0.15rem 0.15rem;
	min-height: 0;//让 flex 子元素可以正确收缩
    margin-top: 0.1rem;
    padding: 0 0.15rem 0.15rem;
    //min-height: 400px; // 确保图表有足够空间
  }
  
  .chart-container {
	flex: 1;
    width: 100%;
    height: 90%;// 确定图 展示占据的比例
    min-height: 0;//400px;// 必须设置，否则 ECharts 不会自动填充
  }
  
  .table-container {
    width: 100%;
    height: 100%;
    overflow-y: auto;
  }
  .table-container {
    flex: 1;
    overflow-y: auto;      // 表格内容过多时可滚动
    padding-right: 5px;    // 滚动条留白
  
    // 美化滚动条（可选）
    &::-webkit-scrollbar {
      width: 6px;
    }
    &::-webkit-scrollbar-track {
      background: rgba(0, 240, 255, 0.05);
    }
    &::-webkit-scrollbar-thumb {
      background: rgba(0, 240, 255, 0.3);
      border-radius: 3px;
    }
  }
  
  // 大屏表格样式优化
  .data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.16rem;    // 增大字体
      line-height: 1.8;      // 增加行高
      
      th {
        background-color: rgba(0, 240, 255, 0.2);
        color: #00f0ff;
        padding: 0.12rem 0.15rem;
        border: 1px solid rgba(0, 240, 255, 0.3);
        text-align: center;
        font-weight: 500;
        white-space: nowrap;
      }
  
      td {
        padding: 0.1rem 0.15rem;
        border: 1px solid rgba(0, 240, 255, 0.15);
        text-align: center;
        color: #d3d6dd;
        white-space: nowrap;
      }
  
      tbody tr {
        transition: background-color 0.2s;
        &:hover {
          background-color: rgba(0, 240, 255, 0.08);
        }
      }
    }
}
</style>