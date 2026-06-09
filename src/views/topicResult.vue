
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
        <el-button
          type="warning"
          size="small"
          :loading="cleanupLoading"
          @click="handleCleanupPods">
          清理 pods 环境
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
      custom-class="topic-run-dialog"
      :before-close="handleDialogClose"
    >
      <el-form :model="taskConfig" label-width="100px" size="small">
        <el-form-item label="课题">
          <el-select v-model="selectedTopic" placeholder="请选择课题" style="width: 100%;">
            <el-option
              v-for="topic in topicList"
              :key="topic.id"
              :label="topic.name"
              :value="topic.id"
            />
          </el-select>
        </el-form-item>

        <template v-if="normalizedSelectedTopic === 1">
          <el-form-item label="硬件平台">
            <el-select v-model="taskConfig.platform" placeholder="请选择硬件平台" style="width: 100%;">
              <el-option label="昇腾" value="ascend" />
              <el-option label="飞腾" value="feiteng" />
            </el-select>
          </el-form-item>
          <el-form-item label="运行模型">
            <el-select
              v-model="taskConfig.models"
              multiple
              collapse-tags
              placeholder="请选择要运行的模型"
              style="width: 100%;"
              @change="onModelsChange"
            >
              <el-option label="全部 (all)" value="all" />
              <el-option
                v-for="model in modelOptions"
                :key="model"
                :label="model"
                :value="model"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="执行轮数">
            <el-input-number
              v-model="taskConfig.rounds"
              :min="1"
              :max="9999"
              :step="1"
              style="width: 100%;"
            />
          </el-form-item>
        </template>

        <template v-else-if="normalizedSelectedTopic === 2">
          <el-form-item label="板子类型">
            <el-select v-model="taskConfig.board" placeholder="请选择板子类型" style="width: 100%;">
              <el-option label="昇腾 (st)" value="st" />
              <el-option label="飞腾 (ft)" value="ft" />
            </el-select>
          </el-form-item>
          <el-form-item label="数据集分组">
            <el-select v-model="taskConfig.dataset_group" placeholder="请选择数据集分组" style="width: 100%;">
              <el-option label="google (1-5号任务)" value="google" />
              <el-option label="huawei (6-10号任务)" value="huawei" />
            </el-select>
          </el-form-item>
          <el-form-item label="负载等级">
            <el-select v-model="taskConfig.load_level" placeholder="请选择负载等级" style="width: 100%;">
              <el-option label="L (低负载)" value="L" />
              <el-option label="H (高负载)" value="H" />
            </el-select>
          </el-form-item>
        </template>

        <template v-else-if="normalizedSelectedTopic === 3">
          <el-form-item label="运行场景">
            <el-select v-model="taskConfig.scenario" placeholder="请选择运行场景" style="width: 100%;">
              <el-option label="昇腾 server / 昇腾 client" value="ascend_ascend" />
              <el-option label="昇腾 server / 飞腾 client" value="ascend_feiteng" />
              <el-option label="昇腾 server / 飞腾 client + 昇腾 client" value="ascend_mixed" />
            </el-select>
          </el-form-item>
          <el-form-item label="运行模型">
            <el-select
              v-model="taskConfig.models"
              multiple
              collapse-tags
              placeholder="请选择运行模型"
              style="width: 100%;"
              @change="onTopic3ModelsChange"
            >
              <el-option label="全部 (all)" value="all" />
              <el-option
                v-for="model in topic3ModelOptions"
                :key="model"
                :label="model"
                :value="model"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="统计次数">
            <el-input-number
              v-model="taskConfig.numTasks"
              :min="1"
              :max="1000"
              :step="1"
              style="width: 100%;"
            />
          </el-form-item>
          <el-form-item label="服务端口">
            <el-input-number
              v-model="taskConfig.port"
              :min="1024"
              :max="65535"
              :step="1"
              style="width: 100%;"
            />
          </el-form-item>
          <el-alert
            title="昇腾 server IP: 192.168.31.154；昇腾 client IP: 192.168.31.247；飞腾 client 为当前机器。支持 1飞1昇双客户端；默认额外预热 5 次，预热不计入统计。"
            type="info"
            :closable="false"
            show-icon
          />
        </template>

        <template v-else-if="normalizedSelectedTopic === 4">
          <el-form-item label="执行设备">
            <el-select v-model="taskConfig.device" placeholder="请选择执行设备" style="width: 100%;">
              <el-option label="昇腾 (192.168.31.179)" value="ascend" />
              <el-option label="飞腾 (本机)" value="feiteng" />
            </el-select>
          </el-form-item>
          <el-form-item label="总轮数">
            <el-input-number
              v-model="taskConfig.rounds"
              :min="1"
              :max="10000"
              :step="1"
              style="width: 100%;"
            />
          </el-form-item>
          <el-alert
            title="昇腾定向调用 192.168.31.179；飞腾只调用本机 127.0.0.1，避免被负载均衡。请求强度固定为 8 req/s。"
            type="info"
            :closable="false"
            show-icon
          />
        </template>

        <el-form-item v-else>
          <el-alert
            title="该课题的运行配置暂未开放"
            type="info"
            :closable="false"
            show-icon
          />
        </el-form-item>
      </el-form>

      <!-- 执行进度 + 执行结果（各自固定高度，独立滚动） -->
      <div class="run-output-area" v-if="taskRunning || outputLogs.length > 0 || resultRows.length > 0 || taskError">
        <div class="output-console">
          <div class="console-header">
            <span>执行进度</span>
            <el-button type="text" size="small" @click="clearOutput">清空</el-button>
          </div>
          <div class="console-body" ref="consoleBody">
            <div v-if="outputLogs.length === 0" class="log-placeholder">等待输出...</div>
            <div v-for="(log, idx) in outputLogs" :key="idx" class="log-line">
              <span class="log-time">{{ log.time }}</span>
              <span :class="['log-text', log.type]">{{ log.text }}</span>
            </div>
          </div>
        </div>

        <div class="result-panel" v-if="taskRunning || taskFinished || resultRows.length > 0 || taskError">
          <div class="console-header">
            <span>执行结果</span>
          </div>
          <div class="result-body" ref="resultBody">
            <div v-if="resultRows.length > 0" class="result-table-wrap">
              <table class="result-table">
                <thead>
                  <tr>
                    <th v-for="column in resultColumns" :key="column">{{ column }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in resultRows" :key="index">
                    <td v-for="column in resultColumns" :key="column">{{ formatResultValue(row[column]) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else-if="taskError" class="result-error">
              <div class="result-title error-text">执行失败</div>
              <pre>{{ taskError }}</pre>
            </div>
            <div v-else-if="taskFinished" class="log-placeholder">任务已完成，暂无结果数据</div>
            <div v-else class="log-placeholder">等待结果...</div>
          </div>
        </div>
      </div>

      <span slot="footer">
        <el-button @click="requestCloseDialog">取消</el-button>
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
  runTopicTask,
  getTopicTaskResult,
  cancelTopicTask,
  cleanupPodsEnvironment,
  createTopicTaskStream,
} from '@/api/taskApi';
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

// 任务选择与运行
    topicList: [
      { id: 1, name: '课题一' },
      { id: 2, name: '课题二' },
      { id: 3, name: '课题三' },
      { id: 4, name: '课题四' },
    ],
    modelOptions: [
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
      'plot_power',
    ],
    topic3ModelOptions: [
      'deit_tiny_patch_16_224',
      'levit_128',
      'mobilenet_v2',
      'mobilenet_v3_large',
      'resnet101',
      'resnet18',
      'resnet50',
      'mobilevgg',
      'lightvgg11',
      'yolov5',
      'yolov8',
    ],
    selectedTopic: 1,
    runLoading: false,
    cleanupLoading: false,
    runDialogVisible: false,
    taskRunning: false,
    taskConfig: {
      platform: '',
      models: [],
      rounds: 300,
      board: '',
      dataset_group: '',
      load_level: '',
      scenario: '',
      model: 'resnet50',
      device: '',
      numTasks: 215,
      port: 9999,
    },
    outputLogs: [],
    resultRows: [],
    resultColumns: [],
    taskFinished: false,
    taskError: '',
    currentTaskId: null,
    eventSource: null,
    resultPollTimer: null,
    abortController: null
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
    normalizedSelectedTopic() {
        const topic = Number(this.selectedTopic);
        return Number.isFinite(topic) ? topic : this.selectedTopic;
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
    this.stopTaskWatchers();
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


    getDefaultTaskConfig() {
      return {
        platform: '',
        models: [],
        rounds: this.normalizedSelectedTopic === 4 ? 300 : 1,
        board: '',
        dataset_group: '',
        load_level: '',
        scenario: '',
        model: 'resnet50',
        device: '',
        numTasks: 215,
        port: 9999,
      };
    },

    onModelsChange(selected) {
      if (!selected.includes('all')) return;
      if (selected.length === 1) {
        this.taskConfig.models = ['all', ...this.modelOptions];
        return;
      }
      this.taskConfig.models = selected.filter((item) => item !== 'all');
    },

    onTopic3ModelsChange(selected) {
      if (!selected.includes('all')) return;
      if (selected.length === 1) {
        this.taskConfig.models = ['all', ...this.topic3ModelOptions];
        return;
      }
      this.taskConfig.models = selected.filter((item) => item !== 'all');
    },

    validateTaskConfig() {
      if (!this.selectedTopic) {
        this.$message.warning('请先选择课题');
        return false;
      }
      const topicId = this.normalizedSelectedTopic;
      if (topicId === 2) {
        if (!this.taskConfig.board) {
          this.$message.warning('请选择板子类型');
          return false;
        }
        if (!this.taskConfig.dataset_group) {
          this.$message.warning('请选择数据集分组');
          return false;
        }
        if (!this.taskConfig.load_level) {
          this.$message.warning('请选择负载等级');
          return false;
        }
        return true;
      }
      if (topicId === 3) {
        if (!this.taskConfig.scenario) {
          this.$message.warning('请选择运行场景');
          return false;
        }
        if (!this.taskConfig.models.length) {
          this.$message.warning('请选择运行模型');
          return false;
        }
        if (!this.taskConfig.numTasks || this.taskConfig.numTasks < 1) {
          this.$message.warning('统计次数至少为 1');
          return false;
        }
        if (!this.taskConfig.port || this.taskConfig.port < 1024) {
          this.$message.warning('请填写有效服务端口');
          return false;
        }
        return true;
      }
      if (topicId === 4) {
        if (!this.taskConfig.device) {
          this.$message.warning('请选择执行设备');
          return false;
        }
        if (!this.taskConfig.rounds || this.taskConfig.rounds < 1) {
          this.$message.warning('总轮数至少为 1');
          return false;
        }
        return true;
      }
      if (topicId !== 1) {
        this.$message.info('该课题运行配置暂未开放');
        return false;
      }
      if (!this.taskConfig.platform) {
        this.$message.warning('请选择硬件平台');
        return false;
      }
      if (!this.taskConfig.models.length) {
        this.$message.warning('请至少选择一个模型');
        return false;
      }
      if (!this.taskConfig.rounds || this.taskConfig.rounds < 1) {
        this.$message.warning('执行轮数至少为 1');
        return false;
      }
      return true;
    },

    buildRunPayload() {
      const topicId = this.normalizedSelectedTopic;
      if (topicId === 2) {
        return {
          topicId,
          board: this.taskConfig.board,
          dataset_group: this.taskConfig.dataset_group,
          load_level: this.taskConfig.load_level,
        };
      }
      if (topicId === 3) {
        const models = this.taskConfig.models.includes('all')
          ? [...this.topic3ModelOptions]
          : [...this.taskConfig.models];
        return {
          topicId,
          scenario: this.taskConfig.scenario,
          models,
          numTasks: this.taskConfig.numTasks,
          port: this.taskConfig.port,
        };
      }
      if (topicId === 4) {
        return {
          topicId,
          device: this.taskConfig.device,
          rounds: this.taskConfig.rounds,
        };
      }
      const models = this.taskConfig.models.includes('all')
        ? ['all']
        : [...this.taskConfig.models];
      return {
        topicId,
        platform: this.taskConfig.platform,
        models,
        rounds: this.taskConfig.rounds,
      };
    },

    openRunDialog() {
      this.stopTaskWatchers();
      this.outputLogs = [];
      this.resultRows = [];
      this.resultColumns = [];
      this.taskFinished = false;
      this.taskError = '';
      this.taskRunning = false;
      this.taskConfig = this.getDefaultTaskConfig();
      this.runDialogVisible = true;
    },

    stopTaskWatchers() {
      if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
      }
      if (this.resultPollTimer) {
        clearTimeout(this.resultPollTimer);
        this.resultPollTimer = null;
      }
    },

    formatResultValue(value) {
      if (value === null || value === undefined || value === '') return '-';
      return value;
    },

    // 清空输出控制台
    clearOutput() {
      this.outputLogs = [];
      this.resultRows = [];
      this.resultColumns = [];
      this.taskFinished = false;
      this.taskError = '';
    },

    async handleCleanupPods() {
      if (this.cleanupLoading) return;
      try {
        await this.$confirm('将把模型与异构任务 Deployment 缩容到 0，是否继续？', '清理 pods 环境', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });
      } catch (error) {
        return;
      }
      this.cleanupLoading = true;
      try {
        await cleanupPodsEnvironment();
        this.$message.success('pods 环境清理完成');
        this.addLog('[清理] 已将模型与异构任务 Deployment 缩容到 0', 'success');
      } catch (error) {
        const message = error.message || '清理 pods 环境失败';
        this.$message.error(message);
        this.addLog(`[清理失败] ${message}`, 'error');
      } finally {
        this.cleanupLoading = false;
      }
    },

    // 添加一条日志
    addLog(text, type = 'info') {
      const isProgressLine = typeof text === 'string' && /^已执行\s+\d+\/\d+$/.test(text);
      if (isProgressLine) {
        const lastIndex = this.outputLogs.length - 1;
        if (lastIndex >= 0) {
          const lastLog = this.outputLogs[lastIndex];
          if (lastLog && /^已执行\s+\d+\/\d+$/.test(lastLog.text || '')) {
            this.$set(this.outputLogs, lastIndex, {
              ...lastLog,
              time: new Date().toLocaleTimeString(),
              text,
              type,
            });
            this.$nextTick(() => {
              const consoleBody = this.$refs.consoleBody;
              if (consoleBody) consoleBody.scrollTop = consoleBody.scrollHeight;
            });
            return;
          }
        }
      }
      this.outputLogs.push({
        time: new Date().toLocaleTimeString(),
        text: text,
        type: type
      });
      this.$nextTick(() => {
        const consoleBody = this.$refs.consoleBody;
        if (consoleBody) consoleBody.scrollTop = consoleBody.scrollHeight;
      });
    },

    applyTaskResult(result) {
      if (result.status === 'completed') {
        this.taskFinished = true;
        this.resultRows = this.normalizeTaskResultRows(result);
        this.resultColumns = this.buildResultColumns(this.resultRows);
        this.taskError = '';
        this.addLog(`任务完成，共 ${this.resultRows.length} 条结果`, 'success');
        this.$nextTick(() => this.scrollResultToTop());
        return;
      }
      if (result.status === 'failed') {
        this.taskFinished = true;
        this.resultRows = this.normalizeTaskResultRows(result);
        this.resultColumns = this.buildResultColumns(this.resultRows);
        this.taskError = result.error || '任务执行失败';
        this.addLog(this.taskError, 'error');
      }
    },

    normalizeTaskResultRows(result) {
      const rows = result.rows || result.resultRows || result.output || result.result || [];
      const parsedRows = Array.isArray(rows) ? rows : [];
      if (this.normalizedSelectedTopic === 2 || this.normalizedSelectedTopic === 3 || this.normalizedSelectedTopic === 4) {
        return parsedRows.map((row) => ({ ...row }));
      }
      return parsedRows.map((row) => ({
        '模型': this.pickResultValue(row, ['model', 'Model', '模型']) || '',
        '平均冷到热时间(s)': this.pickResultValue(row, ['avgColdToHot', 'avg_cold_start_sec', '平均冷到热时间(s)']),
        '平均暖到热时间(s)': this.pickResultValue(row, ['avgWarmToHot', 'avg_warm_start_sec', '平均暖到热时间(s)']),
        '提升比值(%)': this.pickResultValue(row, ['improvementRatio', 'theta_percent', '提升比值(%)']),
      }));
    },

    buildResultColumns(rows) {
      if (!rows.length) return [];
      const columns = [];
      rows.forEach((row) => {
        Object.keys(row).forEach((key) => {
          if (!columns.includes(key)) columns.push(key);
        });
      });
      return columns;
    },

    pickResultValue(row, keys) {
      for (const key of keys) {
        if (Object.prototype.hasOwnProperty.call(row, key)) {
          return row[key];
        }
      }
      return undefined;
    },

    scrollResultToTop() {
      const resultBody = this.$refs.resultBody;
      if (resultBody) resultBody.scrollTop = 0;
    },

    pollTaskResult(taskId) {
      getTopicTaskResult(taskId)
        .then((result) => {
          if (result.status === 'running') {
            this.resultPollTimer = setTimeout(() => this.pollTaskResult(taskId), 1500);
            return;
          }
          this.applyTaskResult(result);
          this.taskRunning = false;
          this.stopTaskWatchers();
        })
        .catch((error) => {
          this.taskError = error.message || '获取任务结果失败';
          this.addLog(this.taskError, 'error');
          this.taskRunning = false;
          this.stopTaskWatchers();
        });
    },

    async handleRunTask() {
      if (this.taskRunning) return;
      if (!this.validateTaskConfig()) return;

      const payload = this.buildRunPayload();
      this.taskRunning = true;
      this.outputLogs = [];
      this.resultRows = [];
      this.resultColumns = [];
      this.taskFinished = false;
      this.taskError = '';
      this.stopTaskWatchers();

      if (payload.topicId === 2) {
        const boardLabel = payload.board === 'st' ? '昇腾' : '飞腾';
        this.addLog(`[配置] 课题二 / ${boardLabel} / ${payload.dataset_group} / ${payload.load_level}`, 'info');
      } else if (payload.topicId === 3) {
        const scenarioMap = {
          ascend_ascend: '昇腾 server / 昇腾 client',
          ascend_feiteng: '昇腾 server / 飞腾 client',
          ascend_mixed: '昇腾 server / 飞腾 client + 昇腾 client',
        };
        const scenarioLabel = scenarioMap[payload.scenario] || payload.scenario;
        this.addLog(`[配置] 课题三 / ${scenarioLabel} / ${payload.models.join(', ')} / 统计 ${payload.numTasks} 次 / 预热 5 次`, 'info');
      } else if (payload.topicId === 4) {
        const deviceLabel = payload.device === 'ascend' ? '昇腾 192.168.31.179' : '飞腾 本机';
        this.addLog(`[配置] 课题四 / ${deviceLabel} / 总轮数 ${payload.rounds} / 请求强度 8 req/s`, 'info');
      } else {
        const platformLabel = payload.platform === 'ascend' ? '昇腾' : '飞腾';
        this.addLog(`[配置] 课题一 / ${platformLabel} / 轮数 ${payload.rounds}`, 'info');
        this.addLog(`[模型] ${payload.models.join(', ')}`, 'info');
      }

      try {
        const { taskId } = await runTopicTask(payload);
        this.currentTaskId = taskId;
        this.addLog(`[任务] 已启动，ID: ${taskId}`, 'info');

        this.eventSource = createTopicTaskStream(taskId, (logData) => {
          this.addLog(logData.message, logData.type || 'stdout');
        });
        this.eventSource.onerror = () => {
          if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
          }
        };

        this.pollTaskResult(taskId);
      } catch (error) {
        this.taskError = error.message || '启动任务失败';
        this.taskFinished = true;
        this.addLog(this.taskError, 'error');
        this.taskRunning = false;
        this.stopTaskWatchers();
      }
    },

    requestCloseDialog() {
      this.handleDialogClose(() => {
        this.runDialogVisible = false;
      });
    },

    handleDialogClose(done) {
      if (this.taskRunning) {
        this.$confirm('任务正在运行，关闭弹窗将中断任务，是否继续？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          if (this.currentTaskId) {
            cancelTopicTask(this.currentTaskId).catch(() => {});
          }
          this.stopTaskWatchers();
          this.taskRunning = false;
          if (typeof done === 'function') done();
        }).catch(() => {});
      } else {
        this.stopTaskWatchers();
        if (typeof done === 'function') done();
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




}
</style>

<!-- 弹窗 append-to-body 后不在 #topic-result 内，样式须单独写 -->
<style lang="scss">
.topic-run-dialog {
  .el-dialog__body {
    max-height: calc(100vh - 200px);
    overflow-x: hidden;
    overflow-y: auto;
    padding-bottom: 16px;
  }

  .run-output-area {
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 12px;

    .log-placeholder {
      color: #858585;
      font-style: italic;
      font-size: 12px;
      padding: 4px 0;
    }
  }

  .output-console,
  .result-panel {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    background: #1e1e1e;
    overflow: hidden;
    flex-shrink: 0;

    .console-header {
      padding: 8px 12px;
      border-bottom: 1px solid #dcdfe6;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #2d2d2d;
      color: #ddd;
      font-weight: bold;
    }
  }

  .output-console .console-body {
    height: 200px;
    max-height: 200px;
    overflow-y: scroll;
    overflow-x: hidden;
    padding: 8px 12px;
    box-sizing: border-box;
    font-family: Consolas, monospace;
    font-size: 12px;
    color: #d4d4d4;

    .log-line {
      margin-bottom: 4px;
      line-height: 1.4;
      word-break: break-all;

      .log-time {
        color: #858585;
        margin-right: 12px;
        white-space: nowrap;
      }

      .log-text.info { color: #d4d4d4; }
      .log-text.stdout { color: #ce9178; }
      .log-text.error { color: #f48771; }
      .log-text.success { color: #4ec9b0; }
      .log-text.result { color: #ffd700; font-weight: bold; }
    }
  }

  .result-panel .result-body {
    height: 160px;
    max-height: 160px;
    overflow-y: scroll;
    overflow-x: auto;
    padding: 8px 12px;
    box-sizing: border-box;
    background: #1e1e1e;

    .result-error pre {
      background: #2d2d2d;
      padding: 8px;
      border-radius: 4px;
      color: #dcdcaa;
      margin: 0;
      font-family: Consolas, monospace;
      font-size: 12px;
      white-space: pre-wrap;
      word-break: break-all;
    }

    .result-title {
      font-weight: bold;
      margin: 0 0 8px;
      color: #4ec9b0;
      font-size: 13px;

      &.error-text { color: #f48771; }
    }

    .result-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;

      th, td {
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 6px 8px;
        text-align: center;
        white-space: nowrap;
      }

      th {
        background: rgba(78, 201, 176, 0.15);
        color: #4ec9b0;
        position: sticky;
        top: 0;
        z-index: 1;
      }

      td { color: #dcdcaa; }
    }
  }

  .output-console .console-body,
  .result-panel .result-body {
    &::-webkit-scrollbar { width: 6px; height: 6px; }
    &::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.05); }
    &::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.25);
      border-radius: 3px;
    }
  }
}
</style>
