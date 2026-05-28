let cachedConfig = null;

const CHART_TYPES = new Set(['scatter', 'line', 'bar', 'pie']);
const META_X = new Set(['x轴', 'xaxis', 'x']);
const META_Y = new Set(['y轴', 'yaxis', 'y']);
const META_TYPE = new Set(['类型', 'type', 'series类型']);

const TOPIC_NAMES = ['', '课题一', '课题二', '课题三', '课题四'];

/** 数据文件名与 config.title 完全一致 */
export function dataFileName(title) {
  return `${title}.csv`;
}

export function buildDataUrl(dataFile) {
  return `/data/${dataFile.split('/').map(encodeURIComponent).join('/')}`;
}

export function normalizeConfig(raw) {
  const topics = (raw.topics || []).map((t) => {
    const topicId = t.topic != null ? t.topic : t.id;
    const figures = (t.figures || []).map((f, index) => enrichFigure(topicId, f, index, t.figures));
    return {
      id: topicId,
      name: t.name || TOPIC_NAMES[topicId] || `课题${topicId}`,
      figures,
    };
  });
  return { topics };
}

function enrichFigure(topicId, figure, index, allFigures) {
  let chartCount = 0;
  let tableCount = 0;
  for (let i = 0; i <= index; i++) {
    const t = (allFigures[i].type || '').toLowerCase();
    if (t === 'table') tableCount += 1;
    else chartCount += 1;
  }
  const type = (figure.type || 'scatter').toLowerCase();
  const isTable = type === 'table';

  return {
    id: figure.title,
    title: figure.title,
    type,
    mockKey: isTable ? `table${tableCount}` : `chart${chartCount}`,
    dataFile: `topic${topicId}/${dataFileName(figure.title)}`,
  };
}

export async function loadFiguresConfig() {
  if (cachedConfig) return cachedConfig;
  const res = await fetch('/config/figures.json');
  if (!res.ok) {
    throw new Error(`无法加载 figures.json: ${res.status}`);
  }
  const raw = await res.json();
  cachedConfig = normalizeConfig(raw);
  return cachedConfig;
}

export function clearFiguresConfigCache() {
  cachedConfig = null;
}

export function findFigure(config, topicId, figureId) {
  const topic = config.topics.find((t) => t.id === topicId);
  if (!topic) return null;
  return topic.figures.find((f) => f.id === figureId) || null;
}

export function buildFigureLabel(figure) {
  return figure.title;
}

export function buildTopicsFromConfig(config) {
  return config.topics.map((t) => ({ id: t.id, name: t.name }));
}

export function buildChartOptionsForTopic(config, topicId) {
  const topic = config.topics.find((t) => t.id === topicId);
  if (!topic) return [];
  return topic.figures.map((f) => ({
    label: buildFigureLabel(f),
    value: f.id,
    kind: f.type === 'table' ? 'table' : 'chart',
  }));
}

function cellValue(val) {
  if (val === null || val === undefined || val === '') return '';
  const s = String(val).trim();
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
    if (META_X.has(key)) {
      xAxisName = String(rows[i][1] ?? '').trim();
      i += 1;
      continue;
    }
    if (META_Y.has(key)) {
      yAxisName = String(rows[i][1] ?? '').trim();
      i += 1;
      continue;
    }
    if (META_TYPE.has(key)) {
      columnTypes = rows[i].slice(1).map((c) => String(c ?? '').trim());
      i += 1;
      continue;
    }
    break;
  }

  if (i >= rows.length) {
    throw new Error('CSV 缺少图表数据表头行');
  }

  const headerRow = rows[i];
  const seriesNames = headerRow.slice(1).map((n) => String(n ?? '').trim());
  const dataRows = rows.slice(i + 1).filter((row) => row.some((c) => c !== '' && c != null));

  return { xAxisName, yAxisName, columnTypes, seriesNames, dataRows };
}

function parseTypeCell(typeStr, seriesName, defaultType) {
  const raw = (typeStr || '').trim();
  if (!raw) {
    const fallback = inferSeriesType(seriesName, defaultType);
    return buildSeriesOpts(fallback);
  }

  const parts = raw.split(':');
  const base = parts[0].toLowerCase();
  if (!CHART_TYPES.has(base)) {
    throw new Error(`不支持的图表类型: ${typeStr}`);
  }

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

function inferSeriesType(seriesName, defaultType) {
  const name = String(seriesName || '');
  if (/kpi/i.test(name) || name.includes('指标')) return 'line';
  if (defaultType === 'mixed') return 'scatter';
  if (CHART_TYPES.has(defaultType)) return defaultType;
  return 'scatter';
}

function buildSeriesOpts(type) {
  const opts = { type };
  if (type === 'scatter') opts.symbolSize = 20;
  if (type === 'line') opts.smooth = true;
  return opts;
}

function parseChartFromRows(rows, figure) {
  const { xAxisName, yAxisName, columnTypes, seriesNames, dataRows } = splitChartRows(
    rows,
    figure.type
  );

  const categories = dataRows.map((row) => String(row[0] ?? ''));
  const series = seriesNames.map((name, idx) => {
    const col = idx + 1;
    const typeCell = columnTypes ? columnTypes[idx] : '';
    const opts = parseTypeCell(typeCell, name, figure.type);
    const data = dataRows.map((row) => cellValue(row[col]));
    return { name, ...opts, data };
  });

  const result = { categories, series };
  if (xAxisName) result.xAxisName = xAxisName;
  if (yAxisName) result.yAxisName = yAxisName;
  return result;
}

function parseTableRows(rows) {
  if (!rows.length) {
    throw new Error('表格数据为空');
  }

  const headers = rows[0].map((h) => String(h ?? '').trim());
  if (headers.some((h) => !h)) {
    throw new Error('表头不能为空');
  }

  return rows.slice(1)
    .filter((row) => row.some((c) => c !== '' && c != null))
    .map((row) => {
      const obj = {};
      headers.forEach((h, i) => {
        obj[h] = row[i] != null && row[i] !== '' ? String(row[i]) : '';
      });
      return obj;
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
        if (line[i + 1] === '"') {
          cur += '"';
          i += 1;
        } else {
          inQuotes = false;
        }
      } else {
        cur += ch;
      }
    } else if (ch === '"') {
      inQuotes = true;
    } else if (ch === ',') {
      result.push(cur);
      cur = '';
    } else {
      cur += ch;
    }
  }
  result.push(cur);
  return result;
}

export function csvTextToRows(text) {
  return text
    .replace(/^\ufeff/, '')
    .trim()
    .split(/\r?\n/)
    .filter((line) => line.length > 0)
    .map(parseCsvLine);
}

export function parseTableCsv(text) {
  return parseTableRows(csvTextToRows(text));
}

export function parseChartCsv(text, figure) {
  return parseChartFromRows(csvTextToRows(text), figure);
}

export async function fetchFigureData(figure) {
  const url = buildDataUrl(figure.dataFile);
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`无法加载数据文件: ${figure.dataFile} (${res.status})`);
  }

  const text = await res.text();
  if (figure.type === 'table') {
    return parseTableCsv(text);
  }
  return parseChartCsv(text, figure);
}
