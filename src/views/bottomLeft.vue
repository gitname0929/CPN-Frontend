<template>
  <div id="bottomLeft">
    <div class="bg-color-black" >
      <div class="d-flex pt-2 pl-2">
        <span style="color: #5cd9e8">
          <icon name="chart-bar"></icon>
        </span>
        <div class="d-flex">
          <span class="fs-xl text mx-2" style="font-size: medium">数据统计图</span>
          <el-radio-group class="fs-xl text mx-2" v-model="radioValue" size="small" @input="refreshDataInfo">
            <el-radio label="history">历史</el-radio>
            <el-radio label="prediction">预测</el-radio>
          </el-radio-group>
        </div>
      </div>
      <div>
        <bottomLeftChart ref="bottomLeftChart"/>
      </div>
    </div>
  </div>
</template>

<script>
import bottomLeftChart from "@/components/echart/bottom/bottomLeftChart";
export default {
  data() {
    return {
      clusterName:'kubernetes01', 
      radioValue: 'history', // 默认选中第一个选项
    };
  },
  components: {
    bottomLeftChart,
  },
  mounted() {
    //this.changeTiming();
  },
  methods: {
    changeTiming() {
      setInterval(() => {
        //this.fetchSystemSum(); //获取-状态
      }, 3000);
    },
    refreshDataInfo() {
      if (this.radioValue === 'history') {
        this.$refs.bottomLeftChart.changeResourceData(this.clusterName);
      } else if (this.radioValue === 'prediction') {
        this.$refs.bottomLeftChart.changePredictionData(this.clusterName);
      }
    }
  },
};
</script>

<style lang="scss">
#bottomLeft {
  padding: 0.3rem 0.2rem;
  height: 7rem;
  min-width: 3.75rem;
  border-radius: 0.0625rem;
  .bg-color-black {
    height: 6.0625rem;
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
}
</style>
