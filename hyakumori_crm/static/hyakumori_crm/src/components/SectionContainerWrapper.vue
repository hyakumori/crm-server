<template>
  <div>
    <content-header
      :content="headerContent"
      :toggleEditBtnContent="toggleEditBtnContent"
      :loading="isLoading"
      @toggleEdit="$emit('toggleEdit', true)"
      :permissions="permissions"
    />
    <slot></slot>
    <template v-if="isEditing">
      <addition-button
        v-if="showAddBtn"
        class="my-2"
        :content="addBtnContent"
        :click="addBtnClickHandler"
      />
      <update-button
        class="mb-9"
        :class="{ 'mt-4': !showAddBtn }"
        :cancel="cancelEdit"
        :save="save"
        :saving="saving"
        :saveDisabled="saveDisabled"
      />
    </template>
  </div>
</template>

<script>
import ContentHeader from "./detail/ContentHeader";
import AdditionButton from "./AdditionButton";
import UpdateButton from "./detail/UpdateButton";

export default {
  components: {
    ContentHeader,
    AdditionButton,
    UpdateButton,
  },
  props: {
    headerContent: String,
    toggleEditBtnContent: String,
    addBtnContent: String,
    addBtnClickHandler: Function,
    permissions: Array,
    isLoading: Boolean,
    save: Function,
    saving: Boolean,
    saveDisabled: Boolean,
    isEditing: Boolean,
    cancelEdit: Function,
    showAddBtn: { type: Boolean, default: true },
  },
};
</script>
