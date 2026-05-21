// 文件路径：src/api/topicApi.js
// 说明：课题数据接口封装，支持 Mock 和真实后端切换。

import mockTopicData from './mockData';

/**
 * 根据课题ID和数据键获取图表/表格数据
 * @param {number} topicId - 课题ID (1~4)
 * @param {string} dataKey - 数据键，如 'chart1', 'table1'
 * @returns {Promise<Object|Array>}
 */
export function fetchTopicData(topicId, dataKey) {
  // ---------- Mock 模式 ----------
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const topic = mockTopicData[topicId];
      if (topic && topic[dataKey] !== undefined) {
        resolve(topic[dataKey]);
      } else {
        reject(new Error(`Data not found: topic=${topicId}, key=${dataKey}`));
      }
    }, 100); // 模拟网络延迟
  });

  // ---------- 真实后端模式（需要时取消注释）----------
  /*
  import axios from 'axios';
  return axios.get(`/api/topic/${topicId}/${dataKey}`)
    .then(response => response.data);
  */
}