<!--<template>
  <div class="topic-selector">
    <div class="module-title">课题选择</div>
    <div class="button-group">
      <div
        v-for="(topic, index) in topics"
        :key="topic.id"
        class="topic-button"
        :class="{ active: activeTopic === topic.id }"
        @click="selectTopic(topic.id)"
      >
        {{ topic.name }}
      </div>
    </div>
  </div>
</template>-->

<template>
  <div id="topic-result">
    <div class="bg-color-black">
      <div class="d-flex pt-2 pl-2">
        <span style="color: #5cd9e8">
          <icon name="chart-bar"></icon>
        </span>
        <span class="fs-xl text mx-2" style="font-size: medium">课题选择</span>
      </div>  
    </div>
  </div>
</template>

<script>
export default {
  name: 'TopicSelector',
  data() {
    return {
      activeTopic: 1, // 默认选中的课题ID
      topics: [
        { id: 1, name: '课题一' },
        { id: 2, name: '课题二' },
        { id: 3, name: '课题三' },
        { id: 4, name: '课题四' },
      ],
    };
  },
  methods: {
    selectTopic(topicId) {
      this.activeTopic = topicId;
      // 通过事件总线发送课题变更事件
      this.$root.$bus.$emit('topic-change', topicId);
    },
  },
};
</script>

<style scoped>
.module-title {
  font-size: 0.2rem;
  color: #00f0ff;
  margin-bottom: 0.1rem;
}
.button-group {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
}
.topic-button {
  width: 45%;
  margin-bottom: 0.1rem;
  padding: 0.1rem 0;
  text-align: center;
  background-color: rgba(0, 240, 255, 0.1);
  border: 1px solid #00f0ff;
  color: #d3d6dd;
  font-size: 0.18rem;
  cursor: pointer;
  transition: all 0.3s;
}
.topic-button:hover {
  background-color: rgba(0, 240, 255, 0.2);
}
.topic-button.active {
  background-color: rgba(0, 240, 255, 0.4);
  color: #ffffff;
  border-color: #ffffff;
}
</style>
