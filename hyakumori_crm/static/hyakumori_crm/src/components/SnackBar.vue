<template>
  <v-snackbar
    :value="isShow"
    bottom
    :color="color"
    :timeout="timeout"
    @input="onDismiss"
  >
    {{ msg }}
    <v-btn text @click="closeSnackbar">{{ $t("raw_text.agree") }}</v-btn>
  </v-snackbar>
</template>

<script>
export default {
  name: "snack-bar",

  props: {
    isShow: Boolean,
    msg: String,
    color: String,
    timeout: Number,
  },

  methods: {
    closeSnackbar() {
      this.$emit("dismiss", false);
    },

    onDismiss(val) {
      this.$emit("dismiss", val);
    },
  },
};
</script>
