<template>
  <div class="update-btn">
    <v-btn
      color="primary"
      elevation="0"
      class="mr-2"
      :loading="isLoading"
      @click="onSave"
      :disabled="disabled"
      >保存</v-btn
    >
    <v-btn class="update-btn__cancel" text @click="onCancel">キャンセル</v-btn>
  </div>
</template>

<script>
export default {
  name: "update-button",

  props: {
    save: Function,
    cancel: Function,
    isLoading: Boolean,
    disabled: Boolean,
  },

  methods: {
    onCancel() {
      if (this.cancel) {
        this.cancel();
      }
    },

    onSave() {
      if (this.save) {
        this.save();
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.update-btn {
  display: flex;
  font-weight: bold;

  &__cancel {
    color: #999999;
  }
}
</style>
