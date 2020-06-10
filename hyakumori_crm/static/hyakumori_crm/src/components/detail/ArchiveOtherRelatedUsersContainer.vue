<template>
  <div>
    <content-header
      :loading="loading || isLoading"
      :content="headerContent"
      :toggleEditBtnContent="toggleEditBtnContent"
      :update="isEditing"
      @toggleEdit="handleToggleEdit"
      class="mb-4"
      :displayAdditionBtn="allowEdit"
    />
    <ul v-if="!isEditing">
      <li v-for="name in tempParticipants" :key="name">{{ name }}</li>
    </ul>
    <text-input
      ref="input"
      v-else
      v-model="participantsText"
      placeholder="カンマで複数の参加者入力可能（例：山田太郎,山田次郎）"
    ></text-input>
    <template v-if="isEditing">
      <update-button
        class="my-2"
        :cancel="cancel"
        :saving="saving"
        :save="handleSave"
        :saveDisabled="saveDisabled"
      />
    </template>
  </div>
</template>

<script>
import ContentHeader from "./ContentHeader";
import ContainerMixin from "./ContainerMixin";
import ArchiveDetailMixin from "./ArchiveDetailMixin";
import UpdateButton from "./UpdateButton";
import TextInput from "../forms/TextInput";

export default {
  mixins: [ContainerMixin, ArchiveDetailMixin],

  components: {
    ContentHeader,
    UpdateButton,
    TextInput,
  },
  props: {
    archive: { type: Object },
  },
  data() {
    return {
      loading: false,
      archive_id: this.$route.params.id,
      tempParticipants: [],
      participants: [],
    };
  },

  methods: {
    itemsForAddingResultFilter(p) {
      return this.userIdsMap[p.id];
    },
    handleToggleEdit(val) {
      this.isEditing = val;
    },
    async handleSave() {
      this.loading = true;
      try {
        await this.$rest.put(`archives/${this.archive_id}/other-participants`, {
          other_participants: this.tempParticipants,
        });
        this.participants = this.tempParticipants;
        this.isEditing = false;
      } catch (error) {}
      this.loading = false;
    },
  },

  computed: {
    participantsText: {
      get() {
        return this.tempParticipants.join(",");
      },
      set(val) {
        const val_ = val.endsWith(",") ? val.splice(0, val.length - 1) : val;
        if (val_ === "") this.tempParticipants = [];
        else this.tempParticipants = val_.split(",");
      },
    },
    saveDisabled() {
      return this.participantsText === this.participants.join(",");
    },
  },

  watch: {
    isEditing(val) {
      if (!val) {
        this.tempParticipants = this.participants;
      }
    },
    archive(val) {
      this.participants = val
        ? this.archive.attributes.other_participants || []
        : [];
      this.tempParticipants = [...this.participants];
    },
  },
};
</script>

<style scoped></style>
