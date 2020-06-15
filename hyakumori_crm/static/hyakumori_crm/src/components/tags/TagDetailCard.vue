<template>
  <div class="ml-6 mb-6">
    <h4 class="mb-1">タグ情報</h4>
    <v-progress-linear
      height="2"
      indeterminate
      rounded
      v-if="isLoading"
    ></v-progress-linear>

    <v-card
      class="tag-card pa-0"
      flat
      @click.native="hasPermission && (isUpdate = true)"
      :ripple="false"
      :class="{ 'd-hover pointer': !isUpdate && hasPermission }"
    >
      <v-container class="pa-0">
        <v-row class="pa-0 tag-list" no-gutters>
          <v-col class="pa-2 d-flex align-center flex-wrap">
            <template v-if="availableEditingTags.length">
              <div v-for="(item, index) in availableEditingTags" :key="index">
                <v-chip
                  color="primary"
                  @click:close="() => deleteTag(item)"
                  :ripple="false"
                  class="ma-1"
                  draggable
                  pill
                  :close="isUpdate"
                  :title="`${item.key}: ${item.value}`"
                >
                  {{
                    item.key.length > 15
                      ? item.key.slice(0, 15) + "..."
                      : item.key
                  }}:
                  {{
                    item.value.length > 15
                      ? item.value.slice(0, 15) + "..."
                      : item.value
                  }}
                </v-chip>
              </div>
            </template>
            <template v-else>
              <p class="ma-0 grey--text justify-center">
                {{
                  hasPermission && !isUpdate
                    ? $t("tags.no_tags")
                    : (!isUpdate && $t("tags.no_tags_view_only")) || ""
                }}
              </p>
            </template>
          </v-col>
        </v-row>

        <template v-if="isUpdate && hasPermission">
          <v-divider></v-divider>

          <v-row no-gutters>
            <v-col class="pa-4">
              <div class="memo-input__value">
                <v-row no-gutters>
                  <v-col cols="5" class="pr-1">
                    <v-combobox
                      dense
                      height="45"
                      outlined
                      autofocus
                      validate-on-blur
                      v-model="selectedTagKey"
                      hide-details
                      :items="tagKeyItems"
                      :filter="tagFilter"
                    ></v-combobox>
                  </v-col>
                  <v-col cols="6">
                    <v-combobox
                      v-model="selectedTagValue"
                      :items="tagValueItems"
                      :loading="isLoading"
                      :filter="tagFilter"
                      :search-input.sync="tagValueSearchInput"
                      :disabled="!selectedTagKey"
                      height="45"
                      hide-details
                      hide-no-data
                      auto-select-first
                      clearable
                      dense
                      outlined
                    ></v-combobox>
                  </v-col>
                  <v-col cols="1" class="mt-1 pl-1">
                    <v-btn
                      icon
                      color="primary"
                      @click.stop="addTag"
                      :disabled="
                        !trimmedSelectedTagKey || !trimmedTagValueSearchInput
                      "
                    >
                      <v-icon>mdi-plus</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </div>
            </v-col>
          </v-row>

          <v-divider></v-divider>

          <v-row no-gutters>
            <v-col cols="12" class="px-4 py-2">
              <update-button
                :saveDisabled="!hasChanged"
                :cancel="onCancel"
                :save="onSave"
                :saving="isLoading"
              />
              <div v-acl-only="['admin', 'group_admin']">
                <tag-setting-manage
                  :app-name="appName"
                  :object-type="objectType"
                  :show-dialog.sync="tagSettingDialog"
                ></tag-setting-manage>
                <v-btn
                  icon
                  color="primary"
                  @click.stop="tagSettingDialog = true"
                  class="edit-tag-btn"
                >
                  <v-icon>mdi-cog</v-icon>
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </template>
      </v-container>
    </v-card>
  </div>
</template>

<script>
import UpdateButton from "../detail/UpdateButton";
import TagSettingManage from "./TagSettingManage";
import { hasScope } from "../../helpers/security";

export default {
  props: {
    tags: { type: Object },
    appName: { type: String, required: true },
    objectType: { type: String, required: true },
    objectId: { type: String },
  },
  components: {
    UpdateButton,
    TagSettingManage,
  },
  data() {
    return {
      settings: {},
      isLoading: false,
      isUpdate: false,
      tagValues: [],
      selectedTagKey: "",
      selectedTagValue: "",
      tagValueSearchInput: "",
      editingTags: [],
      originalTags: { ...this.tags },
      tagSettingDialog: false,
    };
  },
  async mounted() {
    this.isLoading = true;
    await Promise.all([this.getTagSettings(), this.getTagValues()]);
    this.isLoading = false;
  },
  methods: {
    deleteTag(tag) {
      this.editingTags = this.editingTags.map(item => {
        if (item.key === tag.key) {
          item.deleted = true;
        }
        return item;
      });
    },
    onCancel() {
      this.isUpdate = false;
      this.selectedTagKey = "";
      this.selectedTagValue = "";
      this.editingTags = this.mapTagsToEditingValues(this.originalTags);
    },
    async onSave() {
      try {
        this.isLoading = true;
        const results = await this.$rest.post(
          `/tags/${this.appName}/${this.objectType}/assign`,
          {
            object_id: this.objectId,
            tags: this.editingTags
              .filter(item => item.value && !item.deleted)
              .map(item => ({
                tag_name: item.key,
                value: item.value,
              })),
          },
        );
        if (results) {
          this.$emit("input", results.tags);
          this.originalTags = results.tags;
          await this.getTagValues();
          await this.getTagSettings();
        }
      } catch (e) {
      } finally {
        this.isLoading = false;
        this.isUpdate = false;
      }
    },
    async getTagSettings() {
      const tagSettings = await this.$rest.get(
        `/tags/settings/${this.appName}/${this.objectType}`,
      );
      if (tagSettings && tagSettings.results) {
        this.settings = tagSettings.results;
      }
    },
    async getTagValues() {
      const tags = await this.$rest.get(
        `/tags/${this.appName}/${this.objectType}`,
      );
      if (tags && tags.results) {
        this.tagValues = tags.results;
      }
    },
    tagFilter(item, queryText) {
      return item.includes(queryText);
    },
    async addTag() {
      if (
        !this.trimmedTagValueSearchInput ||
        this.trimmedTagValueSearchInput.length === 0
      ) {
        return;
      }
      let hasItem = false;
      for (let item of this.editingTags) {
        if (this.selectedTagKey === item.key) {
          item.value = this.trimmedTagValueSearchInput;
          item.deleted = false;
          item.edited = true;
          hasItem = true;
          break;
        }
      }
      if (!hasItem) {
        this.editingTags.push({
          key: this.selectedTagKey,
          value: this.trimmedTagValueSearchInput,
          added: true,
          deleted: false,
        });
      }
      this.tagValueSearchInput = "";
      this.selectedTagKey = "";
    },
    mapTagsToEditingValues(tags) {
      let results = [];
      for (let tagKey of Object.keys(tags).sort()) {
        if (tags[tagKey] !== null) {
          results.push({
            key: tagKey,
            value: tags[tagKey],
            added: false,
            edited: false,
            deleted: false,
          });
        }
      }
      return results;
    },
  },
  computed: {
    availableEditingTags() {
      return this.editingTags.filter(i => i.value && !i.deleted);
    },
    hasPermission() {
      const managePermission = `manage_${this.objectType}`;
      return hasScope(managePermission);
    },
    hasChanged() {
      return (
        this.editingTags.filter(
          item =>
            item.added === true ||
            item.edited === true ||
            item.deleted === true,
        ).length > 0
      );
    },
    tagKeyItems() {
      const selectedTagKeys = this.editingTags
        .filter(item => item.key && item.value && !item.deleted)
        .map(item => item.key);
      return this.settings
        .filter(item => !selectedTagKeys.includes(item.name))
        .map(item => item.name);
    },
    tagValueItems() {
      const tags = this.tagValues[this.selectedTagKey];
      return tags && tags.length > 0 && tags.filter(item => !!item);
    },
    trimmedTagValueSearchInput() {
      return this.tagValueSearchInput && this.tagValueSearchInput.trim();
    },
    trimmedSelectedTagKey() {
      return this.selectedTagKey && this.selectedTagKey.trim();
    },
  },
  watch: {
    tags: {
      deep: true,
      handler(val) {
        this.originalTags = { ...val };
        this.editingTags = this.mapTagsToEditingValues(this.originalTags);
      },
    },
    selectedTagKey() {
      this.selectedTagValue = "";
    },
    async tagSettingDialog(val) {
      if (!val) {
        await this.getTagSettings();
        await this.getTagValues();
      }
    },
  },
};
</script>
<style lang="scss">
.pointer {
  cursor: pointer;
}
.tag-card {
  margin-top: 12px;
  min-height: 60px;
  box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);
  align-items: center;
  border-radius: 4px;
  padding: 8px;
  display: flex;
  width: 399px;
  .tag-list {
    min-height: 44px;
  }
  .edit-tag-btn {
    position: absolute;
    right: 10px;
    bottom: 10px;
  }
}
</style>
