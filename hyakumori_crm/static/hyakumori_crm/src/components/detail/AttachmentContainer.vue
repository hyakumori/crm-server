<template>
  <div>
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="loading"
      :permissions="['just_unnecessary']"
    />
    <template v-if="isExpand">
      <attachment-card
        class="mt-4"
        :isUpdate="isUpdate"
        :attaches="archiveExpand"
        :ripple="false"
      />
    </template>
    <template v-else>
      <attachment-card
        class="mt-4"
        :isUpdate="isUpdate"
        :attaches="archiveCollapse"
        :ripple="false"
      />
    </template>
    <p
      v-if="isRequiredExpand && archiveExpand && archiveExpand.length > 0"
      class="expand"
      @click="this.isExpand = !this.isExpand"
    >
      {{ isExpand ? "一部表示する" : "すべて表示する" }}
    </p>
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import AttachmentCard from "./AttachmentCard";

export default {
  name: "attachment-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    AttachmentCard,
  },

  props: {
    id: String,
    isRequiredExpand: {
      type: Boolean,
      default: true,
    },
    archives: { type: Array, default: () => [] },
  },

  data() {
    return {
      loading: false,
      isExpand: false,
      isUpdate: false,
    };
  },
  computed: {
    archiveExpand() {
      return this.archives;
    },

    archiveCollapse() {
      return this.archives.slice(0, 3);
    },
  },
};
</script>

<style lang="scss" scoped>
.expand {
  margin-top: 20px;
  margin-bottom: 50px;
  width: fit-content;
  font-size: 14px;
  color: #999999;

  &:hover {
    cursor: pointer;
  }
}
</style>
