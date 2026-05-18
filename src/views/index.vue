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

        <!--第三行 靠右的再分上下两行-->
		<div class="body-box">
          <!-- 第三行 数据  todo 数据框之间的间隔需要修改 现在没有铺满屏幕宽度-->  
          <div class="main-layout"> <!--原有的两行风格content-box-->
			<!--左侧：课题结果（占满左侧50%-->
			<div class="left-panel">
				<dv-border-box-12>
					<topicResult />
				</dv-border-box-12>
			</div>
			<!-- 右侧：集群指标区 -->
			<div class="right-panel">
			<!-- 右侧第一行：响应情况 + 资源概况 -->
              <div class="right-top-row">
				<dv-border-box-12>
					<centerLeft1 ref="centerLeft1" />
				</dv-border-box-12>
				<dv-border-box-12>
					<centerRight2 ref="progressChart"/>
				</dv-border-box-12>
              </div>
			<!-- 右侧第二行：集群节点资源 -->
              <div class="right-bottom-row">
				<dv-border-box-12>
					<bottomRight ref="NodeInfo"/>
				</dv-border-box-12>
              </div>
			</div>
          </div>
			<!--原有响应情况 中间左1
            <div>
              <dv-border-box-12>
                <centerLeft1 ref="centerLeft1" />
              </dv-border-box-12>
            </div>-->
			<!--原有雷达图
            <div>
              <dv-border-box-12>
                <centerLeft2 />
              </dv-border-box-12>
            </div>-->
			<!--新增课题选择  中间左2
			<div>
              <dv-border-box-12>
                <topicSelector />
              </dv-border-box-12>
			</div>-->
            <!-- 中间 原有算力地图 
            <div>
              <dv-border-box-12>
                <centerMap ref="resourceMap" @parent-event="doRefreshSelect"/>
              </dv-border-box-12>
            </div>-->
			
            <!--原有资源进度条 中间右1
            <div>
              <dv-border-box-12>
                <centerRight2 ref="progressChart"/>
              </dv-border-box-12>
            </div>-->
			<!--原有集群选择 中间右2
            <div>
              <dv-border-box-13>
                <centerRight1 ref="card" @parent-event="doRefreshChart"/>
              </dv-border-box-13>
            </div>-->
          </div>

          <!-- 第四行数据 -->
        <!--<div class="bototm-box">-->
            <!--原有历史数据展示
			<dv-border-box-12>
              <bottomLeft ref="InfoChart"/>
            </dv-border-box-12>-->
			
			<!--新增课题结果展示 下左
			<dv-border-box-12>
				<topicResult />
			</dv-border-box-12>-->

            <!--原有集群资源展示 下右
			<dv-border-box-12>
              <bottomRight ref="NodeInfo"/>
            </dv-border-box-12>-->
        <!--</div>-->
      </div>
    </dv-full-screen-container>
  </div>
</template>

<script>
import centerLeft1 from "./centerLeft1";
// import centerLeft2 from "./centerLeft2";雷达
// import centerMap from "./centerMap.vue";算力地图
//import centerRight1 from "./centerRight1";集群选择
import centerRight2 from "./centerRight2";
// import bottomLeft from "./bottomLeft";历史数据图
import bottomRight from "./bottomRight.vue";
//import topicSelector from './topicSelector.vue';课题选择
import topicResult from './topicResult.vue';
export default {
  data() {
    return {
      loading: true,
      clusterName: "kubernetes01", 
      currtime: "",
    };
  },
  components: {
    centerLeft1,
    // centerLeft2,
    // centerMap,
    //centerRight1,
    centerRight2,
    // bottomLeft,
    bottomRight,
	// 替换
	//topicSelector,
	topicResult,
  },
  mounted() {
    this.cancelLoading();
    // 定时刷新当前时间
    this.currentTime();
    //this.refreshAll();
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
      setInterval(this.getTime, 500);
    },
    cancelLoading() {
      setTimeout(() => {
        this.loading = false;
      }, 500);
    },
    doRefreshSelect(selectCity, cityIndex) {
      this.$refs.card.InitializeCityCluster(selectCity, cityIndex);
    },
    doRefreshChart(selectCluster) {
      console.log("doRefreshChart");
      this.clusterName = selectCluster;
      this.$refs.progressChart.updateClusterResource(selectCluster);
      this.$refs.InfoChart.clusterName = selectCluster;
      this.$refs.InfoChart.refreshDataInfo();
      this.$refs.centerLeft1.clusterName = selectCluster;
      this.$refs.centerLeft1.getNumber();
      this.$refs.NodeInfo.clusterName = selectCluster;
      this.$refs.NodeInfo.refreshNodeInfo();
      //this.refreshAll();
    },
    refreshAll(){
      setInterval(this.doRefreshChart, 5000);
    },
  },
  Initialize() {

  }
};
</script>

<style lang="scss">
@import "../assets/scss/index.scss";
</style>
