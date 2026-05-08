<template>
  <div>
    <el-table
      :data="dataCenters"
      height="4rem"
      style="width: 8rem"
      @row-click="onRowClickWrapper"
    >
      <el-table-column type="index" label="#" width="60" />
      <el-table-column prop="name" label="城市" />
      <el-table-column prop="value" label="数据中心数" width="120" />
      <el-table-column label="操作" width="120">
        <template slot-scope="{ row, $index }">
          <el-button type="primary" size="mini" @click.stop="onRowClick(row, $index)">选择</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
// 移除地图相关依赖，保留数据拉取与错误处理
import handleErrorMessage from "@/utils/handleError";
import { getDataCenters } from "@/utils/api";
export default {
  data() {
    return {
      selectCityName: "",
      dataCenters: [{ name: "南京市", value: 8 }],
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      try {
        const data = await getDataCenters();
        let list = data.data || [];
        // 按原逻辑从索引1开始加入（如果需要全量可改为 i=0）
        const rows = [];
        for (let i = 0; i < list.length; i++) {
          rows.push({ name: list[i].city, value: list[i].dataCenterNum , id : list[i].id});
        }
        this.dataCenters = rows;
      } catch (error) {
        console.error("获取数据中心失败", error);
        handleErrorMessage(error);
      }
    },
    // 行点击事件包装：Element UI 传 (row, column, event)，这里只取 row
    onRowClickWrapper(row) {
      const idx = this.dataCenters.findIndex(r => r === row || r.name === row.name);
      this.onRowClick(row, idx);
    },
    onRowClick(row, index) {
      // 如果第二个参数不是数字，兜底重新计算
      if (typeof index !== 'number' || index < 0) {
        index = this.dataCenters.findIndex(r => r === row || r.name === row.name);
      }
      this.handleMapClick({ name: row.name, dataIndex: row.id });
    },
    handleMapClick(data) {
      const { name, dataIndex } = data;
      const cityId = dataIndex;
      console.log("handleMapClick", name, cityId);
      if (typeof cityId !== 'number') return; // 防御
      if (name !== this.selectCityName) {
        this.selectCityName = name;
        this.$emit("parent-event", name, cityId);
      } else {
        this.selectCityName = "";
        this.$emit("parent-event", "未选择", -1);
      }
    },
    refresh(data) {
      this.dataCenters = Array.isArray(data) ? data : [];
    },
  },
};
</script>

<style lang="scss" scoped>
/* 将表格背景（含表头、行、悬停）设为透明 */
::v-deep .el-table,
::v-deep .el-table__header-wrapper,
::v-deep .el-table__body-wrapper,
::v-deep .el-table th,
::v-deep .el-table tr,
::v-deep .el-table td {
  background-color: transparent !important;
}

/* 去除顶部细线背景 */
::v-deep .el-table::before {
  background-color: transparent !important;
}

/* 悬停行保持透明（若需要高亮可改为半透明色） */
::v-deep .el-table--enable-row-hover .el-table__body tr:hover > td {
  background-color: transparent !important;
}
</style>
