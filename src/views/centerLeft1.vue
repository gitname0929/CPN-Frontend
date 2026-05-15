<template>
  <div id="centreLeft1">
    <div class="bg-color-black">
      <div class="d-flex pt-2 pl-2">
        <span style="color: #5cd9e8">
          <icon name="chart-bar"></icon>
        </span>
        <div class="d-flex">
          <span class="fs-xl text mx-2" style="font-size: medium">响应情况</span>
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
      <!-- 4个主要的数据 -->
      <div class="bottom-data">
        <div class="item-box" v-for="(item, index) in numberData" :key="index">
          <div class="d-flex">
            <dv-digital-flop :config="item.number" style="width: 2.5rem; height: 0.625rem" />
          </div>
          <p class="text" style="text-align: center">
            {{ item.text }}
            <!-- <span class="colorYellow">(个)</span> -->
          </p>
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
      numberData: [
        {
          number: {
            number: [0],
            toFixed: 0,
            content: "{nt}",
          },
          text: "响应时间(ms)",
        },
        {
          number: {
            number: [0],
            toFixed: 0,
            content: "{nt}",
          },
          text: "pod数(个)",
        },
        // {
        //   number: {
        //     number: [0],
        //     toFixed: 0,
        //     content: "{nt}",
        //   },
        //   text: "运行中任务数",
        // },
        // {
        //   number: {
        //     number: [0],
        //     toFixed: 0,
        //     content: "{nt}",
        //   },
        //   text: "未确认任务数",
        // },
      ],
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
        // const t0 = performance.now();
        const result = await getData(this.clusterName);
        // const durationMs = Math.round(performance.now() - t0);
        console.log("centreLeft1 获取数据",this.clusterName);
        this.numberData[0].number.number = [result.data.responseTimeMs]; //durationMs
        this.numberData[1].number.number = [result.data.podCount];
        this.config.data[0].value = result.data.nodeCount;
        this.config = JSON.parse(JSON.stringify(this.config)); // 触发视图更新
        this.numberData = JSON.parse(JSON.stringify(this.numberData)); // 触发视图更新
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
    height: 6.125rem;//4.8125rem; // 纯色背景高度
    border-radius: 0.125rem;
  }

  .text {
    color: #c3cbde;
  }

  .chart-box {
    margin-top: 0.2rem;
    width: 2.125rem;
    height: 5.125rem;

    .active-ring-name {
      padding-top: 0.125rem;
    }
  }

  .bottom-data {
    .item-box {
      float: right;
      position: relative;
      width: 50%;
      color: #d3d6dd;

      // 金币
      .coin {
        position: absolute;
        left: 0.1rem;
        top: 0.2125rem;
        font-size: 0.25rem;
        color: #ffc107;
      }

      .colorYellow {
        color: yellowgreen;
      }
    }
  }
}
</style>
