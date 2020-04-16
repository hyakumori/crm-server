<template>
  <v-card class="log-card" flat @click="onClickCard">
    <div class="d-flex pa-4">
      <v-icon class="align-self-start">mdi-calendar-text</v-icon>

      <div class="log-card__info">
        <h5>{{ action }}</h5>

        <p>{{ info }}</p>
      </div>
    </div>

    <div class="align-self-center pr-4">
      <v-btn icon @click="onClick">
        <v-icon>mdi-chevron-right</v-icon>
      </v-btn>
    </div>
  </v-card>
</template>

<script>
export default {
  name: "log-card",

  props: {
    action: String,
    date: String,
    editor: String,
    type: String,
  },

  methods: {
    onClick() {
      // Handle click navigate
    },

    onClickCard() {
      // Handle click card
    },
  },

  computed: {
    info() {
      if (this.date) {
        if (this.editor) {
          return `${this.date}・${this.editor}`;
        } else {
          return this.date;
        }
      } else {
        return "";
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.log-card {
  display: flex;
  justify-content: space-between;
  width: 399px;
  height: 72px;
  margin-top: 12px;
  box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);
  border-radius: 4px;

  &__info {
    margin-left: 20px;

    h5 {
      color: #444444;
      font-size: 14px;
      font-weight: normal;
    }

    p {
      color: #999999;
      font-size: 12px;
    }
  }
}
</style>
