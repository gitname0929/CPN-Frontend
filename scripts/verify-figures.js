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
  if (base === 'line' && (parts[1] === 'symbol' || parts[1] === '20')) opts.symbolSize = 20;
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

function parseChart(rows, figure) {
  const { xAxisName, yAxisName, columnTypes, seriesNames, dataRows } = splitChartRows(rows);
  const categories = dataRows.map((r) => String(r[0] ?? ''));
  const series = seriesNames.map((name, idx) => {
    const col = idx + 1;
    const opts = parseTypeCell(columnTypes ? columnTypes[idx] : '', name, figure.type);
    const data = dataRows.map((r) => {
      const v = r[col];
      const s = String(v ?? '').trim();
      const n = Number(s);
      return Number.isFinite(n) && s !== '' ? n : s;
    });
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

function main() {
  const mock = loadMockData();
  const raw = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const config = { topics: normalizeConfig(raw) };
  let ok = 0;
  let fail = 0;

  config.topics.forEach((topic) => {
    topic.figures.forEach((figure) => {
      const expected = mock[topic.id][figure.mockKey];
      const filePath = path.join(dataDir, figure.dataFile);
      const rows = csvTextToRows(fs.readFileSync(filePath, 'utf8'));
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
