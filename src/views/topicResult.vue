
<template>
  <div id="topic-result">
    <div class="bg-color-black" >
		


    <div class="border-box">
      <!-- 新增：课题选择器 + 运行按钮 -->
      <div class="task-selector-area">
        <el-select 
          v-model="selectedTopic" 
          placeholder="请选择课题"
          size="small"
          style="width: 180px; margin-right: 12px;">
        <el-option
          v-for="topic in topicList"
          :key="topic.id"
          :label="topic.name"
          :value="topic.id">
        </el-option>
        </el-select>
        <el-button 
          type="primary" 
          size="small" 
          :loading="runLoading"
          @click="openRunDialog">
          运行
        </el-button>
      </div>

  
	
  <div class="content-area">
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
    </div>
        </div><!--下方固定数据展示模块-->
        </div><!--边框容器包含整个左边-->


            <!-- 运行配置弹窗 -->
    <el-dialog
      :visible.sync="runDialogVisible"
      title="课题运行配置"
      width="700px"
      :close-on-click-modal="true"
      append-to-body
      @close="handleDialogClose"
    >
      <el-form :model="taskConfig" label-width="100px" size="small">
        <el-form-item label="CPU核心数">
          <el-input-number v-model="taskConfig.cpu" :min="0.5" :step="0.5" />
        </el-form-item>
        <el-form-item label="内存大小(GB)">
          <el-input-number v-model="taskConfig.memory" :min="1" :step="1" />
        </el-form-item>
        <el-form-item label="实例数量">
          <el-input-number v-model="taskConfig.instances" :min="1" :max="10" />
        </el-form-item>
        <el-form-item label="额外参数">
          <el-input v-model="taskConfig.extraArgs" placeholder="例如：--verbose --output=result.txt" />
        </el-form-item>
      </el-form>

      <!-- 实时输出控制台 -->
      <div class="output-console" v-if="taskRunning || outputLogs.length > 0">
        <div class="console-header">
          <span>运行输出</span>
          <el-button type="text" size="small" @click="clearOutput">清空</el-button>
        </div>
        <div class="console-body">
          <div v-for="(log, idx) in outputLogs" :key="idx" class="log-line">
            <span class="log-time">{{ log.time }}</span>
            <span :class="['log-text', log.type]">{{ log.text }}</span>
          </div>
          <div v-if="finalResult" class="final-result">
            <el-divider />
            <div class="result-title">最终结果：</div>
            <pre>{{ finalResult }}</pre>
          </div>
        </div>
      </div>

      <span slot="footer">
        <el-button @click="runDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="taskRunning" @click="handleRunTask">
          {{ taskRunning ? '运行中...' : '运行' }}
        </el-button>
      </span>
    </el-dialog>

  

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

// 新增：任务选择与运行
    selectedTopic: null,
    runLoading: false,
    runDialogVisible: false,
    taskRunning: false,
    taskConfig: {
      cpu: 1,
      memory: 2,
      instances: 1,
      extraArgs: ''
    },
    outputLogs: [],      // 输出日志数组
    finalResult: '',     // 最终结果
    abortController: null // 用于中断模拟请求
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
    },

    //新
    // 当课题列表加载完成后，默认选中第一个课题
    topics: {
      handler(newTopics) {
        if (newTopics.length && !this.selectedTopic) {
          this.selectedTopic = newTopics[0].id;
        }
      },
      immediate: true
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
    formatChartValue(point) {
        const raw = point && typeof point === 'object' && Object.prototype.hasOwnProperty.call(point, 'value')
          ? point.value
          : point;
        if (raw === null || raw === undefined || raw === '') return '';
        const n = Number(raw);
        if (!Number.isFinite(n)) return String(raw);
        const rounded = Math.round(n * 100) / 100;
        return Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(2);
    },
    formatChartLabel(point) {
        const value = this.formatChartValue(point);
        if (point && typeof point === 'object' && point.label) {
          return value ? `${value}\n${point.label}` : point.label;
        }
        return value;
    },
    formatVisibleChartLabel(point) {
        if (point && typeof point === 'object' && point.label) {
          return this.formatChartLabel(point);
        }
        return this.formatChartValue(point);
    },
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
          const hasExplicitLabels = Array.isArray(s.data)
            && s.data.some((point) => point && typeof point === 'object' && point.label);
          const showSeriesLabel = s.type === 'bar' || hasExplicitLabels;
          return {
            ...s,
            itemStyle: s.itemStyle || { color: colors[index % colors.length] },
            smooth: s.type === 'line' ? true : s.smooth,
            label: s.label || (showSeriesLabel ? {
              show: true,
              position: s.type === 'line' ? 'top' : 'top',
              distance: 6,
              color: '#d3d6dd',
              fontSize: 10,
              formatter: (params) => this.formatVisibleChartLabel(params.data),
            } : undefined),
          };
        });
  
        const legendData = series.map(s => s.name);
  
        const baseOption = {
          backgroundColor: 'transparent',
          tooltip: {
            trigger: series[0].type === 'pie' ? 'item' : 'axis',
            backgroundColor: 'rgba(15, 19, 37, 0.9)',
            borderColor: '#00f0ff',
            textStyle: { color: '#d3d6dd' },
            formatter: (params) => {
              if (!Array.isArray(params)) return '';
              const lines = [];
              if (params[0] && params[0].axisValue != null) {
                lines.push(params[0].axisValue);
              }
              params.forEach((item) => {
                const label = this.formatChartLabel(item.data);
                lines.push(`${item.marker} ${item.seriesName}: ${label}`);
              });
              return lines.join('<br/>');
            },
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


       // ---------- 新增：运行相关方法 ----------
    openRunDialog() {
      if (!this.selectedTopic) {
        this.$message.warning('请先选择课题');
        return;
      }
      // 重置弹窗状态
      this.outputLogs = [];
      this.finalResult = '';
      this.taskRunning = false;
      // 重置配置为默认值
      this.taskConfig = {
        cpu: 1,
        memory: 2,
        instances: 1,
        extraArgs: ''
      };
      this.runDialogVisible = true;
    },

    // 清空输出控制台
    clearOutput() {
      this.outputLogs = [];
      this.finalResult = '';
    },

    // 添加一条日志
    addLog(text, type = 'info') {
      this.outputLogs.push({
        time: new Date().toLocaleTimeString(),
        text: text,
        type: type
      });
      // 自动滚动到底部
      this.$nextTick(() => {
        const consoleBody = document.querySelector('.console-body');
        if (consoleBody) consoleBody.scrollTop = consoleBody.scrollHeight;
      });
    },

    // 模拟执行任务（可替换为真实后端调用）
    async mockRunTask(config) {
      const topic = this.topics.find(t => t.id === this.selectedTopic);
      const topicName = topic ? topic.name : `课题${this.selectedTopic}`;
      this.addLog(`[开始] 正在为课题「${topicName}」执行任务...`);
      this.addLog(`[配置] CPU: ${config.cpu}核, 内存: ${config.memory}GB, 实例数: ${config.instances}`);
      if (config.extraArgs) {
        this.addLog(`[参数] 额外参数: ${config.extraArgs}`);
      }
      
      // 模拟执行步骤
      await this.sleep(1000);
      this.addLog(`[步骤1] 连接集群调度器...`, 'info');
      await this.sleep(800);
      this.addLog(`[步骤2] 分配计算资源...`, 'info');
      await this.sleep(1200);
      this.addLog(`[步骤3] 启动容器实例...`, 'info');
      await this.sleep(1500);
      this.addLog(`[步骤4] 运行课题脚本...`, 'info');
      
      // 模拟脚本输出
      const outputs = [
        "Loading model...",
        "Processing data...",
        "Epoch 1/10: loss=0.234",
        "Epoch 2/10: loss=0.187",
        "Epoch 3/10: loss=0.152",
        "Validation accuracy: 94.7%"
      ];
      for (const line of outputs) {
        await this.sleep(600);
        this.addLog(`[脚本] ${line}`, 'stdout');
      }
      
      await this.sleep(1000);
      this.addLog(`[完成] 任务执行成功！`, 'success');
      const resultMsg = `课题「${topicName}」运行完成\n最终准确率: 94.7%\n输出文件: /output/result_${Date.now()}.txt`;
      this.finalResult = resultMsg;
      this.addLog(`[结果] ${resultMsg}`, 'result');
    },

    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },

    // 实际调用后端（替换 mockRunTask）
    async realRunTask(config) {
      try {
        // 使用 axios 或 this.$http 发送请求
        const response = await this.$http.post('/api/tasks/run', {
          topicId: this.selectedTopic,
          parameters: config
        });
        const taskId = response.data.taskId;
        // 轮询获取输出（或使用 WebSocket/SSE）
        this.addLog(`任务已提交，ID: ${taskId}`);
        // 示例：轮询结果接口
        const pollInterval = setInterval(async () => {
          const res = await this.$http.get(`/api/tasks/${taskId}/status`);
          if (res.data.logs) {
            res.data.logs.forEach(log => this.addLog(log, 'stdout'));
          }
          if (res.data.status === 'completed') {
            this.finalResult = res.data.result;
            clearInterval(pollInterval);
            this.taskRunning = false;
          } else if (res.data.status === 'failed') {
            this.addLog(`执行失败: ${res.data.error}`, 'error');
            clearInterval(pollInterval);
            this.taskRunning = false;
          }
        }, 1000);
      } catch (error) {
        this.addLog(`请求失败: ${error.message}`, 'error');
        this.taskRunning = false;
      }
    },

    // 处理运行按钮点击
    async handleRunTask() {
      if (this.taskRunning) return;
      this.taskRunning = true;
      this.outputLogs = [];
      this.finalResult = '';
      
      // 这里选择使用模拟执行（便于测试弹窗效果），实际使用请改为 realRunTask
      await this.mockRunTask(this.taskConfig);
      
      // 如果使用真实后端，调用 this.realRunTask(this.taskConfig)
      this.taskRunning = false;
    },

    handleDialogClose() {
      console.log('关闭弹窗');
      // 如果任务还在运行，提示关闭会中断
      if (this.taskRunning) {
        this.$confirm('任务正在运行，关闭弹窗将中断任务，是否继续？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          if (this.abortController) {
            this.abortController.abort();
          }
          this.taskRunning = false;
          this.runDialogVisible = false;
        }).catch(() => {});
      } else {
        this.runDialogVisible = false;
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

  .border-box {
    flex: 1;
    display: flex;
    flex-direction: column;
    border: 1px solid rgba(0, 240, 255, 0.3);
    border-radius: 0.125rem;
    padding: 0.12rem 0.1rem 0.1rem 0.1rem;
    background: rgba(0, 0, 0, 0.3);
  }//新
  .task-selector-area {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0.08rem 0 0.12rem 0;
    border-bottom: 1px dashed rgba(0, 240, 255, 0.2);
    margin-bottom: 0.08rem;
  }//新
  .content-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0; // 防止溢出
  }//新
  
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




  // 弹窗内输出控制台样式
  .output-console {
    margin-top: 16px;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    background: #1e1e1e;
    
    .console-header {
      padding: 8px 12px;
      border-bottom: 1px solid #e4e7ed;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #2d2d2d;
      color: #ddd;
      font-weight: bold;
    }
    
    .console-body {
      height: 280px;
      overflow-y: auto;
      padding: 8px 12px;
      font-family: 'Consolas', monospace;
      font-size: 12px;
      color: #d4d4d4;
      
      .log-line {
        margin-bottom: 4px;
        line-height: 1.4;
        
        .log-time {
          color: #858585;
          margin-right: 12px;
        }
        
        .log-text {
          &.info { color: #d4d4d4; }
          &.stdout { color: #ce9178; }
          &.error { color: #f48771; }
          &.success { color: #4ec9b0; }
          &.result { color: #ffd700; font-weight: bold; }
        }
      }
      
      .final-result {
        pre {
          background: #2d2d2d;
          padding: 8px;
          border-radius: 4px;
          overflow-x: auto;
          color: #dcdcaa;
          margin-top: 8px;
        }
        .result-title {
          font-weight: bold;
          margin: 8px 0 4px;
          color: #4ec9b0;
        }
      }
    }
  }
}
</style>
