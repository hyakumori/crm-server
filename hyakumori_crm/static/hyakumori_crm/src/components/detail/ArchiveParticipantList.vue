<template>
  <v-row dense>
    <template v-for="(participant, index) in participants">
      <v-col cols="6" :key="index">
        <archive-participant-card
          :name="participant.full_name"
          :isUpdate="isUpdate"
          :added="participant.added"
          :deleted="participant.deleted"
          :card_id="participant.id"
          @deleteParticipant="$emit('deleteParticipant', participant, index)"
          @undoDeletedParticipant="$emit('undoDeletedParticipant', participant)"
        />
      </v-col>
    </template>
  </v-row>
</template>

<script>
import ArchiveParticipantCard from "./ArchiveParticipantCard";

export default {
  name: "archive-participant-list",

  components: {
    ArchiveParticipantCard,
  },

  props: {
    participants: Array,
    isUpdate: Boolean,
  },
};
</script>
