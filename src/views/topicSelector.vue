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
  <div id="topic-result" class="topic-selector">
    <div class="bg-color-black">
      <div class="d-flex pt-2 pl-2">
        <span style="color: #5cd9e8">
          <icon name="chart-bar"></icon>
        </span>
        <span class="fs-xl text mx-2" style="font-size: medium">课题选择</span>
      </div>
      <div class="button-group">
		<div
		v-for="topic in topics"
		:key="topic.id"
		class="topic-button"
		:class="{ active: activeTopic === topic.id }"
		@click="selectTopic(topic.id)"
		>
		<span class="btn-icon">{{ topic.icon }}</span>
		<span class="btn-text">{{ topic.name }}</span>
		</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TopicSelector',
  data() {
    return {
      activeTopic: 1,
      topics: [
        { id: 1, name: '课题一', icon: '📊' },
        { id: 2, name: '课题二', icon: '📈' },
        { id: 3, name: '课题三', icon: '📋' },
        { id: 4, name: '课题四', icon: '🔬' },
      ],
    };
  },
  methods: {
    selectTopic(topicId) {
      this.activeTopic = topicId;
      this.$root.$bus.$emit('topic-change', topicId);
    },
  },
};
</script>

<style scoped>
.module-title {
  font-size: 0.18rem;
  color: #00f0ff;
  margin-bottom: 0.12rem;
  padding-left: 0.1rem;
  border-left: 3px solid #00f0ff;
}

.button-group {
  display: flex;
  flex-wrap: wrap;
  height: 60%;
  gap: 0.1rem;
}

.topic-button {
  flex: 1 1 60%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.06rem;
  padding: 0.50rem 0.1rem;
  background-color: rgba(0, 240, 255, 0.05);
  border: 1px solid rgba(0, 240, 255, 0.3);
  border-radius: 4px;
  color: #d3d6dd;
  font-size: 0.16rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.topic-button:hover {
  background-color: rgba(0, 240, 255, 0.15);
  border-color: rgba(0, 240, 255, 0.6);
  transform: scale(1.02);
}

.topic-button.active {
  background-color: rgba(0, 240, 255, 0.25);
  border-color: #00f0ff;
  color: #ffffff;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
}

.btn-icon {
  font-size: 0.18rem;
}

.btn-text {
  font-weight: 500;
}
</style>
