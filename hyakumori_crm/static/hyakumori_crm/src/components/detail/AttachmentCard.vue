<template>
  <div>
    <v-card
      v-for="(attach, index) in attaches"
      :key="index"
      class="history-discussion d-flex align-center d-hover"
      outlined
      :ripple="ripple"
    >
      <v-row>
        <v-col cols="1" class="pl-3">
          <v-icon small class="history-discussion__icon"
            >mdi-calendar-text</v-icon
          >
        </v-col>
        <v-col cols="2">
          <p class="ml-3 mr-6">{{ getArchiveDate(attach.archive_date) }}</p>
        </v-col>
        <v-col cols="4" class="d-flex pr-4 text-truncate">
          <p class="history-discussion__attach text-truncate">
            {{ attach.title }}
          </p>
          <v-icon v-if="attach.attachments.length" small>mdi-paperclip</v-icon>
        </v-col>
        <v-col cols="2" class="pr-2 text-truncate">
          <p>{{ renderArchiveForests(attach) }}</p>
        </v-col>
        <v-col col="2" class="pr-2 text-truncate">
          <p class="history-discussion__host">
            {{ renderArchiveParticipants(attach) }}
          </p>
        </v-col>
        <v-col cols="1">
          <router-link
            :to="{ name: 'archive-detail', params: { id: attach.id } }"
            v-slot="{ href }"
          >
            <v-btn icon :href="href">
              <v-icon>{{ toggleBtn }}</v-icon>
            </v-btn>
          </router-link>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script>
import { getDate } from "../../helpers/datetime";
import { get as _get } from "lodash";

export default {
  name: "attachment-card",

  props: {
    attaches: Array,
    isUpdate: Boolean,
    cancel: Function,
    ripple: {
      type: Boolean,
      default: true,
    },
  },

  methods: {
    getArchiveDate(date) {
      return getDate(date) || "";
    },
    renderArchiveForests(data) {
      const list = _get(data, "attributes.forest_cache.list", []);
      if (list.length > 0) {
        let results = _get(list[0], "forest__internal_id", "");
        if (list.length > 1) {
          results +=
            " " +
            this.$t("tables.another_item_thing", { count: list.length - 1 });
        }
        return results;
      }
      return this.$t("archive.no_associated_forest");
    },
    renderArchiveParticipants(data) {
      const list = _get(data, "attributes.customer_cache.list", []);
      if (list.length > 0) {
        let results = _get(list[0], "customer__name_kanji.last_name", "");
        results += " " + _get(list[0], "customer__name_kanji.first_name", "");
        if (list.length > 1) {
          results +=
            " " +
            this.$t("tables.another_item_human_kanji", {
              count: list.length - 1,
            });
        }
        return results;
      }
      return "";
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
