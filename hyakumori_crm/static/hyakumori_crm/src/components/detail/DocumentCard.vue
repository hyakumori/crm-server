<template>
  <v-card class="document-card d-hover" outlined flat>
    <v-icon class="document-card__icon" size="16">mdi-paperclip</v-icon>
    <span class="document-card__file-name">{{ fileName }}</span>
    <v-spacer></v-spacer>
    <v-btn class="align-self-center ma-3" icon>
      <v-icon size="24">mdi-download</v-icon>
    </v-btn>
  </v-card>
</template>

<script>
export default {
  name: "document-card",

  props: {
    fileName: String,
  },
};
</script>

<style lang="scss" scoped>
@import "../../styles/variables";

.document-card {
  display: flex;
  height: 48px;

  &__icon {
    margin-left: 11px;
    align-self: center;
    @include round-icon(32px);
  }

  &__file-name {
    margin-left: 14px;
    color: #444444;
    font-size: 14px;
    align-self: center;
  }
}
</style>
