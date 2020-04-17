<template>
  <div class="content-header d-flex flex-column">
    <div class="d-flex">
      <div class="d-flex align-center content-header__content">
        {{ content }}
        <v-img
          class="ml-2"
          src="../../assets/img/detail-header-icon.png"
          height="10"
          width="13"
        >
        </v-img>
      </div>
      <v-spacer></v-spacer>
      <addition-button
        v-if="displayAdditionBtn"
        :content="editBtnContent"
        :click="onUpdate.bind(this)"
      />
    </div>
    <v-progress-linear v-if="loading" height="2" indeterminate />
    <v-divider v-else class="content-header__divider mt-3"></v-divider>
  </div>
</template>

<script>
import AdditionButton from "../AdditionButton";

export default {
  name: "content-header",

  components: {
    AdditionButton,
  },

  props: {
    loading: Boolean,
    content: String,
    editBtnContent: String,
    update: Boolean,
    displayAdditionBtn: {
      type: Boolean,
      default: true,
    },
  },

  methods: {
    onUpdate() {
      this.$emit("update", true);
    },
  },
};
</script>

<style lang="scss" scoped>
.content-header {
  width: 100%;
  display: flex;

  &__content {
    font-size: 17px;
    font-weight: bold;
  }
}
</style>
