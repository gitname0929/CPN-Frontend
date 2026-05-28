/**
 * 校验 CSV 解析结果与 mockData 一致
 * 运行: node scripts/verify-figures.js
 */
const fs = require('fs');
const path = require('path');

const mockPath = path.join(__dirname, '../src/api/mockData.js');
const configPath = path.join(__dirname, '../public/config/figures.json');
const dataDir = path.join(__dirname, '../public/data');

const META_X = new Set(['x轴', 'xaxis', 'x']);
const META_Y = new Set(['y轴', 'yaxis', 'y']);
const META_TYPE = new Set(['类型', 'type', 'series类型']);

function loadMockData() {
  const content = fs.readFileSync(mockPath, 'utf8');
  const fn = new Function(`${content.replace('export default mockTopicData;', 'return mockTopicData;')}`);
  return fn();
}

function normalizeConfig(raw) {
  return raw.topics.map((t) => {
    const topicId = t.topic != null ? t.topic : t.id;
    let chartCount = 0;
    let tableCount = 0;
    const figures = (t.figures || []).map((f) => {
      const type = (f.type || 'scatter').toLowerCase();
      const isTable = type === 'table';
      let mockKey;
      if (isTable) {
        tableCount += 1;
        mockKey = `table${tableCount}`;
      } else {
        chartCount += 1;
        mockKey = `chart${chartCount}`;
      }
      return {
        id: f.title,
        type,
        mockKey,
        dataFile: `topic${topicId}/${f.title}.csv`,
      };
    });
    return { id: topicId, figures };
  });
}

function parseCsvLine(line) {
  const result = [];
  let cur = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"') {
        if (line[i + 1] === '"') { cur += '"'; i += 1; }
        else inQuotes = false;
      } else cur += ch;
    } else if (ch === '"') inQuotes = true;
    else if (ch === ',') { result.push(cur); cur = ''; }
    else cur += ch;
  }
  result.push(cur);
  return result;
}

function csvTextToRows(text) {
  return text.replace(/^\ufeff/, '').trim().split(/\r?\n/).filter((l) => l.length).map(parseCsvLine);
}

function metaKey(cell) {
  return String(cell ?? '').trim().toLowerCase();
}

function splitChartRows(rows) {
  let xAxisName = '';
  let yAxisName = '';
  let columnTypes = null;
  let i = 0;

  while (i < rows.length) {
    const key = metaKey(rows[i][0]);
    if (META_X.has(key)) { xAxisName = String(rows[i][1] ?? '').trim(); i += 1; continue; }
    if (META_Y.has(key)) { yAxisName = String(rows[i][1] ?? '').trim(); i += 1; continue; }
    if (META_TYPE.has(key)) {
      columnTypes = rows[i].slice(1).map((c) => String(c ?? '').trim());
      i += 1;
      continue;
    }
    break;
  }

  const headerRow = rows[i];
  const seriesNames = headerRow.slice(1).map((n) => String(n ?? '').trim());
  const dataRows = rows.slice(i + 1).filter((r) => r.some((c) => c !== ''));
  return { xAxisName, yAxisName, columnTypes, seriesNames, dataRows };
}

function parseTypeCell(typeStr, seriesName, defaultType) {
  const raw = (typeStr || '').trim();
  if (!raw) {
    const name = String(seriesName || '');
    let t = defaultType === 'mixed' ? 'scatter' : defaultType;
    if (/kpi/i.test(name) || name.includes('指标')) t = 'line';
    const opts = { type: t };
    if (t === 'scatter') opts.symbolSize = 20;
    return opts;
  }
  const parts = raw.split(':');
  const base = parts[0].toLowerCase();
  const opts = { type: base };
  if (base === 'scatter') opts.symbolSize = 20;
  if (base === 'line') {
    opts.smooth = true;
    if (parts[1] === 'symbol' || parts[1] === '20') opts.symbolSize = 20;
  }
  if (base === 'bar') {
    if (parts[1] === 'stack' && parts[2]) {
      opts.stack = parts[2];
      opts.emphasis = { focus: 'series' };
    } else if (parts[1] === 'emphasis' || parts[1] === 'focus') {
      opts.emphasis = { focus: 'series' };
    }
  }
  return opts;
}

function parseCellValue(v) {
  const s = String(v ?? '').trim();
  if (s === '') return '';
  const sep = s.indexOf('|');
  if (sep >= 0) {
    const valueText = s.slice(0, sep).trim();
    const label = s.slice(sep + 1).trim();
    const n = Number(valueText);
    return {
      value: Number.isFinite(n) && valueText !== '' ? n : valueText,
      label,
    };
  }
  const n = Number(s);
  return Number.isFinite(n) && s !== '' ? n : s;
}

function parseChart(rows, figure) {
  const { xAxisName, yAxisName, columnTypes, seriesNames, dataRows } = splitChartRows(rows);
  const categories = dataRows.map((r) => String(r[0] ?? ''));
  const series = seriesNames.map((name, idx) => {
    const col = idx + 1;
    const opts = parseTypeCell(columnTypes ? columnTypes[idx] : '', name, figure.type);
    const data = dataRows.map((r) => parseCellValue(r[col]));
    return { name, ...opts, data };
  });
  const result = { categories, series };
  if (xAxisName) result.xAxisName = xAxisName;
  if (yAxisName) result.yAxisName = yAxisName;
  return result;
}

function parseTable(rows) {
  const headers = rows[0].map((h) => String(h).trim());
  return rows.slice(1)
    .filter((r) => r.some((c) => c !== ''))
    .map((r) => {
      const o = {};
      headers.forEach((h, i) => { o[h] = String(r[i] ?? ''); });
      return o;
    });
}

function deepEqual(a, b) {
  if (Array.isArray(a)) {
    return Array.isArray(b) && a.length === b.length && a.every((v, i) => deepEqual(v, b[i]));
  }
  if (a && typeof a === 'object') {
    if (!b || typeof b !== 'object') return false;
    const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
    for (const k of keys) {
      if (!deepEqual(a[k], b[k])) return false;
    }
    return true;
  }
  return a === b;
}

function verifyThroughputCompare(rows) {
  const META_CHART = new Set(['图表类型', 'charttype', 'chart type']);
  let i = 0;
  while (i < rows.length) {
    const key = metaKey(rows[i][0]);
    if (META_X.has(key) || META_Y.has(key) || META_CHART.has(key)
      || ['设备', 'device', '标题', '目标倍数', 'targetmultiplier', 'target', '主方法', 'mainmethod', 'main'].includes(key)) {
      i += 1;
      continue;
    }
    break;
  }
  if (i >= rows.length) return false;
  const categories = rows[i].slice(1).filter((c) => String(c ?? '').trim());
  if (categories.length < 1) return false;

  const methods = [];
  for (let r = i + 1; r < rows.length; r += 1) {
    const name = String(rows[r][0] ?? '').trim();
    if (!name) continue;
    methods.push(name);
  }
  return methods.includes('LRU') && methods.includes('Ours') && methods.length >= 3;
}

function main() {
  const mock = loadMockData();
  const raw = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const config = { topics: normalizeConfig(raw) };
  let ok = 0;
  let fail = 0;

  config.topics.forEach((topic) => {
    topic.figures.forEach((figure) => {
      const filePath = path.join(dataDir, figure.dataFile);
      if (!fs.existsSync(filePath)) {
        fail += 1;
        console.error(`MISSING ${figure.dataFile}`);
        return;
      }
      const rows = csvTextToRows(fs.readFileSync(filePath, 'utf8'));

      if (figure.type === 'throughput_compare') {
        if (verifyThroughputCompare(rows)) {
          ok += 1;
        } else {
          fail += 1;
          console.error(`INVALID throughput_compare topic${topic.id}/${figure.id}`);
        }
        return;
      }

      const expected = mock[topic.id] && mock[topic.id][figure.mockKey];
      if (!expected) {
        console.warn(`SKIP (no mock) topic${topic.id}/${figure.id}`);
        ok += 1;
        return;
      }
      const parsed = figure.type === 'table' ? parseTable(rows) : parseChart(rows, figure);

      if (deepEqual(parsed, expected)) {
        ok += 1;
      } else {
        fail += 1;
        console.error(`MISMATCH topic${topic.id}/${figure.id}`);
      }
    });
  });

  console.log(`Verified: ${ok} ok, ${fail} failed`);
  process.exit(fail > 0 ? 1 : 0);
}

main();
