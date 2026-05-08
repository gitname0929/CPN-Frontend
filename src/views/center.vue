<template>
  <div id="center">
<!--    <div class="up">-->
<!--      <div-->
<!--        class="bg-color-black item"-->
<!--        v-for="item in titleItem"-->
<!--        :key="item.title"-->
<!--      >-->
<!--        <p class="colorBlue fw-b" style="text-align: center">-->
<!--          {{ item.title }}-->
<!--        </p>-->
<!--        <div>-->
<!--          <dv-digital-flop-->
<!--            :config="item.number"-->
<!--            style="width: 2.5rem; height: 0.375rem; text-align: center"-->
<!--          />-->
<!--          &lt;!&ndash; padding:0rem 0.9rem 0rem 0.9rem; &ndash;&gt;-->
<!--        </div>-->
<!--      </div>-->
<!--    </div>-->
    <div class="down">
      <div class="ranking bg-color-black">
        <span style="color: #5cd9e8">
          <icon name="align-left"></icon>
        </span>
        <span class="fs-xl text mx-2 mb-1">XXXX</span>
        <!-- <dv-scroll-ranking-board :config="ranking" ref="unit"  style="height:2.75rem" /> -->
        <dv-scroll-board :config="config" ref="Node" style="height: 90%" />
      </div>
<!--      <div class="percent">-->
<!--        <div class="item bg-color-black">-->
<!--          <span>{{ rate[0].id }}</span>-->
<!--          <centerChart-->
<!--            :id="rate[0].id"-->
<!--            :tips="rate[0].tips"-->
<!--            :colorObj="rate[0].colorData"-->
<!--            ref="centerChart1"-->
<!--          />-->
<!--        </div>-->
<!--        <div class="item bg-color-black">-->
<!--          <span>{{ rate[1].id }}</span>-->
<!--          <centerChart-->
<!--            :id="rate[1].id"-->
<!--            :tips="rate[1].tips"-->
<!--            :colorObj="rate[1].colorData"-->
<!--            ref="centerChart2"-->
<!--          />-->
<!--        </div>-->
        <!-- <div class="water">
          <dv-water-level-pond :config="water" style="height: 1.5rem" />
        </div> -->

<!--        <bottomLeftChartState-->
<!--          style=""-->
<!--          ref="bottomLeftChartState"-->
<!--        />-->
<!--      </div>-->
    </div>
  </div>
</template>

<script>
//import centerChart from "../components/echart/center/centerChartRate";
//import bottomLeftChartState from "../components/echart/bottom/bottomLeftChartState";

export default {
  data() {
    return {
      ranking: {
        data: [
          {
            name: "新乡",
            value: 80,
          },
        ],
        waitTime: 4000,
        carousel: "single",
        unit: "件",
      },
      NodeData: [
        ['<span style="color:#9fe6b8;">Node1</span>', "2", "8", "2GB", "4GB", '<button style="border-radius: 4px; width: 40px; background-color: green">正常</button>'],
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
        header: ["Node名称", "Pod数", "VCPU", "内存", "存储", "状态"],
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
      water: {
        data: [5, 45],
        shape: "roundRect",
        formatter: "{value}%",
        waveNum: 3,
      },
      // 通过率和达标率的组件复用数据
      rate: [
        {
          id: "代表自提",
          tips: 22,
          colorData: {
            textStyle: "#3fc0fb",
            series: {
              color: ["#00bcd44a", "transparent"],
              dataColor: {
                normal: "#03a9f4",
                shadowColor: "#97e2f5",
              },
            },
          },
        },
        {
          id: "代表团代提",
          tips: 78,
          colorData: {
            textStyle: "#67e0e3",
            series: {
              color: ["#faf3a378", "transparent"],
              dataColor: {
                normal: "#ff9800",
                shadowColor: "#fcebad",
              },
            },
          },
        },
      ],
    };
  },

  mounted() {
    //this.fetchProposalSubmit(); //获取-数字板数据
    //this.fetchProposalReplace(); //获取-代提百分比
    //this.fetchUnitSum(); //获取-承办单位-排行榜
    //this.setTimer();
  },
  methods: {
    setTimer() {
      this.timer = setInterval(() => {
        this.fetchProposalSubmit(); //获取-数字板数据
        this.fetchProposalReplace(); //获取-代提百分比
        this.fetchUnitSum(); //获取-承办单位-排行榜
        this.fetchState(); //获取-状态
      }, 3000);
    },
    async fetchState() {
      // const { data } = await this.$http.get("getDataByName?name=STATE_SUM");
      //
      // let status = data.status;
      // let dataList = JSON.parse(data.data);
      //
      // if (status === 200) {
      //   this.$refs.bottomLeftChartState.refresh(dataList);
      // }
    },
    async fetchProposalSubmit() {
      // const { data } = await this.$http.get("getDataByName?name=PROPOSAL_SUM");
      //
      // let status = data.status;
      // let titleData = JSON.parse(data.data);
      //
      // var titleRes = new Array();
      // if (status === 200) {
      //   for (var i = titleData.length - 1; i >= 0; i--) {
      //     var item = {
      //       title: "",
      //       number: {
      //         number: [],
      //         toFixed: 0,
      //         content: "{nt}",
      //         style: {
      //           fontSize: 15,
      //           fill: "#3de7c9",
      //         },
      //       },
      //     };
      //     item.title = titleData[i].X0;
      //
      //     item.number.number.push(titleData[i].COUNT);
      //     titleRes.push(item);
      //   }
      //   this.titleItem = titleRes;
      // }
    },
    async fetchProposalReplace() {
      // const { data } = await this.$http.get("getDataByName?name=SUBMIT_SUM");
      //
      // let status = data.status;
      // let dataList = JSON.parse(data.data);
      // if (status === 200) {
      //   this.rate[0].id = dataList[0].X0;
      //   this.rate[1].id = dataList[1].X0;
      //   let submitSumMe = dataList[0].COUNT + 0;
      //   let submitSumNotMe = dataList[1].COUNT + 0;
      //   let count = submitSumMe + submitSumNotMe;
      //   submitSumMe = parseFloat((submitSumMe / count) * 100).toFixed(2);
      //   submitSumNotMe = parseFloat((submitSumNotMe / count) * 100).toFixed(2);
      //
      //   this.$refs.centerChart1.refresh(submitSumMe);
      //   this.$refs.centerChart2.refresh(submitSumNotMe);
      // }
    },
    async fetchUnitSum() {
      // const { data } = await this.$http.get(
      //   "getDataByName?name=UNIT_HANDLE_SUM"
      // );
      //
      // let status = data.status;
      // let dataList = JSON.parse(data.data);
      //
      // let resultList = new Array();
      //
      // if (status === 200) {
      //   for (var i = dataList.length - 1; i >= 0; i--) {
      //     var item = ["组件1", "dev-1"];
      //     let colorCode = "";
      //     if (i % 2 === 0) {
      //       colorCode = '<span style="color:#9fe6b8;">';
      //     } else {
      //       colorCode = '<span style="color:#67e0e3;">';
      //     }
      //     item[0] = colorCode + dataList[i].X0 + "</span>";
      //     item[1] = colorCode + dataList[i].COUNT + "</span>";
      //     resultList.push(item);
      //   }
      //   this.config.data = resultList;
      //   this.$refs["unit"].updateRows(resultList);
      // }
    },
    refreshNodeInfo() {
      this.config.data = this.NodeData;
      this.$refs.Node.calcData(this.config);
    }
  },
  components: {
    //centerChart,
    // centerChart1,
    // centerChart2
    //bottomLeftChartState,
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
    padding: 0.07rem 0.05rem;
    padding-bottom: 0;
    width: 100%;
    display: flex;
    height: 6.5875rem;
    justify-content: space-between;
    .bg-color-black {
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
