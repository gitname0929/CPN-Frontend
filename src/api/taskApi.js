import axios from 'axios';

const taskClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

function getErrorMessage(error, fallback) {
  const data = error.response && error.response.data ? error.response.data : {};
  return data.msg || data.message || data.error || error.message || fallback;
}

export function runTopicTask(payload) {
  return taskClient.post('/tasks/run', payload)
    .then((res) => {
      const body = res.data || {};
      if (body.ret !== 1) {
        throw new Error(body.msg || body.message || body.error || '启动任务失败');
      }
      return body.data;
    })
    .catch((error) => {
      throw new Error(getErrorMessage(error, '启动任务失败'));
    });
}

export function getTopicTaskResult(taskId) {
  return taskClient.get(`/tasks/${taskId}/result`)
    .then((res) => {
      const body = res.data || {};
      if (body.ret !== 1) {
        throw new Error(body.msg || body.message || body.error || '获取任务结果失败');
      }
      return body.data;
    })
    .catch((error) => {
      throw new Error(getErrorMessage(error, '获取任务结果失败'));
    });
}

export function cancelTopicTask(taskId) {
  return taskClient.delete(`/tasks/${taskId}`)
    .then((res) => {
      const body = res.data || {};
      if (body.ret !== 1) {
        throw new Error(body.msg || body.message || body.error || '取消任务失败');
      }
      return body.data;
    })
    .catch((error) => {
      throw new Error(getErrorMessage(error, '取消任务失败'));
    });
}

export function cleanupPodsEnvironment() {
  return taskClient.post('/k8s/cleanupPods')
    .then((res) => {
      const body = res.data || {};
      if (body.ret !== 1) {
        throw new Error(body.msg || body.message || body.error || '清理 pods 环境失败');
      }
      return body.data;
    })
    .catch((error) => {
      throw new Error(getErrorMessage(error, '清理 pods 环境失败'));
    });
}

export function createTopicTaskStream(taskId, onMessage) {
  const source = new EventSource(`/api/tasks/${taskId}/stream`);
  source.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);
      onMessage(payload);
    } catch (error) {
      onMessage({ message: event.data, type: 'info' });
    }
  };
  return source;
}
