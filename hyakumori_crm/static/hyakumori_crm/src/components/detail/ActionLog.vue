<template>
  <div class="action-log ml-6">
    <h4 class="mb-1">更新履歴</h4>
    <v-progress-linear
      height="2"
      indeterminate
      rounded
      v-if="isLoading"
    ></v-progress-linear>
    <div class="items">
      <log-card
        v-for="log in results"
        :key="log.id"
        :icon="log.icon"
        :action="log.template"
        :date="log.created_at"
        :editor="log.author"
        no-right-action
      />
    </div>
  </div>
</template>

<script>
import LogCard from "./LogCard";
import busEvent from "../../BusEvent";

export default {
  components: { LogCard },
  props: {
    appName: { type: String },
    objectType: { type: String },
    objectId: { type: String },
  },
  data() {
    return {
      isLoading: false,
      results: [],
    };
  },
  created() {
    busEvent.$off("action-log:reload");
    busEvent.$on("action-log:reload", async () => await this.getActionLogs());
  },
  async mounted() {
    await this.getActionLogs();
  },
  methods: {
    async getActionLogs() {
      try {
        this.isLoading = true;
        const response = await this.$rest.get(
          `/activity/ja_JP/${this.appName}/${this.objectType}/${this.objectId}`,
        );
        if (response) {
          this.results = response.results;
        }
      } catch {
      } finally {
        setTimeout(() => {
          this.isLoading = false;
        }, 400);
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.action-log {
  .items {
    max-height: 640px;
    overflow: auto;
  }
}
</style>
