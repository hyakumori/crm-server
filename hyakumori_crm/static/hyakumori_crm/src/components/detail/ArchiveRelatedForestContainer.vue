<template>
  <div>
    <content-header
      class="mb-4"
      :content="headerContent"
      :toggleEditBtnContent="toggleEditBtnContent"
      :loading="loading"
      @toggleEdit="handleEdit"
    />

    <forest-info-list
      :forests="relatedForests"
      :isUpdate="isUpdate"
      @deleteForest="deleteForest"
      @undoDeleteForest="handleUndoDelete"
    />
    <template v-if="isUpdate">
      <addition-button
        class="my-2"
        :content="addBtnContent"
        :click="onAdditionClick.bind(this)"
      />
      <update-button
        :cancel="cancel.bind(this)"
        :save="save.bind(this)"
        :saveDisabled="addedForests.length === 0 && deletedForests.length === 0"
        :saving="addRelatedForestLoading"
      />
    </template>
    <select-list-modal
      :shown="shown"
      :loading="fetchAllForestLoading"
      :submitBtnText="$t('buttons.add')"
      :handleSubmitClick="submitRelatedForest.bind(this)"
      :disableAdditionBtn="fetchAllForestLoading || !selectingForestId"
      :handle-cancel-click="onCancel"
      submitBtnIcon="mdi-plus"
      @search="deboundGetSearch"
      @needToLoad="handleLoadMore"
      @update:shown="val => (shown = val)"
      ref="selectListModal"
    >
      <template #list>
        <forest-info-card
          v-for="(item, index) in allForests"
          mode="search"
          :key="index"
          :index="index"
          :forest-id="item.internal_id"
          :card_id="item.id"
          :customerCount="item.customers_count"
          :address="getFullAddress(item)"
          :showAction="false"
          :selectedId="selectingForestId"
          @selected="handleForestSelected"
          clickable
          flat
        />
      </template>
    </select-list-modal>
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import ForestInfoList from "./ForestInfoList";
import UpdateButton from "./UpdateButton";
import AdditionButton from "../AdditionButton";
import SelectListModal from "../SelectListModal";
import ForestInfoCard from "./ForestInfoCard";
import { cloneDeep, pullAllWith, debounce } from "lodash";

export default {
  name: "archive-related-forest-container",

  mixins: [ContainerMixin],

  components: {
    ForestInfoList,
    ContentHeader,
    UpdateButton,
    AdditionButton,
    SelectListModal,
    ForestInfoCard,
  },

  data() {
    return {
      id: this.$route.params.id,
      isUpdate: false,
      shown: false,
      relatedForests: [],
      immutableRelatedForest: [],
      loading: false,
      fetchAllForestLoading: false,
      allForests: [],
      immutableAllForest: [],
      next: "",
      selectingForestId: null,
      selectingForestIndex: null,
      addRelatedForestLoading: false,
      searchNext: null,
    };
  },

  created() {
    this.deboundGetSearch = debounce(this.fetchSearchForest, 500);
  },

  mounted() {
    this.fetchRelatedForests();
  },

  methods: {
    onCancel() {
      this.selectingForestId = null;
      this.selectingForestIndex = null;
    },
    handleForestSelected(fId, fIndex) {
      this.selectingForestId = fId;
      this.selectingForestIndex = fIndex;
    },

    handleEdit(val) {
      if (!this.isUpdate && this.relatedForests) {
        this.immutableRelatedForest = cloneDeep(this.relatedForests);
      }
      this.isUpdate = val;
    },

    cancel() {
      this.isUpdate = false;
      this.relatedForests = cloneDeep(this.immutableRelatedForest);
      this.allForests = cloneDeep(this.immutableAllForest);
    },

    async save() {
      if (this.relatedForests.length === 0) {
        this.isUpdate = false;
      } else {
        this.addRelatedForestLoading = true;
        await this.deleteRelatedForests();
        await this.addRelatedForests();
        this.addRelatedForestLoading = false;
        this.isUpdate = false;
      }
    },

    async deleteRelatedForests() {
      if (this.deletedForests.length > 0) {
        const deletedIds = this.deletedForests.map(f => f.id);
        const deleteRequest = { ids: deletedIds };
        const isDeleted = await this.$rest.delete(
          `/archives/${this.id}/forests`,
          {
            data: deleteRequest,
          },
        );
        if (isDeleted) {
          this.selectingForestId = null;
          this.relatedForests = this.removeDuplicateForests(
            this.relatedForests,
            this.deletedForests,
          );
          const pureForests = cloneDeep(this.deletedForests);
          pureForests.forEach(f => (f.deleted = false));
          this.allForests.push(...pureForests);
          this.immutableAllForest = cloneDeep(this.allForests);
        }
      }
    },

    async addRelatedForests() {
      if (this.addedForests.length > 0) {
        const addedIds = this.addedForests.map(f => f.id);
        const addRequest = { ids: addedIds };
        const newRelatedForests = await this.$rest.post(
          `/archives/${this.id}/forests`,
          addRequest,
        );
        if (newRelatedForests) {
          const tempForest = this.removeDuplicateForests(
            this.relatedForests,
            newRelatedForests.data,
          );
          this.allForests = this.removeDuplicateForests(
            this.allForests,
            this.addedForests,
          );
          this.immutableAllForest = cloneDeep(this.allForests);
          tempForest.push(...newRelatedForests.data);
          this.relatedForests = tempForest;
        }
      }
    },

    onAdditionClick() {
      this.shown = true;
      if (this.allForests.length === 0 || this.next === "") {
        this.fetchAllForests(this.next);
      }
    },

    getFullAddress(data) {
      if (!data.cadastral) {
        return "";
      } else {
        return `${data.cadastral.prefecture} ${data.cadastral.municipality} ${data.cadastral.sector} ${data.cadastral.subsector}`;
      }
    },

    async fetchRelatedForests() {
      this.loading = true;
      const response = await this.$rest.get(`/archives/${this.id}/forests`);
      if (response) {
        this.relatedForests = response.data;
        this.loading = false;
      }
    },

    async fetchAllForests(next) {
      if (this.next !== null) {
        this.fetchAllForestLoading = true;
        const response = await this.$rest.get(
          next !== "" ? next : "/forests/minimal",
        );
        if (response) {
          this.fetchAllForestLoading = false;
          const filteredForests = this.removeDuplicateForests(
            response.results,
            this.relatedForests,
          );
          const allForests = this.removeDuplicateForests(
            filteredForests,
            this.allForests,
          );
          this.allForests.push(...allForests);
          this.immutableAllForest.push(...allForests);
          this.next = response.next;
        }
      }
    },

    removeDuplicateForests(forests1, forests2) {
      return pullAllWith(forests1, forests2, (f1, f2) => f1.id === f2.id);
    },

    handleLoadMore() {
      if (!this.next || this.fetchAllForestLoading) return;
      this.fetchAllForests(this.next);
    },

    submitRelatedForest() {
      if (this.selectingForestId && this.selectingForestIndex) {
        const selectedForest = this.allForests[this.selectingForestIndex];
        selectedForest.added = true;
        this.relatedForests.push(selectedForest);
        this.allForests.splice(this.selectingForestIndex, 1);
        this.selectingForestId = null;
        this.selectingForestIndex = null;
      } else {
        this.allForests[0].added = true;
        this.relatedForests.push(this.allForests[0]);
        this.allForests.splice(0, 1);
      }
    },

    deleteForest(forest, index) {
      if (forest.added) {
        this.relatedForests.splice(index, 1);
        this.allForests = [forest, ...this.allForests];
      } else {
        this.$set(forest, "deleted", true);
      }
    },

    handleUndoDelete(forest) {
      this.$set(forest, "deleted", false);
    },

    async fetchSearchForest(keyword) {
      this.fetchAllForestLoading = true;
      const response = await this.$rest.get("/forests/minimal", {
        params: {
          search: keyword || "",
        },
      });
      if (response) {
        this.allForests = [];
        this.immutableAllForest = [];
        const tempSearchData = this.removeDuplicateForests(
          response.results,
          this.relatedForests,
        );
        this.next = response.next;
        this.allForests.push(...tempSearchData);
        this.immutableAllForest.push(...tempSearchData);
        this.fetchAllForestLoading = false;
      }
    },
  },

  computed: {
    addedForests() {
      return this.relatedForests.filter(forest => forest.added);
    },

    deletedForests() {
      return this.relatedForests.filter(forest => forest.deleted);
    },
  },

  watch: {
    shown(val) {
      if (!val) {
        if (this.allForests.length === 0)
          this.$refs.selectListModal.keyword = "";
      }
    },
    allForests: {
      deep: true,
      handler(allForests) {
        if (allForests.length <= 3 && this.next !== null) {
          this.handleLoadMore();
        }
      },
    },
  },
};
</script>
