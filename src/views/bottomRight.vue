<template>
  <div id="center">
    <div class="down">
      <div class="ranking bg-color-black">
        <span style="color: #5cd9e8">
          <icon name="align-left"></icon>
        </span>
        <span class="fs-xl text mx-2 mb-1" style="font-size: medium">集群node资源概况</span>
        <dv-scroll-board :config="config" ref="Node" style="height: 90%" />
      </div>
    </div>
  </div>
</template>

<script>
import handleErrorMessage from "@/utils/handleError";
import {getNodeResource} from "@/utils/api";
export default {
  data() {
    return {
      clusterName: 'kubernetes01',
      NodeData: [
        ['Node1', "2", "8", "2GB", "4GB", '正常'],
        ['<span style="color:#9fe6b8;">Node2</span>', "2", "8", "2GB", "4GB", '<button style="border-radius: 4px; width: 40px; background-color: green">正常</button>'],
        ['<span style="color:#9fe6b8;">Node3</span>', "3", "12", "2GB", "4GB", '<button style="border-radius: 4px; width: 40px; background-color: green">正常</button>'],
        ['<span style="color:#9fe6b8;">Node4</span>', "3", "12", "2GB", "4GB", '<button style="border-radius: 4px; width: 40px; background-color: green">正常</button>'],
        ['<span style="color:#9fe6b8;">Node5</span>', "3", "12", "2GB", "4GB", '<button style="border-radius: 4px; width: 40px; background-color: green">正常</button>'],
        ['<span style="color:#9fe6b8;">Node6</span>', "4", "16", "2GB", "4GB", '<button style="border-radius: 4px; width: 40px; background-color: green">正常</button>'],
        ['<span style="color:#9fe6b8;">Node7</span>', "3", "8", "2GB", "4GB", '<button style="border-radius: 4px; width: 40px; background-color: green">正常</button>'],
        ['<span style="color:#9fe6b8;">Node8</span>', "3", "12", "2GB", "4GB", '<button style="border-radius: 4px; width: 40px; background-color: green">正常</button>'],
        ['<span style="color:#9fe6b8;">Node9</span>', "2", "8", "2GB", "4GB", '<button style="border-radius: 4px; width: 40px; background-color: green">正常</button>'],
        ['<span style="color:#9fe6b8;">Node10</span>', "3", "12", "2GB", "4GB", '<button style="border-radius: 4px; width: 40px; background-color: green">正常</button>'],
      ],
      config: {
        header: ["Node名称", "Pod数", "CPU", "内存", "存储", "状态"],
        data: [
        ],
        rowNum: 5, //表格行数
        headerHeight: 35,
        headerBGC: "#0f1325", //表头
        oddRowBGC: "#0f1325", //奇数行
        evenRowBGC: "#171c33", //偶数行
        index: true,
        columnWidth: [50, 150, 100, 100, 150, 150, 100],
        align: ["center"],
        //text_align: "center",
        waitTime: 3000,
        carousel: "page",
      },
    };
  },

  mounted() {
  },
  methods: {
    setTimer() {
      clearInterval(this.timer);
      this.fetchNodeResource();
      this.timer = setInterval(() => {
        this.fetchNodeResource(); //获取-状态
      }, 5000);
    },
    async fetchNodeResource() {
      try {
        let result = await getNodeResource(this.clusterName);
        let data = result.data;
        console.log("获取node资源概况", data);
        this.NodeData = [];
        for (let i = 0; i < data.length; i++) {
          let item = [
            `<span style="color:#9fe6b8;">${data[i].nodeName}</span>`,
            data[i].podCount,
            data[i].cpu,
            data[i].memory,
            data[i].storage,
            `<button style="border-radius: 4px; width: 40px; background-color: ${data[i].nodeStatus === '正常' ? 'green' : 'red'}">${data[i].nodeStatus}</button>`
          ];
          this.NodeData.push(item);
        }
        this.config.data = this.NodeData;
        this.$refs.Node.calcData(this.config);
      } catch (error) {
        handleErrorMessage(error);
      }
    },
    refreshNodeInfo() {
      this.setTimer();
    }
  },
};
</script>

<style lang="scss" scoped>
#center {
  display: flex;
  flex-direction: column;
  .up {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
    .item {
      border-radius: 0.0625rem;
      padding-top: 0.13rem;
      margin-top: 0.1rem;
      width: 32%;
      height: 0.675rem;
      font-size: 0.01rem;
    }
  }
  .down {
    padding: 0.3rem 0.2rem;
    height: 7rem;
    min-width: 3.75rem;
    border-radius: 0.0625rem;
    .bg-color-black {
      height: 6.0625rem;
      border-radius: 0.0625rem;
    }
    .ranking {
      padding: 0.125rem;
      width: 98%;
    }
    .percent {
      width: 54%;
      display: flex;
      flex-wrap: wrap;
      .item {
        width: 50%;
        height: 1.5rem;
        span {
          margin-top: 0.0875rem;
          display: flex;
          justify-content: center;
        }
      }
      .water {
        width: 100%;
      }
    }
  }
}
</style>
