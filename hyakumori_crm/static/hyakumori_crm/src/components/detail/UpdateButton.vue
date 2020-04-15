<template>
  <div class="update-btn">
    <v-btn color="primary" elevation="0">保存</v-btn>
    <v-btn text @click="onCancel">キャンセル</v-btn>
  </div>
</template>

<script>
export default {
  name: "update-button",

  props: {
    save: Function,
    cancel: Function,
  },

  methods: {
    onCancel() {
      this.cancel();
    },
  },
};
</script>

<style lang="scss" scoped>
.update-btn {
  display: flex;
}
</style>
