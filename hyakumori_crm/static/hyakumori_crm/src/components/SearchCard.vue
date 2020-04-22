<template>
  <v-card class="search-card">
    <v-card-title class="search-card__title d-flex justify-space-between">
      {{ $t("search.search_condition") }}
      <v-btn dense small text @click="resetSearch">
        {{ $t("buttons.reset") }}
      </v-btn>
    </v-card-title>

    <v-form ref="form">
      <div
        class="search-card__search"
        v-for="(condition, index) in conditions"
        :key="`${index}:${condition.criteria}`"
      >
        <div class="d-flex justify-space-between">
          <select-list
            class="search-card__search--spacing"
            :placeHolder="$t('search.select_item')"
            :actions="condition.fields"
            :index="index"
            :value="condition.criteria"
            @selectedAction="onSelected"
          />

          <v-btn
            v-if="conditions.length > 1"
            @click="deleteSearchField(index)"
            icon
          >
            <v-icon class="grey--text lighten-5">mdi-backspace</v-icon>
          </v-btn>
        </div>

        <v-text-field
          v-model="condition.keyword"
          class="mt-1"
          height="45"
          clearable
          outlined
          dense
          :placeholder="$t('search.enter_condition')"
        ></v-text-field>
      </div>

      <div
        class="d-flex flex-xl-row flex-lg-row flex-md-column search-card__btn"
      >
        <div class="d-flex align-center" @click="addSearchField">
          <v-icon>mdi-plus</v-icon>

          <span class="ml-1 caption">{{
            $t("search.add_search_condition")
          }}</span>
        </div>

        <v-btn
          class="mt-md-2 mt-lg-0 mt-xl-0"
          color="primary"
          depressed
          @click="onSearch"
          :disabled="!searchable"
        >
          {{ $t("raw_text.search") }}
          <v-icon>mdi-magnify</v-icon>
        </v-btn>
      </div>
    </v-form>
  </v-card>
</template>

<script>
import { uniq, map } from "lodash";
import SelectList from "./SelectList";

export default {
  name: "search-card",

  components: {
    SelectList,
  },

  props: {
    searchCriteria: Array,
    onSearch: Function,
  },

  data() {
    return {
      usedFields: new Set(),
      conditions: [
        {
          fields: [...this.searchCriteria],
          criteria: null,
          keyword: null,
        },
      ],
    };
  },
  computed: {
    searchable() {
      const criteria = uniq(map(this.conditions, "criteria"));
      const keywords = uniq(map(this.conditions, "keyword"));
      if (
        (criteria.length === 1 && criteria[0] === null) ||
        (keywords.length === 1 && keywords[0] === null)
      )
        return false;
      return true;
    },
  },
  watch: {
    searchCriteria(val) {
      this.conditions[0].fields = [...val];
    },
    usedFields(val) {
      for (let con of this.conditions) {
        this.$set(
          con,
          "fields",
          this.searchCriteria.filter(
            f => !val.has(f.value) || f.value === con.criteria,
          ),
        );
      }
    },
  },
  methods: {
    resetSearch() {
      this.conditions = [
        {
          fields: [...this.searchCriteria],
          criteria: null,
          keyword: null,
        },
      ];

      if (this.onSearch) {
        this.onSearch();
      }

      this.$emit("resetSearch");
    },

    addSearchField() {
      if (this.conditions.length == this.searchCriteria.length) {
        this.$emit("conditionOutOfBounds", true);
      } else {
        this.conditions.push({
          keyword: null,
          criteria: null,
          fields: this.searchCriteria.filter(
            f => !this.usedFields.has(f.value),
          ),
        });
      }
    },

    onSelected(item, index) {
      const oldField = this.conditions[index].criteria;
      this.usedFields.has(oldField) && this.usedFields.delete(oldField);
      this.conditions[index].criteria = item;
      this.usedFields.add(item);
      this.usedFields = new Set(this.usedFields);
    },

    deleteSearchField(index) {
      if (this.conditions.length > 1) {
        const oldField = this.conditions[index].criteria;
        this.conditions.splice(index, 1);
        if (this.usedFields.has(oldField)) {
          this.usedFields.delete(oldField);
          this.usedFields = new Set(this.usedFields);
        }
      } else {
        this.$emit("unableDelete", true);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$action-color: #12c7a6;
$text-color: #999999;
$text-field--min-height: 0;
$text-font-size: 14px;

.search-card {
  padding: 18px;
  min-height: 625px;
  overflow: auto;
  min-width: 295px;
  max-width: 295px;
  box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);

  &__title {
    font-size: $text-font-size;
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
    margin-top: 5px !important;

    & i {
      color: $action-color;
    }
  }
}

.v-input ::v-deep {
  input {
    color: $text-color;
    font-size: $text-font-size;
  }

  fieldset {
    border: 1px solid #e1e1e1;
  }

  & .v-text-field__details {
    margin-bottom: 0 !important;
    min-height: $text-field--min-height;

    & .v-messages {
      min-height: $text-field--min-height;
    }
  }
}
</style>
