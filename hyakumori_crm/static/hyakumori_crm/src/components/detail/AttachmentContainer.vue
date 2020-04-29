<template>
  <div>
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :displayAdditionBtn="false"
      @toggleEdit="val => (isUpdate = val)"
    />
    <template v-if="isExpand">
      <attachment-card
        class="mt-4"
        :isUpdate="isUpdate"
        :attaches="attachExpand"
      />
    </template>
    <template v-else>
      <attachment-card
        class="mt-4"
        :isUpdate="isUpdate"
        :attaches="attachCollapse"
      />
    </template>
    <addition-button class="mb-3" v-if="isUpdate" :content="addBtnContent" />
    <update-button v-if="isUpdate" :cancel="cancel.bind(this)" />
    <p
      v-if="isRequiredExpand && attachExpand && attachExpand.length > 0"
      class="expand"
      @click="expandAttachList"
    >
      {{ isExpand ? "一部表示する" : "すべて表示する" }}
    </p>
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import UpdateButton from "./UpdateButton";
import ContainerMixin from "./ContainerMixin";
import AttachmentCard from "./AttachmentCard";
import AdditionButton from "../AdditionButton";

export default {
  name: "attachment-container",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    UpdateButton,
    AdditionButton,
    AttachmentCard,
  },

  props: {
    attaches: Array,
    isRequiredExpand: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      isExpand: false,
      isUpdate: false,
    };
  },

  methods: {
    expandAttachList() {
      this.isExpand = !this.isExpand;
    },
  },

  computed: {
    attachExpand() {
      return this.attaches;
    },

    attachCollapse() {
      return this.attaches.slice(0, 3);
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
