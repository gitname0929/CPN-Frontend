<template>
  <div id="centreRight2">
    <div class="bg-color-black">
      <div class="d-flex pt-2 pl-2">
        <span style="color: #5cd9e8">
          <icon name="align-left"></icon> <!--文字前的黑色小图标-->
        </span>
        <span class="fs-xl text mx-2" style="font-size: medium">资源概况</span>
      </div>
      <div class="d-flex jc-center body-box" style="margin-top: 0">
        <dv-capsule-chart :config="config" ref="capsule" style="width: 100%; height: 5.7rem" />
        <!-- <dv-conical-column-chart :config="config" ref="capsule" style="width: 100%; height: 2rem" /> -->
        <!-- <centreLeft1Chart ref="centreLeft1Chart" /> -->

        <!-- ---------------------------------------- -->
        <!-- <centreRight2Chart1></centreRight2Chart1> -->
      </div>
    </div>
  </div>
</template>

<script>
import { getClusterResource } from '../utils/api';
import handleErrorMessage from "@/utils/handleError";

// import centreRight2Chart1 from "@/components/echart/centreRight2/centreRight2Chart1";
// import centreLeft1Chart from "@/components/echart/centerLeft2/centreLeft1Chart";

export default {
  data() {
    return {
      config: {
        data: [
          {
            name: "VCPU",
            value: 0,
          },
          {
            name: "存储",
            value: 0,
          },
          {
            name: "内存",
            value: 0,
          },
          {
            name: "节点数",
            value: 0,
          },
        ],
        unit: "%",
        showValue: true,
      },
      VCPUOption: [
          24,
          16,
          28,
          26
      ],
      memoryOption: [
          26,
          24,
          36,
          30
      ],
      diskOption: [
        10,
        10,
        10,
        11
      ],
      bandOption: [
          100,
          100,
          100,
          100
      ],
      index: 0,
      defaultCluster: "kubernetes",
    };
  },
  components: {
    // centreLeft1Chart,
    // centreRight2Chart1,
  },
  mounted() {
    //this.fetchSystemSum(this.defaultCluster);
    //this.setTimer();
  },
  methods: {
    setTimer() {
      this.timer = setInterval(() => {
        //this.fetchProposalSubmit(); //获取-系统情况分析数据
        this.fetchSystemSum(); //获取-系统情况分析数据
      }, 3000);
    },
    async updateClusterResource(selectCluster) {
      // 这里可以添加获取集群信息的逻辑
      // 例如：调用API获取集群信息
      console.log("获取集群信息: ", selectCluster);
      try {
          const result = await getClusterResource(selectCluster);
          let ClusterResourceData = result.data;
          this.config.data[0].value = ClusterResourceData.cpuUsage;
          this.config.data[1].value = ClusterResourceData.storageUsage;
          this.config.data[2].value = ClusterResourceData.memoryUsage;
          this.config.data[3].value = ClusterResourceData.nodeCount;
          this.$refs.capsule.calcData();
        } catch (error) {
          handleErrorMessage(error);
        }

      // return await this.$http.get(`/api/cluster/${selectCluster}`);
    },
    async fetchSystemSum(selectCluster) {
      console.log("----------------fetchSystemSum--------------------");
      console.log(selectCluster);
      this.config.data[0].value = this.VCPUOption[this.index];
      this.config.data[1].value = this.diskOption[this.index];
      this.config.data[2].value = this.memoryOption[this.index];
      this.config.data[3].value = this.bandOption[this.index];
      this.index = this.index+1;
      this.$refs.capsule.calcData();
      // let url = "/K8sService/cluster/" + selectCluster + "/nodes";
      // console.log(url);
      // let clusterData = []
      // clusterData = await this.$http.get(url);
      // console.log(clusterData.data[0])
      // let usedcpu = parseInt(clusterData.data[0].usedcpu.slice(0,-1));
      // let maxcpu = clusterData.data[0].maxcpu * 1000000000;
      // let usedMemory = parseInt(clusterData.data[0].usedmemory.slice(0,-1));
      // let maxMemory = parseInt(clusterData.data[0].maxmemory.slice(0,-3)) * 1000;
      // this.config.data[0].value = (usedcpu / maxcpu)*100;
      // console.log(this.config.data[0].value);
      // // this.config.data[1].value = clusterData.data[0].maxcpu;
      // this.config.data[2].value = (usedMemory / maxMemory)*100;
      // console.log(this.config.data[2].value);
      // this.$refs.capsule.$forceUpdate();
      // this.config.data[3].value = clusterData.data[0].maxcpu;
      //todo 在这里刷新集群的资源概况
      //const { data } = await this.$http.get("/K8sService/clusters");
      // for (var i = 0;i < this.config.data.length;i++){
      //   var cur = this.config.data[i].value;
      //   console.log(cur)
      //   this.config.data[i].value = cur+1;
      // }
      //let status = data.status;
      // let dataList = JSON.parse(data.data);
      //
      // if (status === 200) {
      //   this.$refs.centreLeft1Chart.refresh(dataList);
      // }
    },
    async fetchProposalSubmit() {
      // const { data } = await this.$http.get("getDataByName?name=SYSTEM_SUM");
      //
      // let status = data.status;
      // let dataList = JSON.parse(data.data);
      //
      // var dataRes = new Array();
      // if (status === 200) {
      //   for (var i = dataList.length - 1; i >= 0; i--) {
      //     var item = {
      //       name: "西峡",
      //       value: 98,
      //     };
      //     item.name = dataList[i].X0;
      //
      //     item.value = dataList[i].COUNT;
      //     dataRes.push(item);
      //   }
      //   this.config.data = dataRes;
      //   this.$refs.capsule.calcData();
      // }
    },
  },
};
</script>

<style lang="scss">
#centreRight2 {
  padding: 0.0625rem;
  height: 5rem;
  min-width: 3.75rem;
  border-radius: 0.0625rem;
  .bg-color-black {
    padding: 0.24rem;
    height: 4.9rem;// 纯色背景高度
    border-radius: 0.125rem;
  }
  .text {
    color: #c3cbde;
  }
  .body-box {
    border-radius: 0.125rem;
    overflow: hidden;
  }
}
</style>
