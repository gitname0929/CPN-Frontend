<template>
  <div id="centreLeft1">
    <div class="bg-color-black">
      <div class="d-flex pt-2 pl-2">
        <span style="color: #5cd9e8">
          <icon name="chart-bar"></icon>
        </span>
        <div class="d-flex">
          <span
            class="fs-xl text mx-2"
            style="font-size: medium"
            title="展示集群节点规模与运行中的工作负载"
          >集群运行概况</span>
          <dv-decoration-3 style="
              width: 1.25rem;
              height: 0.25rem;
              position: relative;
              top: -0.0375rem;"/>
        </div>
      </div>
      <div class="d-flex jc-center">
        <!-- <centreLeft1Chart ref="centreLeft1Chart" /> -->
        <dv-active-ring-chart ref="ring" :config="config" style="height: 3.25rem; width: 3.25rem" />
      </div>
      <div class="bottom-data">
        <div class="item-box">
          <div class="d-flex jc-center">
            <dv-digital-flop :config="podCountConfig" style="width: 2.5rem; height: 0.625rem" />
          </div>
          <p class="text" style="text-align: center">运行Pod(个)</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getData } from "@/utils/api";
export default {
  data() {
    return {
      clusterName: "",
      index: 0,
      config: {
        data: [
          {
            name: "节点数",
            value: 0,
          },
        ],
        color: ["#00baff", "#3de7c9", "#fff", "#ffc530", "#469f4b"],
        lineWidth: 20,
        radius: "55%",
        activeRadius: "60%",
        digitalFlopStyle: {
          fontSize: 16,
        },
        showOriginValue: true,
      },
      podCountConfig: {
        number: [0],
        toFixed: 0,
        content: "{nt}",
      },
    };
  },

  mounted() {
    this.changeTiming();
  },
  methods: {
    changeTiming() {
      this.getNumber();
      setInterval(() => {
        this.getNumber(); // 获取数字数据
      }, 3000);
    },

    async getNumber(){
      if(this.clusterName==''){
        return;
      }
      else{
        const result = await getData(this.clusterName);
        console.log("centreLeft1 获取数据",this.clusterName);
        this.podCountConfig = JSON.parse(JSON.stringify({
          ...this.podCountConfig,
          number: [result.data.podCount],
        }));
        this.config.data[0].value = result.data.nodeCount;
        this.config = JSON.parse(JSON.stringify(this.config));
      }
      
    }
  },
};
</script>

<style lang="scss">
#centreLeft1 {
  padding: 0.2rem;
  height: 5.125rem;
  min-width: 3.75rem;
  border-radius: 0.0625rem;

  .bg-color-black {
    height: 4.75rem;//4.8125rem; // 纯色背景高度
    border-radius: 0.125rem;
  }

  .text {
    color: #c3cbde;
  }

  .chart-box {
    margin-top: 0.2rem;
    width: 2.125rem;
    height: 2.125rem;

    .active-ring-name {
      padding-top: 0.125rem;
    }
  }

  .bottom-data {
    display: flex;
    justify-content: center;

    .item-box {
      color: #d3d6dd;
      text-align: center;
    }
  }
}
</style>
