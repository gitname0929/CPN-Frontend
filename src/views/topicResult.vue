
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
				style="width: 200px;"
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
import { fetchTopicData, loadFiguresConfig } from '@/api/topicApi';
import {
  buildTopicsFromConfig,
  buildChartOptionsForTopic,
} from '@/utils/figureParser';

export default {
  name: 'TopicResult',
  data() {
    return {
		currentTopic: 1,
		currentChart: '',
		chartInstance: null,
		isLoading: false,
		configLoading: true,
		figuresConfig: null,
		loadedChartData: null,
		loadedTableData: [],
    };
  },
  computed: {
    topics() {
        if (!this.figuresConfig) return [];
        return buildTopicsFromConfig(this.figuresConfig);
    },
    currentChartOptions() {
        if (!this.figuresConfig) return [];
        return buildChartOptionsForTopic(this.figuresConfig, this.currentTopic);
    },
    currentFigureMeta() {
        if (!this.figuresConfig || !this.currentChart) return null;
        const topic = this.figuresConfig.topics.find((t) => t.id === this.currentTopic);
        if (!topic) return null;
        return topic.figures.find((f) => f.id === this.currentChart) || null;
    },
    currentView() {
        if (!this.currentFigureMeta) return 'chart';
        return this.currentFigureMeta.type === 'table' ? 'table' : 'chart';
    },
    currentTableColumns() {
        if (this.loadedTableData && this.loadedTableData.length > 0) {
          return Object.keys(this.loadedTableData[0]);
        }
        return [];
    },
    currentTableData() {
        return this.loadedTableData || [];
    },
  },
  watch: {
    currentView(newVal) {
        if (newVal === 'chart') {
            this.$nextTick(() => {
                this.renderChart();
            });
        }
    }
  },
  async mounted() {
        try {
          this.figuresConfig = await loadFiguresConfig();
          if (this.topics.length > 0) {
            this.currentTopic = this.topics[0].id;
          }
          this.initDefaultSelection();
        } catch (error) {
          console.error('加载 figures 配置失败:', error);
        } finally {
          this.configLoading = false;
        }
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
    initDefaultSelection() {
        const options = this.currentChartOptions;
        if (options && options.length > 0) {
          this.currentChart = options[0].value;
          this.loadTopicData();
        }
    },
    onTopicChange() {
        const options = this.currentChartOptions;
        if (options && options.length > 0) {
          this.currentChart = options[0].value;
        }
        this.loadTopicData();
    },
    onChartChange() {
        this.loadTopicData();
    },
	
    async loadTopicData() {
        if (!this.currentChart) return;
        this.isLoading = true;
        try {
          const data = await fetchTopicData(this.currentTopic, this.currentChart);
          
		if (this.currentView === 'chart') {
            this.loadedChartData = data;
          } else {
            this.loadedTableData = data || [];
          }
        } catch (error) {
          console.error('加载课题数据失败:', error);
          this.loadedChartData = null;
          this.loadedTableData = [];
        } finally {
          this.isLoading = false;
          this.$nextTick(() => {
            if (this.currentView === 'chart' && this.loadedChartData) {
              this.renderChart();
            }
          });
        }
    },
    renderChart() {
        if (!this.loadedChartData) return;
        
        const container = this.$refs.chartContainer;
        if (!container) return;
  
        if (this.chartInstance) {
          this.chartInstance.dispose();
          this.chartInstance = null;
        }
  
        this.chartInstance = echarts.init(container);
        const option = this.buildChartOption(this.loadedChartData);
        if (option) {
          this.chartInstance.setOption(option);
        }
    },
    buildChartOption(chartData) {
        if (!chartData || !chartData.series) return null;
  
        const series = chartData.series.map((s, index) => {
          const colors = ['#00f0ff', '#ffd700', '#ff6b6b', '#4ecdc4', '#a855f7'];
          return {
            ...s,
            itemStyle: s.itemStyle || { color: colors[index % colors.length] },
            smooth: s.type === 'line' ? true : s.smooth,
          };
        });
  
        const legendData = series.map(s => s.name);
  
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
          grid: { left: '7%', right: '4%', bottom: '5%', top: '12%', containLabel: true },
        };// 增加底部空间给 x轴名称
  
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
		
    // 构建坐标轴配置，并添加名称
		const xAxis = {
			type: 'category',
			data: chartData.categories || [],
			axisLabel: { color: '#d3d6dd' },
			axisLine: { lineStyle: { color: 'rgba(0, 240, 255, 0.3)' } },
			axisTick: { show: false },
			// 新增横坐标名称
			name: chartData.xAxisName || '',
			nameLocation: 'middle',        // 名称居中
			nameGap: 30,                   // 与轴线的距离
			nameTextStyle: {
			color: '#a0c0e0',           // 柔和蓝白色，与大屏协调
			fontSize: 18,
			fontWeight: 'normal',
			}
		};
	
		const yAxis = {
			type: 'value',
			axisLabel: { color: '#d3d6dd' },
			splitLine: { lineStyle: { color: 'rgba(0, 240, 255, 0.1)' } },
			// 新增纵坐标名称
			name: chartData.yAxisName || '',
			nameLocation: 'middle',
			nameGap: 40,
			nameTextStyle: {
			color: '#a0c0e0',
			fontSize: 18,
			fontWeight: 'normal',
			}
		};

        return {
          ...baseOption,
		xAxis: xAxis,
		yAxis: yAxis,
		series: series,
        };
    },
    handleResize() {
        if (this.chartInstance) {
          this.chartInstance.resize();
        }
    },
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
    padding: 0.25rem 0.15rem 0.15rem;
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
	//课题2单选框
	.dataset-switch {
		display: flex;
		align-items: center;
		margin: 0.1rem 0;
		padding-left: 0.15rem;
		.dataset-label {
			color: #d3d6dd;
			font-size: 0.16rem;
			margin-right: 0.1rem;
		}
	}
}
</style>