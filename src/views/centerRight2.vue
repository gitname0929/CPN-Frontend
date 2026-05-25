<template>
  <div id="centreRight2">
    <div class="bg-color-black">
      <div class="d-flex pt-2 pl-2">
        <span style="color: #5cd9e8">
          <icon name="align-left"></icon> <!--文字前的黑色小图标-->
        </span>
        <span class="fs-xl text mx-2" style="font-size: medium">集群资源概况</span>
      </div>
      <div class="body-box resource-list">
        <div v-for="item in metrics" :key="item.name" class="resource-item">
          <div class="resource-header">
            <span class="resource-name">{{ item.name }}</span>
            <span class="resource-value">
              <span class="resource-amount">{{ item.amount }}</span>
              {{ formatPercent(item.value) }}
            </span>
          </div>
          <div class="resource-track">
            <div class="resource-fill" :style="{ width: `${clampPercent(item.value)}%` }"></div>
          </div>
        </div>
        <div class="node-summary">
          <span class="node-summary-label">节点数</span>
          <span class="node-summary-value">{{ nodeCount }}</span>
        </div>
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
      currentCluster: "",
      refreshTimer: null,
      metrics: [
        { name: "VCPU", value: 0, amount: "" },
        { name: "存储", value: 0, amount: "" },
        { name: "内存", value: 0, amount: "" },
      ],
      nodeCount: 0,
    };
  },
  components: {
    // centreLeft1Chart,
    // centreRight2Chart1,
  },
  mounted() {
  },
  beforeDestroy() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
    }
  },
  methods: {
    clampPercent(value) {
      const numeric = Number(value);
      if (!Number.isFinite(numeric)) {
        return 0;
      }
      return Math.max(0, Math.min(100, numeric));
    },
    formatPercent(value) {
      const numeric = Number(value);
      if (!Number.isFinite(numeric)) {
        return "0.0%";
      }
      return `${numeric.toFixed(1)}%`;
    },
    async updateClusterResource(selectCluster) {
      this.currentCluster = selectCluster;
      console.log("获取集群信息: ", selectCluster);
      try {
        const result = await getClusterResource(selectCluster);
        const clusterResourceData = result.data;
        this.metrics = [
          {
            name: "VCPU",
            value: clusterResourceData.cpuUsage,
            amount: clusterResourceData.cpuUsed || "",
          },
          {
            name: "存储",
            value: clusterResourceData.storageUsage,
            amount: `${clusterResourceData.storageUsed || ""} / ${clusterResourceData.storageTotal || ""}`,
          },
          {
            name: "内存",
            value: clusterResourceData.memoryUsage,
            amount: `${clusterResourceData.memoryUsed || ""} / ${clusterResourceData.memoryTotal || ""}`,
          },
        ];
        this.nodeCount = clusterResourceData.nodeCount || 0;
      } catch (error) {
        handleErrorMessage(error);
      }
    },
    startAutoRefresh(selectCluster) {
      if (this.refreshTimer) {
        clearInterval(this.refreshTimer);
      }
      this.currentCluster = selectCluster;
      this.refreshTimer = setInterval(() => {
        if (this.currentCluster) {
          this.updateClusterResource(this.currentCluster);
        }
      }, 1000);
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
  .resource-list {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    padding: 0.35rem 0.2rem 0;
  }
  .resource-item {
    display: flex;
    flex-direction: column;
    gap: 0.12rem;
  }
  .resource-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #d9e7ff;
    font-size: 0.18rem;
  }
  .resource-name {
    font-weight: 600;
    letter-spacing: 0.02rem;
  }
  .resource-value {
    color: #5cd9e8;
    font-family: DIN, "Helvetica Neue", Arial, sans-serif;
    font-size: 0.16rem;
  }
  .resource-amount {
    color: #d9e7ff;
    margin-right: 0.08rem;
  }
  .resource-track {
    width: 100%;
    height: 0.2rem;
    border-radius: 999px;
    overflow: hidden;
    background: rgba(92, 217, 232, 0.12);
    border: 1px solid rgba(92, 217, 232, 0.18);
  }
  .resource-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #1d9bf0 0%, #5cd9e8 100%);
    box-shadow: 0 0 0.12rem rgba(92, 217, 232, 0.35);
    transition: width 0.3s ease;
  }
  .node-summary {
    margin-top: 0.12rem;
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    padding: 0.16rem 0.2rem;
    border-radius: 0.1rem;
    background: rgba(20, 37, 68, 0.55);
    color: #d9e7ff;
  }
  .node-summary-label {
    font-size: 0.18rem;
  }
  .node-summary-value {
    color: #5cd9e8;
    font-size: 0.32rem;
    font-weight: 700;
    line-height: 1;
  }
}
</style>
