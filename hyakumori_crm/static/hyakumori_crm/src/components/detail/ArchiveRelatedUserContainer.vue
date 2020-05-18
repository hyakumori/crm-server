<template>
  <div>
    <content-header
      :content="headerContent"
      :toggleEditBtnContent="toggleEditBtnContent"
      :update="isEditing"
      @toggleEdit="handleToggleEdit"
      class="mb-4"
    />
    <archive-participant-list
      :participants="tempUserParticipants"
      :isUpdate="isEditing"
      @deleteParticipant="handleDelete"
      @undoDeletedParticipant="handleUndoDelete"
    />
    <select-list-modal
      submitBtnIcon="mdi-plus"
      :loading="itemsForAddingLoading"
      :submitBtnText="$t('buttons.add')"
      :shown.sync="showSelect"
      :handleSubmitClick="submitRelatedParticipant"
      :disableAdditionBtn="itemsForAddingLoading"
      @search="debounceLoadInitItemsForAdding"
      @needToLoad="handleLoadMore"
      ref="selectListModal"
    >
      <template #list>
        <archive-participant-card
          v-for="(participant, index) in itemsForAdding.results"
          showPointer
          :key="index"
          :index="index"
          :name="participant.full_name"
          :showAction="false"
          :card_id="participant.id"
          :selectedId="modalSelectingId"
          @selected="
            (pId, pIndex) => {
              modalSelectingId = pId;
              modelSelectingIndex = pIndex;
            }
          "
          flat
        />
      </template>
    </select-list-modal>
    <template v-if="isEditing">
      <addition-button
        class="my-2"
        :content="addBtnContent"
        :click="() => (showSelect = true)"
      />
      <update-button
        :cancel="cancel"
        :saving="saving"
        :save="updateParticipant"
        :saveDisabled="saveDisabled"
      />
    </template>
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import SelectListModalMixin from "./SelectListModalMixin";
import ArchiveParticipantList from "./ArchiveParticipantList";
import AdditionButton from "../AdditionButton";
import UpdateButton from "./UpdateButton";
import SelectListModal from "../SelectListModal";
import ArchiveParticipantCard from "./ArchiveParticipantCard";
import { reject } from "lodash";

export default {
  name: "ArchiveRelatedUserContainer",

  mixins: [ContainerMixin, SelectListModalMixin],

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
      userParticipants: [],
      addedParticipants: [],
      deletedParticipants: [],
      itemsForAddingUrl: "/users/minimal",
      isLoading_: false,
    };
  },

  mounted() {
    this.fetchRelatedParticipants();
  },

  methods: {
    itemsForAddingResultFilter(p) {
      return this.userIdsMap[p.id];
    },
    handleToggleEdit(val) {
      this.isEditing = val;
    },

    async updateParticipant() {
      this.saving = true;
      await this.deleteParticipants();
      await this.addParticipants();
      this.saving = false;
      this.isEditing = false;
      this.fetchRelatedParticipants();
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
          this.modalSelectingId = null;
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
        }
      }
    },

    fetchRelatedParticipants() {
      this.isLoading_ = true;
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
          this.userParticipants = tempRelatedData;
          this.isLoading_ = false;
        });
    },

    submitRelatedParticipant() {
      const participant = this.itemsForAdding.results.splice(
        this.modalSelectingIndex,
        1,
      )[0];
      participant.added = true;
      this.addedParticipants.push(participant);
      this.modalSelectingIndex = null;
      this.modalSelectingId = null;
      if (this.itemsForAdding.results.length <= 3) {
        this.handleLoadMore();
      }
    },
    handleDelete(participant) {
      if (participant.added) {
        delete participant.added;
        this.addedParticipants = reject(this.addedParticipants, {
          id: participant.id,
        });
        this.itemsForAdding = { results: [] };
      } else {
        this.$set(participant, "deleted", true);
        this.deletedParticipants.push(participant);
      }
    },
    handleUndoDelete(participant) {
      this.$set(participant, "deleted", undefined);
      this.deletedParticipants = reject(this.deletedParticipants, {
        id: participant.id,
      });
    },
  },

  computed: {
    tempUserParticipants() {
      return [...this.userParticipants, ...this.addedParticipants];
    },
    userIdsMap() {
      return Object.fromEntries(
        this.tempUserParticipants.map(u => [u.id, true]),
      );
    },
    saveDisabled() {
      return (
        this.addedParticipants.length === 0 &&
        this.deletedParticipants.length === 0
      );
    },
  },

  watch: {
    isEditing(val) {
      if (!val) {
        if (this.addedParticipants.length > 0) {
          this.addedParticipants = [];
          this.itemsForAdding = { results: [] };
        }
        for (let p of this.deletedParticipants) {
          this.$set(p, "deleted", undefined);
        }
        if (this.deletedParticipants.length > 0) {
          this.deletedParticipants = [];
          this.itemsForAdding = { results: [] };
        }
      }
    },
  },
};
</script>

<style scoped></style>
