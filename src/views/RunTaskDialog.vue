<template>
  <el-dialog 
    :visible.sync="visible" 
    title="课题运行配置" 
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose">
    
    <!-- 参数配置区域 -->
    <el-form :model="configForm" :rules="rules" ref="configFormRef" label-width="120px">
      <el-form-item label="CPU核心数" prop="cpu">
        <el-input-number v-model="configForm.cpu" :min="0.5" :step="0.5"></el-input-number>
      </el-form-item>
      <el-form-item label="内存大小(GB)" prop="memory">
        <el-input-number v-model="configForm.memory" :min="1" :step="1"></el-input-number>
      </el-form-item>
      <el-form-item label="实例数量" prop="instances">
        <el-input-number v-model="configForm.instances" :min="1" :max="10"></el-input-number>
      </el-form-item>
      <!-- 动态参数区域：根据所选课题动态变化 -->
      <el-form-item 
        v-for="param in dynamicParams" 
        :key="param.name" 
        :label="param.label">
        <el-input v-model="configForm[param.name]"></el-input>
      </el-form-item>
    </el-form>
    
    <!-- 实时输出区域 -->
    <div class="output-container" v-if="isRunning || outputLogs.length > 0">
      <div class="output-header">
        <span>运行输出</span>
        <el-button type="text" size="small" @click="clearOutput">清空</el-button>
      </div>
      <div class="output-content">
        <div v-for="(log, idx) in outputLogs" :key="idx" class="log-line">
          <span class="log-time">{{ log.time }}</span>
          <span :class="['log-text', log.type]">{{ log.text }}</span>
        </div>
        <div v-if="finalResult" class="final-result">
          <el-divider></el-divider>
          <div class="result-title">执行结果：</div>
          <pre>{{ finalResult }}</pre>
        </div>
      </div>
    </div>
    
    <span slot="footer">
      <el-button @click="visible = false">取消</el-button>
      <el-button 
        type="primary" 
        :loading="running" 
        @click="handleRun">
        {{ running ? '运行中...' : '运行' }}
      </el-button>
    </span>
  </el-dialog>
</template>

<script>
export default {
  name: 'RunTaskDialog',
  props: {
    visible: Boolean,
    topicId: [String, Number]
  },
  data() {
    return {
      configForm: {
        cpu: 1,
        memory: 2,
        instances: 1
      },
      rules: {
        cpu: [{ required: true, message: '请输入CPU核心数' }],
        memory: [{ required: true, message: '请输入内存大小' }],
        instances: [{ required: true, message: '请输入实例数量' }]
      },
      dynamicParams: [], // 动态加载的参数配置
      running: false,
      outputLogs: [],
      finalResult: '',
      eventSource: null
    }
  },
  watch: {
    visible(val) {
      if (val && this.topicId) {
        this.loadDynamicParams();
      }
    }
  },
  methods: {
    // 加载课题对应的动态参数
    async loadDynamicParams() {
      try {
        const res = await this.$http.get(`/api/topics/${this.topicId}/params`);
        this.dynamicParams = res.data;
        // 初始化动态参数字段
        this.dynamicParams.forEach(p => {
          this.$set(this.configForm, p.name, p.defaultValue || '');
        });
      } catch (error) {
        console.error('加载参数失败', error);
      }
    },
    
    // 执行运行
    async handleRun() {
      this.$refs.configFormRef.validate(async (valid) => {
        if (!valid) return;
        
        this.running = true;
        this.outputLogs = [];
        this.finalResult = '';
        
        try {
          // 提交任务
          const { data } = await this.$http.post('/api/tasks/run', {
            topicId: this.topicId,
            parameters: this.configForm
          });
          
          const taskId = data.taskId;
          
          // 监听 SSE 实时输出（需后端支持）
          this.eventSource = new EventSource(`/api/tasks/${taskId}/stream`);
          this.eventSource.onmessage = (event) => {
            const logData = JSON.parse(event.data);
            this.outputLogs.push({
              time: new Date().toLocaleTimeString(),
              text: logData.message,
              type: logData.type || 'info'
            });
            // 自动滚动到底部
            this.$nextTick(() => {
              const container = this.$el.querySelector('.output-content');
              if (container) container.scrollTop = container.scrollHeight;
            });
          };
          
          this.eventSource.onerror = () => {
            this.eventSource.close();
          };
          
          // 轮询获取最终结果
          const pollResult = async () => {
            const { data: result } = await this.$http.get(`/api/tasks/${taskId}/result`);
            if (result.status === 'completed') {
              this.finalResult = result.output;
              this.eventSource.close();
              this.running = false;
            } else if (result.status === 'failed') {
              this.finalResult = `执行失败: ${result.error}`;
              this.eventSource.close();
              this.running = false;
            } else {
              setTimeout(pollResult, 1000);
            }
          };
          pollResult();
          
        } catch (error) {
          this.outputLogs.push({
            time: new Date().toLocaleTimeString(),
            text: `执行失败: ${error.message}`,
            type: 'error'
          });
          this.running = false;
        }
      });
    },
    
    clearOutput() {
      this.outputLogs = [];
      this.finalResult = '';
    },
    
    handleClose() {
      if (this.eventSource) {
        this.eventSource.close();
      }
      this.running = false;
      this.outputLogs = [];
      this.finalResult = '';
      this.$emit('update:visible', false);
    }
  }
}
</script>

<style scoped>
.output-container {
  margin-top: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}
.output-header {
  padding: 8px 12px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f5f7fa;
}
.output-content {
  height: 300px;
  overflow-y: auto;
  padding: 12px;
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: monospace;
  font-size: 12px;
}
.log-line {
  margin-bottom: 4px;
  line-height: 1.4;
}
.log-time {
  color: #858585;
  margin-right: 12px;
}
.log-text.info { color: #d4d4d4; }
.log-text.warning { color: #dcdcaa; }
.log-text.error { color: #f48771; }
.final-result pre {
  background: #2d2d2d;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  color: #d4d4d4;
}
.result-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #4ec9b0;
}
</style>