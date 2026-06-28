<template>
  <div>
    <div id="bottomLeftChart" style="width: 12.25rem; height: 6.25rem"></div>
  </div>
</template>

<script>
import echartMixins from "@/utils/resizeMixins";
import { getClusterInfoByClusterName,getPredictClusterInfoByClusterName } from "@/utils/api";
import handleErrorMessage from "@/utils/handleError";
export default {
  mixins: [echartMixins],
  data() {
    return {
      chart: null,
      clusterName: "",
      // 新增：统一管理定时器
      timerId: null,
      option: {
        title: {
          text: "",
          x: "center",
          y: 0,
          textStyle: {
            color: "#B4B4B4",
            fontSize: 16,
            fontWeight: "normal",
          },
        },
        tooltip: {
          trigger: "axis",
          backgroundColor: "rgba(255,255,255,0.1)",
          axisPointer: {
            type: "shadow",
            label: {
              show: true,
              backgroundColor: "#7B7DDC",
            },
          },
        },
        legend: {
          data: ["CPU","内存", "存储"], //"内存", "存储", 
          textStyle: {
            color: "#B4B4B4",
          },
          top: "0%",
        },
        grid: {
          x: "5%",
          width: "90%",
          y: "5%",
        },
        xAxis: {
          data: [],
          axisLine: {
            lineStyle: {
              color: "#B4B4B4",
            },
          },
          axisTick: {
            show: false,
          },
        },
        yAxis: [
          {
            splitLine: { show: false },
            axisLine: {
              lineStyle: {
                color: "#B4B4B4",
              },
            },
            axisLabel: {
              formatter: "{value}",
            },
          },
          {
            splitLine: { show: false },
            axisLine: {
              lineStyle: {
                color: "#B4B4B4",
              },
            },
            axisLabel: {
              formatter: "{value}",
            },
          },
        ],
        series: [
          {
            name: "CPU",
            type: "line",
            smooth: true,
            showAllSymbol: true,
            symbol: "emptyCircle",
            symbolSize: 8,
            yAxisIndex: 1,
            itemStyle: {
              normal: {
                color: "#F02FC2",
              },
            },
            data: [],
          },

          {
            name: "存储",
            type: "bar",
            barWidth: 10,
            itemStyle: {
              normal: {
                barBorderRadius: 5,
                color: new this.$echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: "#956FD4" },
                  // { offset: 1, color: "#3EACE5" },
                ]),
              },
            },
            data: [],
          },

          {
            name: "内存",
            type: "bar",
            barGap: "-100%",
            barWidth: 10,
            itemStyle: {
              normal: {
                barBorderRadius: 5,
                color: new this.$echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  // { offset: 0, color: "rgba(156,107,211,0.8)" },
                  // { offset: 0.2, color: "rgba(156,107,211,0.5)" },
                  { offset: 1, color: "#3EACE5" },
                ]),
              },
            },
            z: -12,
            data: [],
          },
        ],
        dataZoom: [
          {
            type: 'slider',
            show: true,
            start: 0,
            end: 100,
            xAxisIndex: [0],
            // 美化样式
            height: 14,
            bottom: 6,
            backgroundColor: 'rgba(0,0,0,0)',
            borderColor: 'rgba(94,187,255,0.4)',
            dataBackground: {
              lineStyle: { color: 'rgba(94,187,255,0.6)' },
              areaStyle: { color: 'rgba(94,187,255,0.2)' }
            },
            fillerColor: 'rgba(94,187,255,0.25)',
            handleSize: '100%',
            handleStyle: {
              color: '#5EBBFF',
              borderColor: '#A7DAFF',
              borderWidth: 1,
              shadowBlur: 2,
              shadowColor: 'rgba(0, 0, 0, 0.2)'
            },
            textStyle: { color: '#B4B4B4' },
            showDetail: false,
            showDataShadow: false,
          },
        ],
      },
      categoryOption: [
        ["22:02:17",
          "22:02:22",
          "22:02:27",
          "22:02:32",
          "22:02:37",
          "22:02:42",
          "22:02:47",
          "22:02:52",
          "22:02:57",
          "22:03:02",
          "22:03:07",
          "22:03:12",
          "22:03:17",
          "22:03:22",
          "22:03:27",
          "22:03:32",
          "22:03:37",
          "22:03:42",
          "22:03:47",
          "22:03:52",
          "22:03:57",
          "22:04:02",
          "22:04:07",
          "22:04:12",
          "22:04:17",
          "22:04:22",
          "22:04:27",
          "22:04:32",
          "22:04:37",
          "22:04:42",
          "22:04:47",
          "22:04:52",
          "22:04:57",
        ],
        [
          "22:02:22",
          "22:02:27",
          "22:02:32",
          "22:02:37",
          "22:02:42",
          "22:02:47",
          "22:02:52",
          "22:02:57",
          "22:03:02",
          "22:03:07",
          "22:03:12",
          "22:03:17",
          "22:03:22",
          "22:03:27",
          "22:03:32",
          "22:03:37",
          "22:03:42",
          "22:03:47",
          "22:03:52",
          "22:03:57",
          "22:04:02",
          "22:04:07",
          "22:04:12",
          "22:04:17",
          "22:04:22",
          "22:04:27",
          "22:04:32",
          "22:04:37",
          "22:04:42",
          "22:04:47",
          "22:04:52",
          "22:04:57",
          "22:05:02",
        ],
        [
          "22:02:27",
          "22:02:32",
          "22:02:37",
          "22:02:42",
          "22:02:47",
          "22:02:52",
          "22:02:57",
          "22:03:02",
          "22:03:07",
          "22:03:12",
          "22:03:17",
          "22:03:22",
          "22:03:27",
          "22:03:32",
          "22:03:37",
          "22:03:42",
          "22:03:47",
          "22:03:52",
          "22:03:57",
          "22:04:02",
          "22:04:07",
          "22:04:12",
          "22:04:17",
          "22:04:22",
          "22:04:27",
          "22:04:32",
          "22:04:37",
          "22:04:42",
          "22:04:47",
          "22:04:52",
          "22:04:57",
          "22:05:02",
          "22:05:07",
        ]
      ],
      diskDataOption: [
        [
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          11,
        ],
        [
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          11,
          11,
        ],
        [
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          10,
          11,
          11,
          11,
        ],
      ],
      memoryDataOption: [
        [
          14,
          15,
          15,
          16,
          17,
          15,
          9,
          12,
          14,
          21,
          23,
          24,
          25,
          13,
          16,
          15,
          15,
          16,
          17,
          18,
          19,
          22,
          14,
          21,
          18,
          19,
          15,
          18,
          21,
          23,
          24,
          24,
          26,
        ],
        [
          15,
          15,
          16,
          17,
          15,
          9,
          12,
          14,
          21,
          23,
          24,
          25,
          13,
          16,
          15,
          15,
          16,
          17,
          18,
          19,
          22,
          14,
          21,
          18,
          19,
          15,
          18,
          21,
          23,
          24,
          24,
          26,
          24,
        ],
        [
          15,
          16,
          17,
          15,
          9,
          12,
          14,
          21,
          23,
          24,
          25,
          13,
          16,
          15,
          15,
          16,
          17,
          18,
          19,
          22,
          14,
          21,
          18,
          19,
          15,
          18,
          21,
          23,
          24,
          24,
          26,
          24,
          25,
        ],
      ],
      CPUDataOption: [
        [
          18,
          16,
          19,
          21,
          20,
          18,
          19,
          16,
          20,
          17,
          15,
          16,
          18,
          19,
          23,
          20,
          18,
          15,
          17,
          16,
          23,
          19,
          21,
          20,
          18,
          16,
          12,
          14,
          15,
          18,
          20,
          26,
          24,
        ],
        [
          16,
          19,
          21,
          20,
          18,
          19,
          16,
          20,
          17,
          15,
          16,
          18,
          19,
          23,
          20,
          18,
          15,
          17,
          16,
          23,
          19,
          21,
          20,
          18,
          16,
          12,
          14,
          15,
          18,
          20,
          26,
          24,
          23
        ],
        [
          19,
          21,
          20,
          18,
          19,
          16,
          20,
          17,
          15,
          16,
          18,
          19,
          23,
          20,
          18,
          15,
          17,
          16,
          23,
          19,
          21,
          20,
          18,
          16,
          12,
          14,
          15,
          18,
          20,
          26,
          24,
          23,
          20
        ],
      ],
      index: 0,
    };
  },
  mounted() {
    this.draw(this.option);
  },
  methods: {
    // 统一清理并只保留一个定时器
    clearTimer() {
      if (this.timerId) {
        clearInterval(this.timerId);
        this.timerId = null;
      }
    },
    // 将毫秒时间戳转为可读字符串（HH:mm:ss）
    formatTimestamp(ts) {
      const ms = typeof ts === 'string' ? Number(ts) : ts;
      if (!ms || isNaN(ms)) return String(ts);
      const d = new Date(ms);
      const pad = (n) => (n < 10 ? `0${n}` : `${n}`);
      return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
    },
    firstDefined(...values) {
      return values.find((value) => value !== undefined && value !== null);
    },
    parseResourceSize(value) {
      if (typeof value === "number") {
        return Number.isFinite(value) ? value : NaN;
      }
      if (typeof value !== "string") {
        return NaN;
      }
      const match = value.trim().match(/^([\d.]+)\s*([kmgtp]?i?b?)?/i);
      if (!match) {
        return NaN;
      }
      const numeric = Number(match[1]);
      if (!Number.isFinite(numeric)) {
        return NaN;
      }
      const unit = (match[2] || "").toLowerCase();
      const multipliers = {
        k: 1024,
        kb: 1024,
        ki: 1024,
        kib: 1024,
        m: 1024 ** 2,
        mb: 1024 ** 2,
        mi: 1024 ** 2,
        mib: 1024 ** 2,
        g: 1024 ** 3,
        gb: 1024 ** 3,
        gi: 1024 ** 3,
        gib: 1024 ** 3,
        t: 1024 ** 4,
        tb: 1024 ** 4,
        ti: 1024 ** 4,
        tib: 1024 ** 4,
        p: 1024 ** 5,
        pb: 1024 ** 5,
        pi: 1024 ** 5,
        pib: 1024 ** 5,
      };
      return numeric * (multipliers[unit] || 1);
    },
    getUsagePercent(used, total, fallback) {
      const usedValue = this.parseResourceSize(used);
      const totalValue = this.parseResourceSize(total);
      if (Number.isFinite(usedValue) && Number.isFinite(totalValue) && totalValue > 0) {
        return (usedValue / totalValue) * 100;
      }
      return fallback;
    },
    changeResourceData(clusterName) {
      this.clearTimer();
      this.fetchResourceData(clusterName);
      this.timerId = setInterval(() => {
        this.fetchResourceData(clusterName); // 获取数字数据
      }, 3000);
    },
    changePredictionData(clusterName) {
      this.clearTimer();
      this.fetchPredictionData(clusterName);
      this.timerId = setInterval(() => {
        this.fetchPredictionData(clusterName); // 获取数字数据
      }, 10000);
    },
    refreshFetchResourceData(data) {
      let option = this.option;
      let CPUDataOption = new Array();
      let diskDataOption = new Array();
      let categoryOption = new Array();
      let memoryDataOption = new Array();
      for (let index = 0; index < data.length; index++) {
        const element = data[index];
        const storageUsed = this.firstDefined(element.storageUsed, element.usedStorage);
        const storageTotal = this.firstDefined(element.storageTotal, element.maxStorage, element.totalStorage);
        categoryOption.push(this.formatTimestamp(element.timestamp));
        CPUDataOption.push(element.cpuUsage );
        diskDataOption.push(this.getUsagePercent(storageUsed, storageTotal, element.storageUsage));
        memoryDataOption.push(element.memoryUsage );
      }
      option.xAxis.data = categoryOption;
      option.series[0].data = CPUDataOption;
      // option.series[1].data = diskDataOption;
      option.series[2].data = memoryDataOption;
      this.draw(option);
      console.log("finish");
    },

    async fetchResourceData(clusterName) {
      try {
        let result = await getClusterInfoByClusterName(clusterName);
        let data = result.data;
        console.log("获取节点资源数据", data);
        this.refreshFetchResourceData(data);
      } catch (error) {
        handleErrorMessage(error);
      }
    },

    async fetchPredictionData(clusterName) {
      console.log(clusterName,"fetchPredictionData");
      // todo 预测接口到时候加这里
      try {
        let result = await getPredictClusterInfoByClusterName(clusterName);
        let data = result.data;
        console.log("获取节点预测资源数据", data);
        this.refreshFetchResourceData(data);
      } catch (error) {
        handleErrorMessage(error);
      }
      // this.refreshDataInfo();
    },
    parseLeadingNumber(str) {
      let numberStr = '';
      for (const char of str) {
        if (/[0-9]/.test(char)) {
          numberStr += char;
        } else {
          break;
        }
      }
      return numberStr ? parseInt(numberStr, 10) : 0;
    },
    getOldInfo(data) {
      let option = this.option;
      let CPUDataOption = new Array();
      let diskDataOption = new Array();
      let categoryOption = new Array();
      let memoryDataOption = new Array();
      for (let index = 0; index < data.length; index++) {
        const element = data[index];
        categoryOption.push(this.formatTimestamp(element.timestamp));
        CPUDataOption.push(this.parseLeadingNumber(element.usedCpu) / 1e7 / element.maxCpu);
        diskDataOption.push(element.maxCpu);
        let temp = this.parseLeadingNumber(element.usedMemory) / this.parseLeadingNumber(element.maxMemory) * 100 / 1024;
        memoryDataOption.push(temp.toFixed(2));
      }
      option.xAxis.data = categoryOption;
      option.series[0].data = CPUDataOption;
      option.series[1].data = diskDataOption;
      option.series[2].data = memoryDataOption;
      this.draw(option);
      // this.chart.setOption(option);
      console.log("finish");
    },
    
    
    
    refreshDataInfo() {
      console.log("refreshDataInfo");
      let option = this.option;
      option.xAxis.data = this.categoryOption[this.index];
      // console.log(option)
      option.series[0].data = this.CPUDataOption[this.index];
      // option.series[1].data = this.diskDataOption[this.index];
      // option.series[2].data = this.memoryDataOption[this.index];
      // option.dataZoom = {
      //   show: true,
      //   start: 0,
      //   end: 100,
      // };
      this.draw(option);
      // this.chart.setOption(option);
      this.index = (this.index + 1) % 3;
    },
    draw(option) {
      // 基于准备好的dom，初始化echarts实例
      this.chart = this.$echarts.init(
        document.getElementById("bottomLeftChart")
      );
      this.chart.setOption(option);
      console.log(this.chart.getOption());
    },
  },
  destroyed() {
    window.onresize = null;
    // 组件销毁时清理定时器
    this.clearTimer();
  },
};
</script>

<style lang="scss" scoped></style>
