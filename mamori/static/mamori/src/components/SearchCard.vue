<template>
  <v-card class="search-card">
    <h5>検索条件</h5>

    <div v-for="(condition, index) in conditions" :key="index">
      <div class="mb-2 mt-2 d-flex align-center">
        <h5 class="font-weight-regular mb-0" style="color: #999999">項目を選択</h5>

        <v-icon>mdi-chevron-down</v-icon>
      </div>

      <v-text-field v-model="condition.input" clearable placeholder="パスワード" outlined></v-text-field>
    </div>

    <div class="d-block" @click="addSearchField">
      <v-icon>mdi-plus</v-icon>

      <span class="ml-1 caption">検索条件を追加</span>
    </div>
  </v-card>
</template>

<script>
export default {
  name: "search-card",
  data() {
    return {
      conditions: [
        {
          input: null
        }
      ]
    }
  },

  methods: {
    addSearchField() {
      this.conditions.push({input: null})
    }
  }
};
</script>

<style lang="scss" scoped>
.search-card {
  padding: 18px;
  min-height: 628px;
  border-radius: 4px;
}

.v-input ::v-deep {
  & .v-text-field__details {
    margin-bottom: 0 !important;
    min-height: 0;

    & .v-messages {
      min-height: 0;
    }
  }
}

.d-block {
  color: #12c7a6 !important;
  cursor: pointer;
  width: fit-content;

  & .v-icon {
    color: #12c7a6 !important;
  }
}
</style>
