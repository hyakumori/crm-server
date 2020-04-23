<template>
  <v-row dense>
    <template v-for="(parti, index) in participants">
      <v-col cols="6" :key="index">
        <archive-participant-card :name="parti" />
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
