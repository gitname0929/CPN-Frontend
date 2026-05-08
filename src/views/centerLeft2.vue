<template>
  <div id="centreLeft1">
    <div class="bg-color-black">
      <div class="d-flex pt-2 pl-2">
        <span style="color: #5cd9e8">
          <icon name="chart-pie"></icon>
        </span>
        <div class="d-flex">
          <span class="fs-xl text mx-2" style="font-size: medium">数据情况雷达图</span>
          <dv-decoration-1
            style="
              width: 1.25rem;
              height: 0.25rem;
              position: relative;
              top: -0.0575rem;
            "/>
        </div>
      </div>
      <div class="d-flex jc-center" style="margin-top: 0.3rem">
        <centreLeft2Chart />
      </div>
    </div>
  </div>
</template>

<script>
import centreLeft2Chart from "../components/echart/centerLeft2/centreLeft2Chart";
export default {
  data() {
    return {
      config: {
        data: [
          {
            name: "全部",
            value: 1315,
          },
        ],
        color: ["#00baff", "#3de7c9", "#fff", "#ffc530", "#469f4b"],
        lineWidth: 20,
        radius: "55%",
        activeRadius: "60%",
        digitalFlopStyle: {
          fontSize: 15,
        },
        showOriginValue: true,
      },
    };
  },
  components: {
    centreLeft2Chart,
  },
  mounted() {

  },
  methods: {

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
    height: 4.8125rem;
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
