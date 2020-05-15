<template>
  <div>
    <content-header
      :content="headerContent"
      :editBtnContent="editBtnContent"
      :loading="fetchRelatedParticipantLoading"
      @toggleEdit="handleToggleEdit"
      class="mb-4"
    />
    <archive-participant-list
      :participants="relatedParticipants"
      :isUpdate="isUpdate"
      @deleteParticipant="handleDeleteParticipant"
      @undoDeletedParticipant="handleUndoDeletedParticipant"
    />
    <select-list-modal
      submitBtnIcon="mdi-plus"
      :loading="fetchAllParticipantLoading"
      :submitBtnText="$t('buttons.add')"
      :shown="shown"
      :handleSubmitClick="submitRelatedParticipant.bind(this)"
      :disableAdditionBtn="fetchAllParticipantLoading"
      @search="debounceSearchParticipant"
      @needToLoad="handleLoadMore"
      @update:shown="val => (shown = val)"
    >
      <template #list>
        <archive-participant-card
          v-for="(participant, index) in allParticipants"
          showPointer
          :key="index"
          :index="index"
          :name="participant.full_name"
          :showAction="false"
          :card_id="participant.id"
          :selectedId="selectingParticipantId"
          @selected="
            (pId, pIndex) => {
              selectingParticipantId = pId;
              selectingParticipantIndex = pIndex;
            }
          "
          flat
        />
      </template>
    </select-list-modal>
    <template v-if="isUpdate">
      <addition-button
        class="my-2"
        :content="addBtnContent"
        :click="addRelatedParticipant.bind(this)"
      />
      <update-button
        :cancel="cancel.bind(this)"
        :saving="updateParticipantLoading"
        :save="updateParticipant.bind(this)"
        :saveDisabled="
          addedParticipants.length === 0 && deletedParticipants.length === 0
        "
      />
    </template>
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import ArchiveParticipantList from "./ArchiveParticipantList";
import AdditionButton from "../AdditionButton";
import UpdateButton from "./UpdateButton";
import SelectListModal from "../SelectListModal";
import ArchiveParticipantCard from "./ArchiveParticipantCard";
import { cloneDeep, pullAllWith, debounce } from "lodash";

export default {
  name: "ArchiveRelatedUserContainer",

  mixins: [ContainerMixin],

  components: {
    ContentHeader,
    ArchiveParticipantList,
    UpdateButton,
    AdditionButton,
    SelectListModal,
    ArchiveParticipantCard,
  },

  data() {
    return {
      archive_id: this.$route.params.id,
      isUpdate: false,
      relatedParticipants: [],
      immutableRelatedParticipants: [],
      allParticipants: [],
      immutableAllParticipants: [],
      shown: false,
      next: "",
      fetchRelatedParticipantLoading: false,
      fetchAllParticipantLoading: false,
      selectingParticipantId: null,
      selectingParticipantIndex: null,
      updateParticipantLoading: false,
      searchNext: null,
    };
  },

  created() {
    this.debounceSearchParticipant = debounce(this.fetchSearchParticipant, 500);
  },

  mounted() {
    this.fetchRelatedParticipants();
  },

  methods: {
    handleToggleEdit(val) {
      if (!this.isUpdate && this.relatedParticipants) {
        this.immutableRelatedParticipants = cloneDeep(this.relatedParticipants);
      }
      this.isUpdate = val;
    },

    cancel() {
      this.isUpdate = false;
      this.relatedParticipants = cloneDeep(this.immutableRelatedParticipants);
      this.allParticipants = cloneDeep(this.immutableAllParticipants);
    },

    async updateParticipant() {
      if (this.relatedParticipants.length === 0) {
        this.isUpdate = false;
      } else {
        this.updateParticipantLoading = true;
        await this.deleteParticipants();
        await this.addParticipants();
        this.updateParticipantLoading = false;
        this.isUpdate = false;
      }
    },

    async deleteParticipants() {
      if (this.deletedParticipants.length > 0) {
        const deletedIds = this.deletedParticipants.map(p => p.id);
        const isDeleted = await this.$rest.delete(
          `/archives/${this.archive_id}/users`,
          {
            data: {
              ids: deletedIds,
            },
          },
        );
        if (isDeleted) {
          this.selectingParticipantId = null;
          this.relatedParticipants = this.removeDuplicateParticipant(
            this.relatedParticipants,
            this.deletedParticipants,
          );
          const pureParticipants = cloneDeep(this.deletedParticipants);
          pureParticipants.forEach(p => (p.deleted = false));
          this.allParticipants.push(...pureParticipants);
          this.immutableAllParticipants = cloneDeep(this.allParticipants);
        }
      }
    },

    async addParticipants() {
      if (this.addedParticipants.length > 0) {
        const addedIds = this.addedParticipants.map(p => p.id);
        const newParticipants = await this.$rest.post(
          `/archives/${this.archive_id}/users`,
          { ids: addedIds },
        );
        if (newParticipants) {
          const tempParticipants = this.removeDuplicateParticipant(
            this.relatedParticipants,
            newParticipants.data,
          );
          this.allParticipants = this.removeDuplicateParticipant(
            this.allParticipants,
            this.addedParticipants,
          );
          this.immutableAllParticipants = cloneDeep(this.allParticipants);
          tempParticipants.push(...newParticipants.data);
          this.relatedParticipants = tempParticipants;
        }
      }
    },

    fetchRelatedParticipants() {
      this.fetchRelatedParticipantLoading = true;
      this.$rest
        .get(`/archives/${this.archive_id}/users`)
        .then(async response => {
          let tempRelatedData = response.results;
          let next = response.next;
          while (!!next) {
            const paginationResponse = await this.$rest.get(next);
            if (paginationResponse) {
              tempRelatedData.push(...paginationResponse.results);
              next = paginationResponse.next;
            }
          }
          this.relatedParticipants = tempRelatedData;
          this.fetchRelatedParticipantLoading = false;
        });
    },

    fetchAllParticipants() {
      if (this.next !== null) {
        this.fetchAllParticipantLoading = true;
        this.$rest
          .get(this.next !== "" ? this.next : "/users/minimal")
          .then(res => {
            this.fetchAllParticipantLoading = false;
            const filteredParticipants = this.removeDuplicateParticipant(
              res.results,
              this.relatedParticipants,
            );
            const allParticipants = this.removeDuplicateParticipant(
              filteredParticipants,
              this.allParticipants,
            );
            this.allParticipants.push(...allParticipants);
            this.immutableAllParticipants.push(...allParticipants);
            this.next = res.next;
          });
      }
    },

    removeDuplicateParticipant(participant1, participant2) {
      return pullAllWith(
        participant1,
        participant2,
        (p1, p2) => p1.id === p2.id,
      );
    },

    addRelatedParticipant() {
      this.shown = true;
      if (this.allParticipants.length === 0 || this.next === "") {
        this.fetchAllParticipants();
      }
    },

    handleLoadMore() {
      if (this.next !== null) {
        this.fetchAllParticipants(this.next);
      }
    },

    submitRelatedParticipant() {
      if (this.selectingParticipantId && this.selectingParticipantIndex) {
        const selectedParticipant = this.allParticipants[
          this.selectingParticipantIndex
        ];
        selectedParticipant.added = true;
        this.relatedParticipants.push(selectedParticipant);
        this.allParticipants.splice(this.selectingParticipantIndex, 1);
        this.selectingParticipantId = null;
        this.selectingParticipantIndex = null;
      } else {
        this.allParticipants[0].added = true;
        this.relatedParticipants.push(this.allParticipants[0]);
        this.allParticipants.splice(0, 1);
      }
    },

    handleDeleteParticipant(participant, index) {
      if (participant.added) {
        this.relatedParticipants.splice(index, 1);
        this.allParticipants = [participant, ...this.allParticipants];
      } else {
        this.$set(participant, "deleted", true);
      }
    },

    handleUndoDeletedParticipant(participant) {
      this.$set(participant, "deleted", false);
    },

    fetchSearchParticipant(keyword) {
      this.fetchAllParticipantLoading = true;
      this.$rest
        .get("/users/minimal", {
          params: {
            search: keyword || "",
          },
        })
        .then(response => {
          this.allParticipants = [];
          this.immutableAllParticipants = [];
          const tempParticipants = this.removeDuplicateParticipant(
            response.results,
            this.relatedParticipants,
          );
          this.next = response.next;
          this.allParticipants.push(...tempParticipants);
          this.immutableAllParticipants.push(...tempParticipants);
          this.fetchAllParticipantLoading = false;
        });
    },
  },

  computed: {
    addedParticipants() {
      return (
        this.relatedParticipants &&
        this.relatedParticipants.filter(participant => participant.added)
      );
    },

    deletedParticipants() {
      return (
        this.relatedParticipants &&
        this.relatedParticipants.filter(participant => participant.deleted)
      );
    },
  },

  watch: {
    allParticipants: {
      deep: true,
      handler(allParticipants) {
        if (allParticipants.length <= 3 && this.next !== null) {
          this.handleLoadMore();
        }
      },
    },
  },
};
</script>

<style scoped></style>
