/**
 * 从 mockData.js 导出 figures.json 与全部 CSV（文件名 = title）
 * 运行: npm run export-figures
 */
const fs = require('fs');
const path = require('path');

const mockPath = path.join(__dirname, '../src/api/mockData.js');

const LABELS = {
  1: {
    chart1: { title: '图1：性能对比图', type: 'mixed' },
    table1: { title: '表1：昇腾测试数据', type: 'table' },
    table2: { title: '表2：飞腾测试数据', type: 'table' },
  },
  2: {
    chart1: { title: '图1.1：PC低负载谷歌数据集', type: 'mixed' },
    chart2: { title: '图1.2：PC高负载谷歌数据集', type: 'mixed' },
    chart3: { title: '图1.3：PC低负载华为数据集', type: 'mixed' },
    chart4: { title: '图1.4：PC高负载华为数据集', type: 'mixed' },
    chart5: { title: '图2.1：昇腾低负载谷歌数据集', type: 'mixed' },
    chart6: { title: '图2.2：昇腾高负载谷歌数据集', type: 'mixed' },
    chart7: { title: '图2.3：昇腾低负载华为数据集', type: 'mixed' },
    chart8: { title: '图2.4：昇腾高负载华为数据集', type: 'mixed' },
    chart9: { title: '图3.1：飞腾低负载谷歌数据集', type: 'mixed' },
    chart10: { title: '图3.2：飞腾高负载谷歌数据集', type: 'mixed' },
    chart11: { title: '图3.3：飞腾低负载华为数据集', type: 'mixed' },
    chart12: { title: '图3.4：飞腾高负载华为数据集', type: 'mixed' },
  },
  3: {
    chart1: { title: '图1.1：昇腾1:1时延图', type: 'bar' },
    chart2: { title: '图1.2：昇腾1:1内存图', type: 'bar' },
    chart3: { title: '图2.1：飞腾1:1时延图', type: 'bar' },
    chart4: { title: '图2.2：飞腾1:1内存图', type: 'bar' },
  },
  4: {
    chart1: { title: '图1：柱状图', type: 'bar' },
    table1: { title: '表1：明细数据', type: 'table' },
    table2: { title: '表2：存储卷数据', type: 'table' },
  },
};

function loadMockData() {
  const content = fs.readFileSync(mockPath, 'utf8');
  const fn = new Function(`${content.replace('export default mockTopicData;', 'return mockTopicData;')}`);
  return fn();
}

function seriesTypeCell(s) {
  if (s.type === 'bar' && s.stack) {
    return `bar:stack:${s.stack}`;
  }
  if (s.type === 'bar' && s.emphasis) {
    return 'bar:emphasis';
  }
  if (s.type === 'line' && s.symbolSize) {
    return 'line:symbol';
  }
  return s.type;
}

function chartToRows(chartData) {
  const { categories, series, xAxisName, yAxisName } = chartData;
  const rows = [];
  if (xAxisName) rows.push(['x轴', xAxisName]);
  if (yAxisName) rows.push(['y轴', yAxisName]);

  const types = series.map(seriesTypeCell);
  const needsTypeRow = new Set(types).size > 1 || types.some((t) => t.includes(':'));
  if (needsTypeRow) {
    rows.push(['类型', ...types]);
  }

  rows.push(['', ...series.map((s) => s.name)]);
  categories.forEach((cat, i) => {
    rows.push([cat, ...series.map((s) => s.data[i])]);
  });
  return rows;
}

function tableToRows(tableData) {
  if (!tableData.length) return [[]];
  const headers = Object.keys(tableData[0]);
  const rows = [headers];
  tableData.forEach((row) => {
    rows.push(headers.map((h) => row[h]));
  });
  return rows;
}

function escapeCsvCell(val) {
  const s = String(val ?? '');
  if (/[",\n\r]/.test(s)) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

function writeCsv(filePath, rows) {
  const lines = rows.map((row) => row.map(escapeCsvCell).join(','));
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `\ufeff${lines.join('\n')}\n`, 'utf8');
}

function main() {
  const mockTopicData = loadMockData();
  const root = path.join(__dirname, '..');
  const dataDir = path.join(root, 'public/data');
  const configDir = path.join(root, 'public/config');
  fs.mkdirSync(configDir, { recursive: true });

  const topics = [];

  Object.keys(mockTopicData).forEach((topicKey) => {
    const topicId = Number(topicKey);
    const topicData = mockTopicData[topicId];
    const labels = LABELS[topicId] || {};
    const figures = [];
    const topicDir = path.join(dataDir, `topic${topicId}`);

    Object.keys(topicData).forEach((figureId) => {
      const meta = labels[figureId] || { title: figureId, type: 'scatter' };
      const value = topicData[figureId];
      const csvPath = path.join(topicDir, `${meta.title}.csv`);

      figures.push({ title: meta.title, type: meta.type });

      if (Array.isArray(value)) {
        writeCsv(csvPath, tableToRows(value));
      } else if (value && value.series) {
        writeCsv(csvPath, chartToRows(value));
      }
    });

    topics.push({ topic: topicId, figures });
  });

  topics.sort((a, b) => a.topic - b.topic);
  const configPath = path.join(configDir, 'figures.json');
  fs.writeFileSync(configPath, JSON.stringify({ topics }, null, 2), 'utf8');
  console.log(`Wrote ${configPath}`);
  console.log(`Exported CSV files under public/data/`);
}

main();
