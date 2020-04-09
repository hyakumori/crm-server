<template>
  <v-card class="search-card">
    <v-card-title class="search-card__title">{{
      $t("search.search_condition")
    }}</v-card-title>

    <v-form ref="form">
      <div
        class="search-card__search"
        v-for="(condition, index) in conditions"
        :key="index"
      >
        <div class="d-flex justify-space-between">
          <select-list
            class="search-card__search--spacing"
            :placeHolder="$t('search.select_item')"
            :actions="searchCriteria"
            :index="index"
            :rules="conditionRules"
            @selectedAction="onSelected"
          />

          <v-btn @click="deleteSearchField(index)" icon>
            <v-icon>mdi-delete-circle</v-icon>
          </v-btn>
        </div>

        <v-text-field
          v-model="condition.data"
          class="mt-1"
          clearable
          outlined
          :placeholder="$t('search.enter_condition')"
          :rules="dataRules"
        ></v-text-field>
      </div>

      <div
        class="d-flex flex-xl-row flex-lg-row flex-md-column search-card__btn"
      >
        <div @click="addSearchField">
          <v-icon>mdi-plus</v-icon>

          <span class="ml-1 caption">{{
            $t("search.add_search_condition")
          }}</span>
        </div>

        <v-btn class="mt-md-2 mt-lg-0 mt-xl-0" dark depressed @click="onSearch">
          {{ $t("raw_text.search") }}
          <v-icon dark>mdi-magnify</v-icon>
        </v-btn>
      </div>
    </v-form>
  </v-card>
</template>

<script>
import SelectList from "./SelectList";

export default {
  name: "search-card",

  components: {
    SelectList,
  },

  props: {
    searchCriteria: Array,
  },

  data() {
    return {
      dataRules: [val => !!val || this.$t("search.required_field")],
      conditionRules: [val => !!val || this.$t("search.required_field")],
      conditions: [
        {
          data: null,
          criteria: null,
        },
      ],
    };
  },

  methods: {
    addSearchField() {
      if (this.conditions.length == this.searchCriteria.length) {
        this.$emit("conditionOutOfBounds", true);
      } else {
        this.conditions.push({ data: null, criteria: null });
      }
    },

    onSelected(item, index) {
      this.conditions[index].criteria = item;
    },

    deleteSearchField(index) {
      if (this.conditions.length > 1) {
        this.conditions.splice(index, 1);
      } else {
        this.$emit("unableDelete", true);
      }
    },

    isUniqueArr(arr) {
      return arr.length === new Set(arr).size;
    },

    onSearch() {
      const criterias = Array.from(this.conditions).map(
        condition => condition.criteria,
      );
      const isDuplicateCriteria = true;
      if (this.$refs.form.validate()) {
        if (criterias && this.isUniqueArr(criterias)) {
          this.$emit("onSearch", !isDuplicateCriteria, this.conditions);
        } else {
          this.$emit("onSearch", isDuplicateCriteria);
        }
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$action-color: #12c7a6;
$text-color: #999999;
$text-field--min-height: 0;

.search-card {
  padding: 18px;
  height: 625px;
  overflow: auto;
  border-radius: 4px;

  &__title {
    font-size: 14px;
    font-weight: bold;
    color: #444444;
    padding: 0;
  }

  &__search {
    &--color {
      color: $text-color;
    }

    &--spacing ::v-deep {
      padding-top: 0;

      input::placeholder {
        color: $text-color;
      }

      .v-input__icon > i {
        color: $text-color !important;
      }
    }
  }

  &__btn {
    width: 100%;
    color: $action-color;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    margin-top: 0 !important;

    & .v-btn {
      background-color: #1b756a !important;

      i {
        color: white;
      }
    }

    & .v-icon {
      color: $action-color;
    }
  }
}

.v-input ::v-deep {
  & .v-text-field__details {
    margin-bottom: 0 !important;
    min-height: $text-field--min-height;

    & .v-messages {
      min-height: $text-field--min-height;
    }
  }
}
</style>
