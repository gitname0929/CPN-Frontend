<template>
  <div id="index">
    <dv-full-screen-container class="bg">
      <dv-loading v-if="loading">Loading...</dv-loading>
      <div v-else class="host-body">
        <!-- 第一行 标题 -->
        <div class="d-flex jc-center">
          <dv-decoration-10 style="width:33.3%;height:.0625rem;" />
          <div class="d-flex jc-center">
            <dv-decoration-8 :color="['#568aea', '#000000']" style="width:2.5rem;height:.625rem;" />
            <div class="title">
              <span class="title-text">云平台数据可视化大屏</span>
              <dv-decoration-6
                class="title-bototm"
                :reverse="true"
                :color="['#50e3c2', '#67a1e5']"
                style="width:3.125rem;height:.1rem;"
              />
            </div>
            <dv-decoration-8
              :reverse="true"
              :color="['#568aea', '#000000']"
              style="width:2.5rem;height:.625rem;"
            />
          </div>
          <dv-decoration-10 style="width:33.3%;height:.0625rem; transform: rotateY(180deg);" />
        </div>

        <!-- 第二行 时间-->
        <div class="d-flex jc-between px-2">
          <div class="d-flex" style="width: 100%">
            <div
              class="react-right ml-4"
              style="width: 6.25rem; text-align: left;background-color: #0f1325;"
            >
              <span class="react-before"></span>
              <span class="text"></span>
            </div>
            <div class="react-right ml-3" style="background-color: rgb(26, 92, 215);">
              <span class="text colorBlue"></span>
            </div>
          </div>
          <div style="width: 40%" class="d-flex">
            <div class="react-left bg-color-blue mr-3">
              <span class="text fw-b"></span>
            </div>
            <div
              class="react-left mr-4"
              style="width: 6.25rem; background-color: #0f1325; text-align: right;"
            >
              <span class="react-after"></span>
              <span class="text">{{currtime}}</span>
            </div>
          </div>
        </div>

        <div class="body-box">
          <div class="main-layout">
            <div class="left-panel">
              <dv-border-box-12>
                <topicResult />
              </dv-border-box-12>
            </div>
            <div class="right-panel">
              <div class="right-top-row">
                <dv-border-box-12>
                  <centerLeft1 ref="centerLeft1" />
                </dv-border-box-12>
                <dv-border-box-12>
                  <centerRight2 ref="progressChart" />
                </dv-border-box-12>
              </div>
              <div class="right-bottom-row">
                <dv-border-box-12>
                  <bottomRight ref="NodeInfo" />
                </dv-border-box-12>
              </div>
            </div>
          </div>
        </div>
      </div>
    </dv-full-screen-container>
  </div>
</template>

<script>
import centerLeft1 from "./centerLeft1";
import centerRight2 from "./centerRight2";
import bottomRight from "./bottomRight.vue";
import topicResult from './topicResult.vue';
export default {
  data() {
    return {
      loading: true,
      clusterName: "kubernetes01", 
      currtime: "",
      refreshTimer: null,
      clockTimer: null,
    };
  },
  components: {
    centerLeft1,
    centerRight2,
    bottomRight,
    topicResult,
  },
  mounted() {
    this.cancelLoading();
    this.currentTime();
    this.autoInit();
  },
  beforeDestroy() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
    if (this.clockTimer) {
      clearInterval(this.clockTimer);
    }
  },
  methods: {
    getTime: function () {
      var _this = this;
      let yy = new Date().getFullYear();
      let mm = new Date().getMonth() + 1;
      let dd = new Date().getDate();
      let hh = new Date().getHours();
      let mf =
        new Date().getMinutes() < 10
          ? "0" + new Date().getMinutes()
          : new Date().getMinutes();
      let ss =
        new Date().getSeconds() < 10
          ? "0" + new Date().getSeconds()
          : new Date().getSeconds();
      _this.currtime = yy + "-" + mm + "-" + dd + " " + hh + ":" + mf + ":" + ss;
    },
    currentTime() {
      this.getTime();
      this.clockTimer = setInterval(this.getTime, 500);
    },
    cancelLoading() {
      setTimeout(() => {
        this.loading = false;
      }, 500);
    },
    doRefreshChart(selectCluster) {
      this.clusterName = selectCluster;
      this.$refs.progressChart.updateClusterResource(selectCluster);
      this.$refs.progressChart.startAutoRefresh(selectCluster);
      this.$refs.centerLeft1.clusterName = selectCluster;
      this.$refs.centerLeft1.getNumber();
      this.$refs.NodeInfo.clusterName = selectCluster;
      this.$refs.NodeInfo.refreshNodeInfo();
    },
    refreshAll() {
      if (this.refreshTimer) {
        clearInterval(this.refreshTimer);
      }
      this.refreshTimer = setInterval(() => {
        if (this.clusterName) {
          this.doRefreshChart(this.clusterName);
        }
      }, 5000);
    },
    autoInit() {
      setTimeout(() => {
        this.clusterName = "k3s-cluster";
        this.doRefreshChart("k3s-cluster");
        this.refreshAll();
      }, 800);
    },
  },
  Initialize() {

  }
};
</script>

<style lang="scss">
@import "../assets/scss/index.scss";
</style>
