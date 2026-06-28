// 文件路径：src/api/mockData.js
// 说明：所有课题的图表和表格预设数据，供 API 模拟使用。

const mockTopicData = {
  1: {
    chart1: {
		xAxisName: '模型与异构任务',// 新增：横坐标说明
		yAxisName: '容器状态调度性能提升比(%)',// 新增：纵坐标说明
		series:[
		{
			name: '昇腾平台(%)',
			type: 'scatter',
			symbolSize : 20,
			data: [
			81.27,
			77.06,
			80.05,
			79.83,
			72.43,
			80.80,
			79.65,
			82.46,
			77.55,
			80.96,
			81.25,
			73.68,
			72.53,
			70.93,
			72.18,
			69.23,
			87.75,
			84.48,
			87.68,
			88.52,
			89.03]
		},
		{
			name: '飞腾平台(%)',
			type: 'scatter',
			symbolSize : 20,
			data: [
			70.44,
			65.97,
			73.75,
			73.13,
			63.42,
			69.46,
			68.06,
			73.02,
			67.21,
			67.33,
			73.90,
			64.37,
			69.53,
			61.32,
			64.99,
			61.55,
			80.88,
			81.39,
			81.61,
			80.01,
			78.01					]
		},
		{
			name: 'KPI指标要求(≥40%)',
			type: 'line',
			data: [40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40]
		}
		],
		categories: [
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
		'plot_power'],
	},
    table1: [ /*昇腾 表格数据*/
		{ model: 'deit_tiny_patch_16_224', 暖到热: '1.02', 冷到热: '5.45', 性能提升比: '81.27' },
		{ model: 'levit_128', 暖到热: '1.15', 冷到热: '5.02', 性能提升比: '77.06' },
		{ model: 'mobilenet_v2', 暖到热: '0.93', 冷到热: '4.64', 性能提升比: '80.05' },
		{ model: 'mobilenet_v3_large', 暖到热: '0.85', 冷到热: '4.22', 性能提升比: '79.83' },
		{ model: 'resnet101', 暖到热: '1.24', 冷到热: '4.51', 性能提升比: '72.43' },
		{ model: 'resnet18', 暖到热: '0.88', 冷到热: '4.56', 性能提升比: '80.80' },
		{ model: 'resnet50', 暖到热: '1.04', 冷到热: '5.13', 性能提升比: '79.65' },
		{ model: 'mobilevgg', 暖到热: '1.00', 冷到热: '5.72', 性能提升比: '82.46' },
		{ model: 'lightvgg11', 暖到热: '1.16', 冷到热: '5.16', 性能提升比: '77.55' },
		{ model: 'yolo5s', 暖到热: '1.00', 冷到热: '5.26', 性能提升比: '80.96' },
		{ model: 'yolov8n', 暖到热: '0.95', 冷到热: '5.07', 性能提升比: '81.25' },
		{ model: 'sampler_cpu', 暖到热: '1.32', 冷到热: '5.02', 性能提升比: '73.68' },
		{ model: 'sampler_ram', 暖到热: '1.32', 冷到热: '4.79', 性能提升比: '72.53' },
		{ model: 'sampler_gpu', 暖到热: '1.31', 冷到热: '4.51', 性能提升比: '70.93' },
		{ model: 'sampler_internet', 暖到热: '1.40', 冷到热: '5.02', 性能提升比: '72.18' },
		{ model: 'sampler_power', 暖到热: '1.30', 冷到热: '4.21', 性能提升比: '69.23' },
		{ model: 'plot_cpu', 暖到热: '0.51', 冷到热: '4.14', 性能提升比: '87.75' },
		{ model: 'plot_ram', 暖到热: '0.52', 冷到热: '3.38', 性能提升比: '84.48' },
		{ model: 'plot_gpu', 暖到热: '0.51', 冷到热: '4.12', 性能提升比: '87.68' },
		{ model: 'plot_internet', 暖到热: '0.49', 冷到热: '4.25', 性能提升比: '88.52' },
		{ model: 'plot_power', 暖到热: '0.50', 冷到热: '4.51', 性能提升比: '89.03' },
    ],
	table2:[ /*飞腾表格数据 */
		{ model: 'deit_tiny_patch_16_224', 暖到热: '0.81', 冷到热: '2.76', 性能提升比: '70.44' },
		{ model: 'levit_128', 暖到热: '0.93', 冷到热: '2.75', 性能提升比: '65.97' },
		{ model: 'mobilenet_v2', 暖到热: '0.74', 冷到热: '2.81', 性能提升比: '73.75' },
		{ model: 'mobilenet_v3_large', 暖到热: '0.71', 冷到热: '2.65', 性能提升比: '73.13' },
		{ model: 'resnet101', 暖到热: '1.10', 冷到热: '3.02', 性能提升比: '63.42' },
		{ model: 'resnet18', 暖到热: '0.69', 冷到热: '2.26', 性能提升比: '69.46' },
		{ model: 'resnet50', 暖到热: '0.87', 冷到热: '2.72', 性能提升比: '68.06' },
		{ model: 'mobilevgg', 暖到热: '0.68', 冷到热: '2.51', 性能提升比: '73.02' },
		{ model: 'lightvgg11', 暖到热: '1.04', 冷到热: '3.19', 性能提升比: '67.21' },
		{ model: 'yolo5s', 暖到热: '0.88', 冷到热: '2.69', 性能提升比: '67.33' },
		{ model: 'yolov8n', 暖到热: '0.79', 冷到热: '3.04', 性能提升比: '73.90' },
		{ model: 'sampler_cpu', 暖到热: '1.00', 冷到热: '2.81', 性能提升比: '64.37' },
		{ model: 'sampler_ram', 暖到热: '0.82', 冷到热: '2.68', 性能提升比: '69.53' },
		{ model: 'sampler_gpu', 暖到热: '1.14', 冷到热: '2.95', 性能提升比: '61.32' },
		{ model: 'sampler_internet', 暖到热: '0.97', 冷到热: '2.78', 性能提升比: '64.99' },
		{ model: 'sampler_power', 暖到热: '0.97', 冷到热: '2.52', 性能提升比: '61.55' },
		{ model: 'plot_cpu', 暖到热: '0.50', 冷到热: '2.63', 性能提升比: '80.88' },
		{ model: 'plot_ram', 暖到热: '0.51', 冷到热: '2.75', 性能提升比: '81.39' },
		{ model: 'plot_gpu', 暖到热: '0.48', 冷到热: '2.61', 性能提升比: '81.61' },
		{ model: 'plot_internet', 暖到热: '0.50', 冷到热: '2.52', 性能提升比: '80.01' },
		{ model: 'plot_power', 暖到热: '0.55', 冷到热: '2.52', 性能提升比: '78.01' },
    ],
  },
  2: {
    chart1: {/*PC low goole*/
		xAxisName: '数据集子集',
		yAxisName: '预测平均绝对误差(MAE)',
		series: [
			{ name: 'LSTM预测',
			type: 'scatter', 
			symbolSize:20,
			data: [0.3951899,0.5929973,0.5637493,0.8171165,0.9799457],
			},
			{ name: 'PatchTST预测',
			type: 'scatter', 
			symbolSize:20,
			data: [0.3823257,0.6052104,0.6567125,0.6132239,0.9766155],
			},
			{ name: 'KPI指标要求(MAE≤1)',
			type: 'line', 
			symbolSize:20,
			data: [1.0,1.0,1.0,1.0,1.0],
			},
		],
		categories: ['1', '2', '3', '4', '5']
    },
	chart2: {//PC high goole
		xAxisName: '数据集子集',
		yAxisName: '预测平均绝对误差(MAE)',
		series: [
			{ name: 'LSTM预测',
			type: 'scatter', 
			symbolSize:20,
			data: [2.4482443,3.043431,1.9756921,2.0574725,2.5189898],
			},
			{ name: 'PatchTST预测',
			type: 'scatter', 
			symbolSize:20,
			data: [2.3543567,3.163499,1.9240668,2.0421845,2.4713287],
			},
			{ name: 'KPI指标要求(MAE≤5)',
			type: 'line', 
			symbolSize:20,
			data: [5.0,5.0,5.0,5.0,5.0],
			},
		],
		categories: ['1', '2', '3', '4', '5']
	},
	chart3: {//PC low 华为
		xAxisName: '数据集子集',
		yAxisName: '预测平均绝对误差(MAE)',
		series: [
			{ name: 'LSTM预测',
			type: 'scatter', 
			symbolSize:20,
			data: [0.2550383,0.3405134,0.7987075,0.3485339,0.2960699],
			},
			{ name: 'PatchTST预测',
			type: 'scatter', 
			symbolSize:20,
			data: [0.2524586,0.3523366,0.8811737,0.3738172,0.2751669],
			},
			{ name: 'KPI指标要求(MAE≤1)',
			type: 'line', 
			symbolSize:20,
			data: [1.0,1.0,1.0,1.0,1.0],
			},
		],
		categories: ['1', '2', '3', '4', '5']
	},
	chart4: {//PC High 华为
		xAxisName: '数据集子集',
		yAxisName: '预测平均绝对误差(MAE)',
		series: [
			{ name: 'LSTM预测',
			type: 'scatter', 
			symbolSize:20,
			data: [3.7544368,4.3463435,4.070341,2.9157586,2.2330606],
			},
			{ name: 'PatchTST预测',
			type: 'scatter', 
			symbolSize:20,
			data: [3.6879606,4.0198502,3.8848554,3.0228745,2.2146439],
			},
			{ name: 'KPI指标要求(MAE≤5)',
			type: 'line', 
			symbolSize:20,
			data: [5.0,5.0,5.0,5.0,5.0],
			},
		],
		categories: ['1', '2', '3', '4', '5']
	},
	chart5: {//昇腾 low goole
		xAxisName: '数据集子集',
		yAxisName: '预测平均绝对误差(MAE)',
		series: [
			{ name: 'LSTM预测',
			type: 'scatter', 
			symbolSize:20,
			data: [0.3899,0.585,0.5619,0.7773,0.9806],
			},
			{ name: 'PatchTST预测',
			type: 'scatter', 
			symbolSize:20,
			data: [0.3794,0.6084,0.6442,0.5884,0.982],
			},
			{ name: 'KPI指标要求(MAE≤1)',
			type: 'line', 
			symbolSize:20,
			data: [1.0,1.0,1.0,1.0,1.0],
			},
		],
		categories: ['1', '2', '3', '4', '5']
	},
	chart6: {//昇腾 High goole
		xAxisName: '数据集子集',
		yAxisName: '预测平均绝对误差(MAE)',
		series: [
			{ name: 'LSTM预测',
			type: 'scatter', 
			symbolSize:20,
			data: [2.4071,3.0288,2.0018,2.066,2.4878],
			},
			{ name: 'PatchTST预测',
			type: 'scatter', 
			symbolSize:20,
			data: [2.3812,3.1778,1.9301,2.0445,2.4502],
			},
			{ name: 'KPI指标要求(MAE≤5)',
			type: 'line', 
			symbolSize:20,
			data: [5.0,5.0,5.0,5.0,5.0],
			},
		],
		categories: ['1', '2', '3', '4', '5']
	},
	chart7: {//昇腾 low 华为
		xAxisName: '数据集子集',
		yAxisName: '预测平均绝对误差(MAE)',
		series: [
			{ name: 'LSTM预测',
			type: 'scatter', 
			symbolSize:20,
			data: [0.2529,0.3567,0.7986,0.3372,0.2808],
			},
			{ name: 'PatchTST预测',
			type: 'scatter', 
			symbolSize:20,
			data: [0.2464,0.3515,0.9046,0.3604,0.2659],
			},
			{ name: 'KPI指标要求(MAE≤1)',
			type: 'line', 
			symbolSize:20,
			data: [1.0,1.0,1.0,1.0,1.0],
			},
		],
		categories: ['1', '2', '3', '4', '5']
	},
	chart8: {//昇腾 High 华为
		xAxisName: '数据集子集',
		yAxisName: '预测平均绝对误差(MAE)',
		series: [
			{ name: 'LSTM预测',
			type: 'scatter', 
			symbolSize:20,
			data: [3.7879,3.8862,4.1284,2.8595,2.2564],
			},
			{ name: 'PatchTST预测',
			type: 'scatter', 
			symbolSize:20,
			data: [3.7815,3.8752,3.8303,3.0153,2.2246],
			},
			{ name: 'KPI指标要求(MAE≤5)',
			type: 'line', 
			symbolSize:20,
			data: [5.0,5.0,5.0,5.0,5.0],
			},
		],
		categories: ['1', '2', '3', '4', '5']
	},
	chart9: {//飞腾 low goole
		xAxisName: '数据集子集',
		yAxisName: '预测平均绝对误差(MAE)',
		series: [
			{ name: 'LSTM预测',
			type: 'scatter', 
			symbolSize:20,
			data: [0.3899,0.585,0.5619,0.7773,0.9806],
			},
			{ name: 'PatchTST预测',
			type: 'scatter', 
			symbolSize:20,
			data: [0.3794,0.6084,0.6441,0.5883,0.9821],
			},
			{ name: 'KPI指标要求(MAE≤1)',
			type: 'line', 
			symbolSize:20,
			data: [1.0,1.0,1.0,1.0,1.0],
			},
		],
		categories: ['1', '2', '3', '4', '5']
	},
	chart10: {//飞腾 High goole
		xAxisName: '数据集子集',
		yAxisName: '预测平均绝对误差(MAE)',
		series: [
			{ name: 'LSTM预测',
			type: 'scatter', 
			symbolSize:20,
			data: [2.4072,3.0287,2.0018,2.066,2.4879],
			},
			{ name: 'PatchTST预测',
			type: 'scatter', 
			symbolSize:20,
			data: [2.3812,3.1778,1.93,2.0445,2.4503],
			},
			{ name: 'KPI指标要求(MAE≤5)',
			type: 'line', 
			symbolSize:20,
			data: [5.0,5.0,5.0,5.0,5.0],
			},
		],
		categories: ['1', '2', '3', '4', '5']
	},
	chart11: {//飞腾 low 华为
		xAxisName: '数据集子集',
		yAxisName: '预测平均绝对误差(MAE)',
		series: [
			{ name: 'LSTM预测',
			type: 'scatter', 
			symbolSize:20,
			data: [0.2529,0.3567,0.7987,0.3372,0.2808],
			},
			{ name: 'PatchTST预测',
			type: 'scatter', 
			symbolSize:20,
			data: [0.2464,0.3516,0.9049,0.3604,0.2659],
			},
			{ name: 'KPI指标要求',
			type: 'line',
			symbolSize:20,
			data: [1.0,1.0,1.0,1.0,1.0],
			},
		],
		categories: ['1', '2', '3', '4', '5']
	},
	chart12: {//飞腾 High 华为
		xAxisName: '数据集子集',
		yAxisName: '预测平均绝对误差(MAE)',
		series: [
			{ name: 'LSTM预测',
			type: 'scatter', 
			symbolSize:20,
			data: [3.7879,3.8865,4.1283,2.8595,2.2564],
			},
			{ name: 'PatchTST预测',
			type: 'scatter', 
			symbolSize:20,
			data: [3.7822,3.875,3.8304,3.0153,2.2246],
			},
			{ name: 'KPI指标要求(MAE≤5)',
			type: 'line', 
			symbolSize:20,
			data: [5.0,5.0,5.0,5.0,5.0],
			},
		],
		categories: ['1', '2', '3', '4', '5']
	},
  },
  3: {
    chart1: {//昇腾1v1时延
      xAxisName: '模型',
      yAxisName: '时延(ms)',
      series: [
		{
        // name: '资源分配',
        // type: 'pie',
        // radius: ['40%', '70%'],
        // data: [
        //   { value: 335, name: '已使用' },
        //   { value: 310, name: '预留' },
        //   { value: 234, name: '空闲' },
        //   { value: 135, name: '故障' }
        // ],
		name: '端侧推理',
		type: 'bar',
		stack: 'Ad',
		emphasis: {
			focus: 'series'
		},
		data: [17.01,31.01,45.47,18.67,16.58,114.45,17.07,877.49,0,0,0,472.54,45.39,9.77,0.51]
		},
		{
		name: '传输时长',
		type: 'bar',
		stack: 'Ad',
		emphasis: {
			focus: 'series'
		},
		data: [0.39,0.37,0.28,0.17,196.69,0.56,194.54,0.21,0.57,0.55,0.57,465.59,196.14,37.15,0.69]
		},
		{
		name: '边缘推理',
		type: 'bar',
		stack: 'Ad',
		emphasis: {
			focus: 'series'
		},
		data: [147.47,38.59,18.27,7.37,847.74,100.81,451.22,3.09,1249.44,1680.34,2089.87,141.48,163.4,180.98,79]
		},
		{
		name: 'Baseline',
		type: 'bar',
		emphasis: {
			focus: 'series'
		},
		data: [587.9247212,267.5110607,243.629967,231.1712689,2329.237232,511.0485725,1220.934453,1106.260592,1553.71892,2059.002435,2566.644745,1462.17578,1097.120133,624.2213025,306.4463143]
		},
      ],
      categories: ['deit_tiny_patch_16_224',
	'levit_128',
	'mobilenet_v2',
	'mobilenet_v3_large',
	'resnet101',
	'resnet18',
	'resnet50',
	'vgg11_static',
	'vgg13',
	'vgg16',
	'vgg19',
	'mobilevgg',
	'lightvgg11',
	'yolov5s',
	'yolov8n']
    },
	chart2: {// 昇腾1v1内存
      xAxisName: '模型',
      yAxisName: '内存占用(MB)',
      series: [
		{
		name: '完整模型内存占用',
		type: 'bar',
		emphasis: {
			focus: 'series'
		},
		data: [279.8,359.7,248.3,286.1,1061.88,166.8,1110.016,2026.496,2048,1944.576,2048,248.7,2048,358.4,244.6]
		},
		{
		name: 'head模型内存占用',
		type: 'bar',
		emphasis: {
			focus: 'series'
		},
		data: [46,43.03,48,44.81,40.31,43.12,40.45,1477.63,0,0,0,167.8,68.32,42.11,35.46]
		},
      ],
      categories: ['deit_tiny_patch_16_224',
	'levit_128',
	'mobilenet_v2',
	'mobilenet_v3_large',
	'resnet101',
	'resnet18',
	'resnet50',
	'vgg11_static',
	'vgg13',
	'vgg16',
	'vgg19',
	'mobilevgg',
	'lightvgg11',
	'yolov5s',
	'yolov8n']
	},
	chart3: {// 飞腾1v1时延
      xAxisName: '模型',
      yAxisName: '时延(ms)',
      series: [
		{
		name: '端侧推理',
		type: 'bar',
		stack: 'Ad',
		emphasis: {
			focus: 'series'
		},
		data: [5.13,0.36,16.78,18.86,0.37,0.39,64.07,0.29,0.38,0.37,0.43,0.65,0.37,0.42,3]
		},
		{
		name: '传输时长',
		type: 'bar',
		stack: 'Ad',
		emphasis: {
			focus: 'series'
		},
		data: [0.27,0.38,0.67,0.17,0.46,0.59,2.81,0.47,0.46,0.36,0.48,0.66,0.39,0.46,0.57]
		},
		{
		name: '边缘推理',
		type: 'bar',
		stack: 'Ad',
		emphasis: {
			focus: 'series'
		},
		data: [224.89,84.37,54.78,10.33,84.25,297.91,611.82,1206.68,1773.02,2380.69,3005.78,792.28,250.54,268.84,106.73]
		},
		{
		name: 'Baseline',
		type: 'bar',
		emphasis: {
			focus: 'series'
		},
		data: [364.1976552,655.9859076,379.21,294.92,6340.610399,932.6931026,3203.690892,1894.99,2317.396222,3658.295343,4415.396613,2488.29769,2329.589507,1449.505676,572.5167201]
		},
      ],
      categories: ['deit_tiny_patch_16_224',
	'levit_128',
	'mobilenet_v2',
	'mobilenet_v3_large',
	'resnet101',
	'resnet18',
	'resnet50',
	'vgg11_static',
	'vgg13',
	'vgg16',
	'vgg19',
	'mobilevgg',
	'lightvgg11',
	'yolov5s',
	'yolov8n']
	},
	chart4: {// 飞腾1v1内存
      xAxisName: '模型',
      yAxisName: '内存占用(MB)',
      series: [
		{
		name: '完整模型内存占用',
		type: 'bar',
		emphasis: {
			focus: 'series'
		},
		data: [159,175.5,134.4,144.3,312.7,166.8,238.1,1040,1056,1183,1167,217.8,1127,164.8,136.3]
		},
		{
		name: 'head模型内存占用',
		type: 'bar',
		emphasis: {
			focus: 'series'
		},
		data: [33.36,29.56,42.59,42.94,27.39,27.66,50.04,27.85,28.63,27.61,28.93,29,29.2,31.51,31.81]
		},
      ],
      categories: ['deit_tiny_patch_16_224',
	'levit_128',
	'mobilenet_v2',
	'mobilenet_v3_large',
	'resnet101',
	'resnet18',
	'resnet50',
	'vgg11_static',
	'vgg13',
	'vgg16',
	'vgg19',
	'mobilevgg',
	'lightvgg11',
	'yolov5s',
	'yolov8n']
	},
  },
  4: {
    chart1: {
      xAxisName: '请求强度',
      yAxisName: '吞吐量(req/s)',
      categories: ['6 req/s', '8 req/s', '10 req/s'],
      series: [
        {
          name: 'LRU缓存策略',
          type: 'bar',
          data: [
            { value: 1.1, label: 'Ours +91.8%' },
            { value: 1.3, label: 'Ours +138.5%' },
            { value: 1.36, label: 'Ours +160.3%' },
          ]
        },
        {
          name: '本方案(无预测)',
          type: 'bar',
          data: [
            { value: 0.64, label: 'Ours +229.6.0%' },
            { value: 0.7, label: 'Ours +342.8%' },
            { value: 0.65, label: 'Ours +444.6%' },
          ]
        },
        {
          name: '本方案(含预测)',
          type: 'bar',
          data: [2.11, 3.1, 3.54]
        },
        {
          name: '相较LRU提升30%下界',
          type: 'line',
          smooth: true,
          data: [1.43, 1.69, 1.768]
        }
      ]
    },
    chart2: {
      xAxisName: '请求强度',
      yAxisName: '吞吐量(req/s)',
      categories: ['6 req/s', '8 req/s', '10 req/s'],
      series: [
        {
          name: 'LRU缓存策略',
          type: 'bar',
          data: [
            { value: 0.84, label: 'Ours +42.9%' },
            { value: 1.06, label: 'Ours +33.0%' },
            { value: 1.07, label: 'Ours +62.6%' },
          ]
        },
        {
          name: '本方案(无预测)',
          type: 'bar',
          data: [
            { value: 0.721, label: 'Ours +66.7%' },
            { value: 0.93, label: 'Ours +51.6%' },
            { value: 0.86, label: 'Ours +102.3%' },
          ]
        },
        {
          name: '本方案(含预测)',
          type: 'bar',
          data: [1.20, 1.41, 1.74]
        },
        {
          name: '相较LRU提升30%下界',
          type: 'line',
          smooth: true,
          data: [1.09, 1.38, 1.39]
        }
      ]
    },
    table1: [
      { 应用: '应用A', Pod数: '15', 状态: '运行中' },
      { 应用: '应用B', Pod数: '23', 状态: '运行中' },
      { 应用: '应用C', Pod数: '18', 状态: '运行中' },
      { 应用: '应用D', Pod数: '27', 状态: '运行中' },
      { 应用: '应用E', Pod数: '20', 状态: '运行中' },
      { 应用: '应用F', Pod数: '12', 状态: '运行中' },
    ],
    table2: [
      { 存储卷: 'vol-app-logs', 容量: '500GB', 已用: '320GB', 类型: 'SSD' },
      { 存储卷: 'vol-database', 容量: '1TB', 已用: '780GB', 类型: 'HDD' },
    ],
  },
};

export default mockTopicData;
