<template>
  <v-row>
    <template v-for="(info, index) in infos">
      <v-col cols="6" :key="index">
        <text-info
          :label="info.label"
          :value="info.value"
          :isUpdate="isUpdate"
        />
      </v-col>
    </template>
  </v-row>
</template>

<script>
import TextInfo from "../detail/TextInfo";

export default {
  name: "basic-info",

  components: {
    TextInfo,
  },

  props: {
    isUpdate: Boolean,
    isSave: Boolean,
    infos: Array,
  },

  watch: {
    isSave(oldVal, newVal) {
      if (oldVal !== newVal) {
        if (newVal) {
          this.$emit("updateInfo", this.infos);
        }
      }
    },
  },
};
</script>
