<template>
  <div>
    <v-card
      v-for="(discuss, index) in discussions"
      :key="index"
      class="history-discussion d-flex align-center"
      outlined
      @click="onClick"
    >
      <v-row>
        <v-col cols="1" class="pl-3">
          <v-icon small class="history-discussion__icon"
            >mdi-calendar-text</v-icon
          >
        </v-col>
        <v-col cols="2">
          <p class="ml-4 mr-6">{{ discuss.date }}</p>
        </v-col>
        <v-col cols="4" class="d-flex pr-4">
          <p class="history-discussion__attach">{{ discuss.attach_name }}</p>
          <v-icon small>mdi-paperclip</v-icon>
        </v-col>
        <v-col cols="2" class="pr-2">
          <p>{{ discuss.participant }}</p>
        </v-col>
        <v-col col="2" class="pr-2">
          <p class="history-discussion__host">{{ discuss.host }}</p>
        </v-col>
        <v-col cols="1">
          <v-btn icon @click="onClick">
            <v-icon>{{ toggleBtn }}</v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script>
export default {
  name: "history-discussion",

  props: {
    discussions: Array,
    isUpdate: Boolean,
    cancel: Function,
  },

  methods: {
    onClick() {
      // Do on click
    },
  },

  computed: {
    toggleBtn() {
      if (this.isUpdate) {
        return "mdi-close";
      } else {
        return "mdi-chevron-right";
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$border-radius: 4px;

.history-discussion::before {
  border-radius: $border-radius;
}

.history-discussion {
  width: 100%;
  padding: 8px;
  margin-bottom: 12px;
  border-radius: $border-radius;

  & .col {
    padding: 0;
    align-self: center;
    white-space: nowrap;
  }

  &__icon {
    width: 33px;
    height: 33px;
    padding: 8px;
    background-color: #f5f5f5;
    border-radius: 50% !important;
  }

  p {
    margin-bottom: 0 !important;
    font-size: 14px;
    color: #444444;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>
