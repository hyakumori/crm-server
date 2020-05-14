<template>
  <v-card
    class="document-card d-hover"
    outlined
    flat
    :class="{ deleted: deleted, added: added }"
  >
    <v-icon class="document-card__icon" size="16">mdi-paperclip</v-icon>
    <span class="document-card__file-name">{{ displayFileName }}</span>
    <v-spacer></v-spacer>
    <v-btn
      v-if="deleted"
      class="align-self-center ma-3"
      icon
      @click.stop="$emit('undoDelete')"
    >
      <v-icon>mdi-undo</v-icon>
    </v-btn>
    <v-btn
      class="align-self-center ma-3"
      v-if="isUpdating && !deleted"
      icon
      @click="onDelete"
    >
      <v-icon size="24">mdi-close</v-icon>
    </v-btn>
    <v-btn
      class="align-self-center ma-3"
      v-if="!isUpdating && !deleted && !added"
      icon
      :loading="loading"
      @click="onDownload"
    >
      <v-icon size="24">mdi-download</v-icon>
    </v-btn>
  </v-card>
</template>

<script>
export default {
  name: "document-card",

  props: {
    attachment: [Object, File],
    fileName: String,
    isUpdating: Boolean,
    deleteClick: Function,
    downloadClick: Function,
    loading: Boolean,
    flat: { type: Boolean, default: false },
    deleted: { type: Boolean, default: false },
    added: { type: Boolean, default: false },
  },

  methods: {
    onDelete() {
      this.deleteClick();
    },

    onDownload() {
      this.downloadClick();
    },
  },

  computed: {
    displayFileName() {
      return (
        (this.attachment &&
          this.attachment.attributes &&
          this.attachment.attributes["original_file_name"]) ||
        this.fileName
      );
    },
  },
};
</script>

<style lang="scss" scoped>
@import "../../styles/variables";

.document-card.deleted {
  border: 1px solid #ff5252 !important;
}

.document-card.added {
  border: 1px solid #12c7a6 !important;
}

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
