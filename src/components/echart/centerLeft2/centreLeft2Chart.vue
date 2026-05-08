<template>
  <div>
    <div id="centreLeft2Chart" style="width:5.5rem; height: 4rem;"></div>
  </div>
</template>

<script>
import echartMixins from "@/utils/resizeMixins";
import handleErrorMessage from "@/utils/handleError";
import { getDataCenters } from "@/utils/api";

export default {
  data() {
    return {
      chart: null,
      displayCityNum: 10,
      maxDataCenterNum: 5,
      cityCategory: [],
      colorCategory: [
        "#f54d4d",
        "#f87544",
        "#ffae00",
        "#dcff00",
        "#25d053",
        "#01fff5",
        "#007cff",
        "#4245ff",
        "#c32eff",
        "#ff62e8",
      ],
      dataCenterNum: [1,2,3,4,5,6,7,8,9,10,11,12,13],
      cityDataCenterNum: [],
      cityItems: [],
    };
  },
  mixins: [echartMixins],
  mounted() {
    this.draw();
  },
  methods: {
    async fetchDataCenterNum() {
      // 获取数据
      try {
        let result = await getDataCenters();
        let dataCenters = result.data;
        for (var i = 0;i < dataCenters.length && i < this.displayCityNum;i++){
          if (dataCenters[i].dataCenterNum !== 0) {
            this.cityCategory.push(dataCenters[i].city);
            if (dataCenters[i].dataCenterNum > this.maxDataCenterNum) {
              this.maxDataCenterNum = dataCenters[i].dataCenterNum;
            }
            this.cityDataCenterNum.push(dataCenters[i].dataCenterNum);
            const item = {
              value: dataCenters[i].dataCenterNum,
              itemStyle: {
                normal: {
                  color: this.colorCategory[i]
                }
              }
            };
            this.cityItems.push(item);
          }
        }
      } catch (error) {
        handleErrorMessage(error);
      }
      // let url = "/dataCenters/getDataCenters";
      // let data = await this.$http.get(url);
      // let dataCenters = data.data.data;
      // for (var i = 0;i < dataCenters.length && i < this.displayCityNum;i++){
      //   if (dataCenters[i].dataCenterNum !== 0) {
      //     this.cityCategory.push(dataCenters[i].city);
      //     if (dataCenters[i].dataCenterNum > this.maxDataCenterNum) {
      //       this.maxDataCenterNum = dataCenters[i].dataCenterNum;
      //     }
      //     this.cityDataCenterNum.push(dataCenters[i].dataCenterNum);
      //     const item = {
      //       value: dataCenters[i].dataCenterNum,
      //       itemStyle: {
      //         normal: {
      //           color: this.colorCategory[i]
      //         }
      //       }
      //     };
      //     this.cityItems.push(item);
      //   }
      // }
      // console.log("cityCategory", this.cityCategory);
      // console.log("cityDataCenterNum", this.cityDataCenterNum);
      // console.log("cityItems", this.cityItems);
    },
    async draw() {
      await this.fetchDataCenterNum();
      console.log("----------------------------------")
      // 基于准备好的dom，初始化echarts实例
      this.chart = this.$echarts.init(document.getElementById("centreLeft2Chart"));
      //  ----------------------------------------------------------------
      let option = {
        angleAxis: {
          interval: 1,
          type: "category",
          data: this.cityCategory,
          z: 1,
          axisLine: {
            show: true,
            lineStyle: {
              color: "#00c7ff",
              width: 1,
              type: "solid"
            }
          },
          axisLabel: {
            interval: 0,
            show: true,
            color: "#00c7ff",
            margin: 8,
            fontSize: 12
          }
        },
        radiusAxis: {
          min: 0,
          max: this.maxDataCenterNum,
          interval: 1,
          axisLine: {
            show: true,
            lineStyle: {
              color: "#00c7ff",
              width: 1,
              type: "solid"
            }
          },
          axisLabel: {
            formatter: "{value} %",
            show: false,
            padding: [0, 0, 20, 0],
            color: "#00c7ff",
            fontSize: 16
          },
          splitLine: {
            lineStyle: {
              color: "#00c7ff",
              width: 1,
              type: "solid"
            }
          }
        },
        legend: {
          show: true,
          orient: "vartical",
          top: "center",
          bottom: "0%",
          itemWidth: 16,
          itemHeight: 8,
          itemGap: 16,
          textStyle: {
            color: "#A3E2F4",
            fontSize: 12,
            fontWeight: 0
          },
          data: ["A"]
        },
        polar: {},
        series: [
          {
            name: "A",
            type: "bar",
            radius: ["20%", "100%"],
            data: this.cityItems,
            coordinateSystem: "polar"
          }
        ]
      };
      this.chart.setOption(option);
    }
  },
  destroyed() {
    window.onresize = null;
  }
};
</script>

<style lang="scss" scoped>
</style>
