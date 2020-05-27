<template>
  <div>
    <content-header
      :content="headerContent"
      :toggleEditBtnContent="toggleEditBtnContent"
      :loading="isLoading"
      :displayAdditionBtn="displayAdditionBtn"
      @toggleEdit="val => (isEditing = val)"
    />
    <forest-info-list
      class="mt-4"
      :forests="tempForests"
      :isUpdate="isEditing"
      @deleteForest="handleDelete"
      @undoDeleteForest="handleUndoDelete"
      :selectedId="selectingForestId_"
      @selected="
        (fId, ind) => {
          selectingForestId_ = selectingForestId_ === fId ? null : fId;
        }
      "
      :itemClickable="itemClickable"
    />
    <addition-button
      ref="addBtn"
      class="my-2"
      v-if="isEditing"
      :content="addBtnContent"
      :click="() => (showSelect = true)"
    />
    <SelectListModal
      :loading="itemsForAddingLoading"
      :shown.sync="showSelect"
      :submitBtnText="$t('buttons.add')"
      submitBtnIcon="mdi-plus"
      :handleSubmitClick="handleAdd"
      :handleCancelClick="onCancel"
      :disableAdditionBtn="!modalSelectingId"
      @needToLoad="handleLoadMore"
      @search="debounceLoadInitItemsForAdding"
      ref="selectListModal"
    >
      <template #list>
        <ForestInfoCard
          @selected="
            (fId, inx) => {
              modalSelectingId = fId;
              modalSelectingIndex = inx;
            }
          "
          v-for="(item, indx) in itemsForAdding.results || []"
          :key="item.id"
          :card_id="item.id"
          :forestId="item.internal_id"
          :customerCount="item.customers_count"
          :address="
            `${item.cadastral.subsector} ${item.cadastral.sector} ${item.cadastral.municipality} ${item.cadastral.prefecture}`
          "
          :showAction="false"
          :index="indx"
          mode="search"
          :selectedId="modalSelectingId"
          flat
          clickable
        />
      </template>
    </SelectListModal>
    <update-button
      v-if="isEditing"
      :cancel="cancel"
      :save="handleSave"
      :saving="saving"
      :saveDisabled="saveDisabled"
    />
  </div>
</template>

<script>
import ContainerMixin from "./ContainerMixin";
import SelectListModalMixin from "./SelectListModalMixin";
import ContentHeader from "./ContentHeader";
import ForestInfoList from "./ForestInfoList";
import UpdateButton from "./UpdateButton";
import AdditionButton from "../AdditionButton";
import SelectListModal from "../SelectListModal";
import ForestInfoCard from "../detail/ForestInfoCard";
import { reject, debounce } from "lodash";

export default {
  name: "forest-list-container",

  mixins: [ContainerMixin, SelectListModalMixin],

  components: {
    ContentHeader,
    ForestInfoList,
    UpdateButton,
    AdditionButton,
    SelectListModal,
    ForestInfoCard,
  },

  props: {
    id: String,
    forests: Array,
    displayAdditionBtn: Boolean,
    selectingForestId: String,
    itemClickable: { type: Boolean, default: false },
  },
  data() {
    return {
      selectingForestId_: null,
      forestsToAdd: [],
      forestsToDelete: [],
      itemsForAddingUrl: "/forests/minimal",
    };
  },
  computed: {
    tempForests() {
      return [...this.forests, ...this.forestsToAdd];
    },
    forestIdsMap() {
      return Object.fromEntries(this.tempForests.map(f => [f.id, true]));
    },
    forestIdsToAdd() {
      return this.forestsToAdd.map(f => f.id);
    },
    forestIdsToDelete() {
      return this.forestsToDelete.map(f => f.id);
    },
    saveDisabled() {
      return (
        this.forestIdsToDelete.length === 0 && this.forestIdsToAdd.length === 0
      );
    },
  },
  methods: {
    itemsForAddingResultFilter(f) {
      return !!this.forestIdsMap[f.id];
    },
    handleAdd() {
      const forestItem = this.itemsForAdding.results.splice(
        this.modalSelectingIndex,
        1,
      )[0];
      forestItem.added = true;
      this.forestsToAdd.push(forestItem);
      this.modalSelectingIndex = null;
      this.modalSelectingId = null;
      if (this.itemsForAdding.results.length <= 3) {
        this.handleLoadMore();
      }
    },
    handleDelete(forest) {
      if (forest.added) {
        delete forest.added;
        this.forestsToAdd = reject(this.forestsToAdd, { id: forest.id });
        this.itemsForAdding = { results: [] };
      } else {
        this.$set(forest, "deleted", true);
        this.forestsToDelete.push(forest);
      }
    },
    handleUndoDelete(forest) {
      this.$set(forest, "deleted", undefined);
      this.forestsToDelete = reject(this.forestsToDelete, { id: forest.id });
    },
    async handleSave() {
      try {
        this.saving = true;
        await this.$rest.put(`/customers/${this.id}/forests`, {
          added: this.forestIdsToAdd,
          deleted: this.forestIdsToDelete,
        });
        this.$emit("saved");
        this.saving = false;
        this.forestsToDelete = [];
        this.forestsToAdd = [];
        this.itemsForAdding = { results: [] };
      } catch (error) {
        this.saving = false;
        if (error.response && error.response.status < 500)
          this.$dialog.notify.error(
            error.response.data.detail || error.response.statusText,
          );
      }
    },
  },
  watch: {
    selectingForestId_(val) {
      this.$emit("update:selectingForestId", val);
    },
    isEditing(val) {
      if (!val) {
        if (this.forestsToAdd.length > 0) {
          this.forestsToAdd = [];
          this.itemsForAdding = { results: [] };
        }
        for (let forestToDelete of this.forestsToDelete) {
          this.$set(forestToDelete, "deleted", undefined);
        }
        if (this.forestsToDelete.length > 0) {
          this.forestsToDelete = [];
          this.itemsForAdding = { results: [] };
        }
      }
    },
  },
};
</script>
