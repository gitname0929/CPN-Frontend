<template>
  <div id="centreRight1">
    <div class="bg-color-black">
      <div class="d-flex pt-2 pl-2">
        <span style="color: #5cd9e8">
          <icon name="chart-line"></icon>
        </span>
        <div class="d-flex">
          <span class="fs-xl text mx-2" style="font-size: medium">操作</span>
        </div>
      </div>
      <div class="d-flex jc-center body-box">
        <div class="cluster-select"  style="margin: 8px; width: 100%" >
          <el-select v-model="selectCluster" @change="refreshClusterInfo(selectCluster)" placeholder="请选择集群"  style="font-size: small">
            <el-option
                v-for="item in clusterOptions"
                :key="item.name"
                :label="item.name"
                :value="item.name">
            </el-option>
          </el-select>
        </div>
        <el-card style="background-color: white" ref="InfoCard">
          <div slot="header" >
            <i class="el-icon-location-information" /><span style="margin: 8px">当前选中： {{this.clickedPosition}}</span>
          </div>
          <div >
            <i class="el-icon-coin" /><span style="margin: 8px">类型：{{this.clusterType}}</span>
          </div><br/>
          <div>
            <i class="el-icon-cpu" /><span style="margin: 8px">集群ip： {{this.clusterIpPort}}</span>
          </div><br/>
          <div>
            <i class="el-icon-time" /><span style="margin: 8px">创建时间： {{this.createTime}}</span>
          </div><br/>
        </el-card>
<!--        <dv-scroll-board-->
<!--          :config="config"-->
<!--          ref="log"-->
<!--          style="width: 3.375rem; height: 4.28rem"-->
<!--        />-->
      </div>
    </div>
  </div>
</template>

<script>
import { getAllClusterInfo,getClusterBaseInfo } from "@/utils/api";
import handleErrorMessage from "@/utils/handleError";
export default {
  data() {
    return {
      config: {
        header: ["用户名",
        // "时间",
        "操作状态"],
        data: [
          ["张三", "<span  class='colorGrass'>操作成功</span>"],
        ],
        rowNum: 8, //表格行数
        headerHeight: 35,
        headerBGC: "#0f1325", //表头
        oddRowBGC: "#0f1325", //奇数行
        evenRowBGC: "#171c33", //偶数行
        index: false,
        columnWidth: [150],
        align: ["left"],
        clusterInfo: [],
      },
      clusterOptions: [
        //{name: "kubernetes00"},
      ],
      clickedPosition: "未选择",
      clusterIpPort: "xx.xx.xx.xx:xx",
      clusterType: "",
      createTime: "",
      selectCluster: "",
    };
  },
  components: {},
  mounted() {
    //this.changeTiming();
  },
  methods: {
    changeTiming() {
      setInterval(() => {
        this.fetchCluster(); //获取-建议情况
      }, 3000);
    },
    async fetchProposalSubmit() {
      // const { data } = await this.$http.get(
      //   "getDataByName?name=LOGIN_LOG"
      // );
      //
      // let status = data.status;
      // let dataList = JSON.parse(data.data);
      //
      // var dataArr = new Array();
      // if (status === 200) {
      //   for (var i = dataList.length - 1; i >= 0; i--) {
      //     let item =new Array();
      //     item.push(dataList[i].NAME);
      //     // item.push(dataList[i].TIME);
      //     item.push("<span  class='colorGrass'>"+dataList[i].MESSAGE+"</span>");
      //     dataArr.push(item);
      //   }
      //   this.config.data = dataArr;
      //   this.$refs["log"].updateRows(dataArr);
      // }
    },
    async refreshClusterInfo(selectCluster) {
      try {
        const result = await getClusterBaseInfo(selectCluster);
        let clusterData = result.data;
        console.log("选择的集群信息", clusterData);
        this.clusterType = clusterData.type;
        this.clusterIpPort = clusterData.ip + ":" + clusterData.port;
        this.createTime = clusterData.createTime;
        this.index = this.index+1;
        this.refreshResourceChart(selectCluster);
      } catch (error) {
        handleErrorMessage(error);
      }
    },
    refreshResourceChart(selectCluster) {
      this.$emit('parent-event', selectCluster);
    },
    async InitializeCityCluster(selectCity, cityIndex) {
      if (cityIndex === -1) {
        this.clusterOptions = [];
      }else {
        try {
          const cityId = cityIndex;
          const result = await getAllClusterInfo(cityId);
          let cityClusterData = result.data;
          console.log("refreshCardInfo", cityClusterData);
          var clusterOptions = [];
          for (var i = 0;i < cityClusterData.length;i++) {
            var item = {
              name: cityClusterData[i].name
            }
            clusterOptions.push(item);
          }
          this.clusterOptions = clusterOptions;
        } catch (error) {
          handleErrorMessage(error);
        }
      }
      console.log("selectCity", selectCity);
      this.clickedPosition = selectCity;
      this.clusterIpPort = "xx.xx.xx.xx:xx";
      this.clusterType = "";
      this.createTime = "";
      this.selectCluster = "";
    },
  },
};
</script>

<style lang="scss">
#centreRight1 {
  padding: 0.2rem;
  height: 5.125rem;
  min-width: 3.75rem;
  border-radius: 0.0625rem;
  .bg-color-black {
    height: 2.8125rem;
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
