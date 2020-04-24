<template>
  <v-dialog eager v-model="shown_" scrollable width="400" height="480">
    <v-card>
      <v-card-title class="px-4 py-2">
        <TextInput
          @input="val => $emit('search', val)"
          placeholder="姓、名、キーワード"
        />
      </v-card-title>
      <v-divider></v-divider>
      <v-progress-linear v-if="loading" height="2" indeterminate />
      <v-card-text ref="listContent" style="height:228px" class="pa-0">
        <slot name="list"></slot>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-btn text rounded @click="shown_ = false">{{
          $t("buttons.cancel")
        }}</v-btn>
        <v-spacer />
        <v-btn
          rounded
          height="36"
          outlined
          color="primary"
          @click="handleSubmitClick"
          ><v-icon v-if="submitBtnIcon">{{ submitBtnIcon }}</v-icon
          >{{ submitBtnText }}</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import TextInput from "./forms/TextInput";

export default {
  components: { TextInput },
  props: [
    "submitHandler",
    "submitBtnText",
    "submitBtnIcon",
    "shown",
    "loading",
    "handleSubmitClick",
  ],
  data() {
    return {
      shown_: false,
    };
  },
  mounted() {
    this.$refs.listContent.addEventListener("scroll", this.needLoadOnNearEnd);
  },
  watch: {
    shown(val) {
      this.shown_ = val;
    },
    shown_(val) {
      if (val != this.shown) {
        this.$emit("update:shown", val);
      }
    },
  },
  methods: {
    needLoadOnNearEnd(event) {
      const el = event.target;
      if (el.scrollHeight - el.scrollTop === el.clientHeight) {
        this.$emit("needToLoad");
      }
    },
  },
  beforeDestroy() {
    this.$refs.listContent.removeEventListener(
      "scroll",
      this.needLoadOnNearEnd,
    );
  },
};
</script>
