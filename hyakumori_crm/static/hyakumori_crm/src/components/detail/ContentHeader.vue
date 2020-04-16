<template>
  <div class="content-header d-flex flex-column">
    <div class="d-flex">
      <div class="d-flex align-center content-header__content">
        {{ content }}
        <v-icon right>mdi-folder</v-icon>
      </div>
      <v-spacer></v-spacer>
      <addition-button
        v-if="displayAdditionBtn"
        :content="editBtnContent"
        :click="onUpdate.bind(this)"
      />
    </div>
    <v-divider class="content-header__divider mt-3"></v-divider>
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

  &__divider {
    border: 1px solid #e1e1e1;
  }
}
</style>
