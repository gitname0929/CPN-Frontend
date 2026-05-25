// 课题数据接口：配置文件 + CSV 解析，mock 作为 fallback

import mockTopicData from './mockData';
import {
  loadFiguresConfig,
  findFigure,
  fetchFigureData,
} from '@/utils/figureParser';

let configPromise = null;

function getConfig() {
  if (!configPromise) {
    configPromise = loadFiguresConfig().catch((err) => {
      configPromise = null;
      throw err;
    });
  }
  return configPromise;
}

/**
 * @param {number} topicId
 * @param {string} figureId - 图表 chartN 或表格 title
 * @returns {Promise<Object|Array>}
 */
export async function fetchTopicData(topicId, figureId) {
  try {
    const config = await getConfig();
    const figure = findFigure(config, topicId, figureId);

    if (figure && figure.dataFile) {
      return fetchFigureData(figure);
    }
  } catch (err) {
    console.warn('数据文件加载失败，尝试 mock fallback:', err.message);
  }

  const config = await getConfig().catch(() => null);
  const figure = config ? findFigure(config, topicId, figureId) : null;
  const mockKey = figure && figure.mockKey ? figure.mockKey : figureId;
  return fetchMockData(topicId, mockKey);
}

function fetchMockData(topicId, figureId) {
  return new Promise((resolve, reject) => {
    const topic = mockTopicData[topicId];
    if (topic && topic[figureId] !== undefined) {
      resolve(topic[figureId]);
      return;
    }
    reject(new Error(`Data not found: topic=${topicId}, key=${figureId}`));
  });
}

export { loadFiguresConfig, findFigure } from '@/utils/figureParser';
