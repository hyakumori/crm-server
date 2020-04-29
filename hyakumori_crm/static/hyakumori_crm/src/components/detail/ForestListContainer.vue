<template>
  <div>
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="isLoading"
      :displayAdditionBtn="displayAdditionBtn"
      @toggleEdit="val => (isUpdate = val)"
    />
    <forest-info-list
      class="mt-4"
      :forests="tempForests"
      :isUpdate="isUpdate"
      @deleteForest="handleDelete"
      @undoDeleteForest="handleUndoDelete"
      :selectedId="selectingForestId_"
      @selected="
        (fId, ind) => {
          selectingForestId_ = selectingForestId_ === fId ? null : fId;
        }
      "
    />
    <addition-button
      ref="addBtn"
      class="my-2"
      v-if="isUpdate"
      :content="addBtnContent"
      :click="() => (showSelect = true)"
    />
    <SelectListModal
      :loading="loadForests"
      :shown.sync="showSelect"
      :submitBtnText="$t('buttons.add')"
      submitBtnIcon="mdi-plus"
      :handleSubmitClick="handleAdd"
      @needToLoad="handleLoadMore"
      @search="debounceLoadInitForests"
    >
      <template #list>
        <ForestInfoCard
          @selected="
            (fId, inx) => {
              modalSelectingForestId = fId;
              modalSelectingForestIndex = inx;
            }
          "
          v-for="(item, indx) in forestitems.results || []"
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
          :selectedId="modalSelectingForestId"
          flat
        />
      </template>
    </SelectListModal>
    <update-button
      v-if="isUpdate"
      :cancel="cancel"
      :save="handleSave"
      :saving="saving"
      :saveDisabled="saveDisabled"
    />
  </div>
</template>

<script>
import ContainerMixin from "./ContainerMixin";
import ContentHeader from "./ContentHeader";
import ForestInfoList from "./ForestInfoList";
import UpdateButton from "./UpdateButton";
import AdditionButton from "../AdditionButton";
import SelectListModal from "../SelectListModal";
import ForestInfoCard from "../detail/ForestInfoCard";
import { reject, debounce } from "lodash";

export default {
  name: "forest-list-container",

  mixins: [ContainerMixin],

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
  },
  data() {
    return {
      isUpdate: false,
      showSelect: false,
      loadForests: false,
      forestitems: {},
      selectingForestId_: null,
      modalSelectingForestId: null,
      modalSelectingForestIndex: null,
      forestsToAdd: [],
      forestsToDelete: [],
      saving: false,
    };
  },
  created() {
    this.debounceLoadInitForests = debounce(this.loadInitForests, 500);
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
    handleAdd() {
      const forestItem = this.forestitems.results.splice(
        this.modalSelectingForestIndex,
        1,
      )[0];
      forestItem.added = true;
      this.forestsToAdd.push(forestItem);
      this.modalSelectingForestIndex = null;
      this.modalSelectingForestId = null;
    },
    handleDelete(forest) {
      if (forest.added) {
        delete forest.added;
        this.forestsToAdd = reject(this.forestsToAdd, { id: forest.id });
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
      } catch (error) {
        this.saving = false;
      }
    },
    async handleLoadMore() {
      if (!this.forestitems.next && this.loadForests) return;
      this.loadForests = true;
      const resp = await this.$rest.get(this.forestitems.next);
      this.forestitems = {
        next: resp.next,
        previous: resp.previous,
        results: [
          ...this.forestitems.results,
          ...reject(resp.results, f => !!this.forestIdsMap[f.id]),
        ],
      };
      this.loadForests = false;
    },
    async loadInitForests(keyword) {
      this.loadForests = true;
      const resp = await this.$rest.get("/forests/minimal", {
        params: {
          search: keyword || "",
        },
      });
      this.forestitems = {
        next: resp.next,
        previous: resp.previous,
        results: reject(resp.results, f => !!this.forestIdsMap[f.id]),
      };
      this.loadForests = false;
    },
  },
  watch: {
    selectingForestId_(val) {
      this.$emit("update:selectingForestId", val);
    },
    async showSelect(val) {
      if (val && !this.forestitems.next) {
        await this.loadInitForests();
      }
    },
    isUpdate(val) {
      if (!val) {
        this.forestsToAdd.length > 0 && (this.forestsToAdd = []);
        for (let forestToDelete of this.forestsToDelete) {
          this.$set(forestToDelete, "deleted", undefined);
        }
        this.forestsToDelete.length > 0 && (this.forestsToDelete = []);
      }
    },
  },
};
</script>
