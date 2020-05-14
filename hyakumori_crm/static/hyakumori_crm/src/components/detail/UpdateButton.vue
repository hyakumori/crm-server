<template>
  <div class="update-btn">
    <v-btn
      color="primary"
      :disabled="saveDisabled"
      elevation="0"
      class="mr-2"
      @click.stop="save"
      :loading="saving"
      :small="small"
      >{{ $t("buttons.save") }}</v-btn
    >
    <v-btn class="update-btn__cancel" text :small="small" @click.stop="cancel">{{
      $t("buttons.cancel")
    }}</v-btn>
  </div>
</template>

<script>
export default {
  name: "update-button",
  props: {
    save: Function,
    cancel: Function,
    saveDisabled: Boolean,
    saving: Boolean,
    small: Boolean,
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
