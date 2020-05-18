<template>
  <v-dialog
    no-click-animation
    :value="showDialog"
    @input="$emit('update:showDialog', $event)"
    width="600"
  >
    <v-card class="dialog-content" :loading="loading">
      <v-card-title class="title px-4 py-2">
        タグ設定
        <v-spacer></v-spacer>
        <v-btn text @click.stop="switchToAddNew" depressed color="primary">
          <v-icon left>mdi-tag-plus-outline</v-icon> 新しいタグを追加
        </v-btn>
        <v-btn icon @click.stop="onClose" depressed color="grey">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider></v-divider>

      <v-card-text class="pa-0">
        <v-content>
          <v-container class="pa-0">
            <v-row no-gutters>
              <v-col cols="4" class="item-list">
                <v-list subheader class="pa-0">
                  <v-list-item-group v-model="selectedTagId">
                    <v-list-item
                      v-for="item in tagSettings"
                      :key="item.id"
                      :value="item.id"
                      @click="() => viewDetail(item)"
                    >
                      <v-list-item-content>
                        <v-list-item-title
                          v-text="item.name"
                        ></v-list-item-title>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list-item-group>
                </v-list>
              </v-col>
              <v-col cols="8" class="item-detail" v-if="selectedTag">
                <div class="pa-4">
                  <div>
                    <v-alert
                      dense
                      outlined
                      dismissible
                      type="error"
                      v-model="hasError"
                      :icon="false"
                      >{{ errors }}
                    </v-alert>
                  </div>
                  <v-text-field
                    v-model="selectedTag.name"
                    label="名称"
                    hide-details
                    dense
                    outlined
                  ></v-text-field>
                  <v-text-field
                    class="mt-4"
                    v-model="selectedTag.code"
                    label="コード名"
                    hide-details
                    dense
                    outlined
                  ></v-text-field>
                </div>

                <v-divider></v-divider>

                <!--color maps-->
                <div class="color-maps pa-4">
                  <div
                    v-for="(item, index) in colorMaps"
                    :key="index"
                    class="mt-2"
                  >
                    <tag-setting-color-item
                      :item="item"
                      :id="index"
                      :get-item-style="getItemStyle"
                      :update-tag-item-color="updateTagItemColor"
                      :show-delete="true"
                      @setting-deleted="onColorSettingDelete"
                    ></tag-setting-color-item>
                  </div>
                  <div class="mt-2">
                    <tag-setting-color-item
                      :item="addingColorItem"
                      :get-item-style="getItemStyle"
                      :update-tag-item-color="updateTagItemColor"
                    ></tag-setting-color-item>
                    <v-btn
                      class="mt-2"
                      text
                      @click.stop="addNewColorSetting"
                      depressed
                      color="primary"
                    >
                      <v-icon left>mdi-plus</v-icon>
                      追加
                    </v-btn>
                  </div>
                </div>

                <template>
                  <v-divider></v-divider>
                  <v-row no-gutters>
                    <v-col class="text-left pa-4" v-if="isEditing">
                      <v-btn color="danger" depressed @click.stop="onDelete">
                        <v-icon left>mdi-delete</v-icon> 削除
                      </v-btn>
                    </v-col>

                    <v-col class="text-right pa-4">
                      <v-btn
                        color="primary"
                        depressed
                        :disabled="!hasChanged && !canSave"
                        @click.stop="onSave"
                        v-if="!isEditing"
                      >
                        <v-icon left>mdi-content-save</v-icon> 保存
                      </v-btn>
                      <v-btn
                        color="primary"
                        :disabled="!hasChanged"
                        depressed
                        @click.stop="onUpdate"
                        v-else
                      >
                        <v-icon left>mdi-content-save-edit-outline</v-icon> 更新
                      </v-btn>
                    </v-col>
                  </v-row>
                </template>
              </v-col>
            </v-row>
          </v-container>
        </v-content>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import TagSettingColorItem from "./TagSettingColorItem";
import { debounce, isEqual, get as _get } from "lodash";

export default {
  props: {
    appName: { type: String, required: true },
    objectType: { type: String, required: true },
    showDialog: { type: Boolean, default: false },
  },
  components: { TagSettingColorItem },
  data() {
    return {
      errors: "",
      loading: false,
      selectedTagId: "",
      hasError: false,
      tagSettings: [],
      tagValues: [],
      colorMaps: [],
      selectedTag: {
        ...this.buildTagSetting(),
      },
      originalSelectedTag: {
        ...this.buildTagSetting(),
      },
      selectedTagMigrateInfo: null,
      addingColorItem: {
        value: "",
        color: "#FF0000",
      },
    };
  },
  created() {
    this.debouncedGetMigrateInfo = debounce(
      async () => await this.getTagMigrateInfo(),
      300,
    );
  },
  methods: {
    updateTagItemColor(colorVal, item) {
      const colors = this.selectedTag.attributes.colors || [];
      const itemIndex = colors.findIndex(
        setting => setting.value === item.value,
      );
      if (itemIndex > -1) {
        colors[itemIndex].color = colorVal.hex;
      } else {
        this.addingColorItem.color = colorVal.hex;
      }
    },
    getItemStyle(item) {
      const { color, menu } = item;
      return {
        backgroundColor: color,
        cursor: "pointer",
        height: "20px",
        width: "20px",
        marginTop: "3px",
        borderRadius: menu ? "50%" : "4px",
        transition: "border-radius 200ms ease-in-out",
      };
    },
    async getTagValues() {
      const tags = await this.$rest.get(
        `/tags/${this.appName}/${this.objectType}`,
      );
      if (tags && tags.results) {
        this.tagValues = tags.results;
      }
    },
    async getTagSettings() {
      const response = await this.$rest.get(
        `/tags/settings/${this.appName}/${this.objectType}`,
      );
      if (response && response.results) {
        this.tagSettings = response.results.map(item => ({
          ...item,
          original_name: item.name,
        }));
      }
    },
    viewDetail(item) {
      this.selectedTag = item;
    },
    buildTagSetting() {
      return {
        attributes: {
          colors: [],
        },
        code: "",
        name: "",
      };
    },
    switchToAddNew() {
      this.selectedTag = { ...this.buildTagSetting() };
      this.originalSelectedTag = { ...this.selectedTag };
    },
    onClose() {
      this.$emit("update:showDialog", false);
    },
    async onUpdate() {
      if (
        !this.selectedTag.name ||
        !this.selectedTag.code ||
        this.selectedTag.code.length === 0 ||
        this.selectedTag.name.length === 0
      ) {
        this.errors = this.$t("tags.required_fields");
        return;
      }
      if (
        this.selectedTagMigrateInfo > 0 &&
        this.selectedTag.name !== this.selectedTag.original_name
      ) {
        const confirm = await this.$dialog.confirm({
          title: this.$t("tags.migrate_title"),
          text: this.$t("tags.confirm_migrate", {
            total: this.selectedTagMigrateInfo,
          }),
        });
        if (!confirm) {
          return;
        }
      }

      try {
        this.loading = true;
        const response = await this.$rest.put(
          `/tags/${this.appName}/${this.objectType}/modify`,
          {
            id: this.selectedTag.id,
            name: this.selectedTag.name,
            code: this.selectedTag.code,
            color_maps: this.colorMaps,
          },
          {
            no_activity: true,
          },
        );
        if (response) {
          await this.getTagSettings();
          this.selectedTag = {
            ...response.results,
            original_name: response.results.name,
          };
          this.onSelectedTagIdChanged();
        }
      } catch (e) {
      } finally {
        this.loading = false;
      }
    },
    async onSave() {
      if (
        !this.selectedTag.name ||
        !this.selectedTag.code ||
        this.selectedTag.code.length === 0 ||
        this.selectedTag.name.length === 0
      ) {
        this.errors = this.$t("tags.required_fields");
        return;
      }
      try {
        this.loading = true;
        const response = await this.$rest.post(
          `/tags/${this.appName}/${this.objectType}/modify`,
          {
            name: this.selectedTag.name,
            code: this.selectedTag.code,
            color_maps: this.colorMaps,
          },
          {
            no_activity: true,
          },
        );
        if (response && response.results) {
          await this.getTagSettings();
          this.selectedTagId = response.results.id;
          this.onSelectedTagIdChanged();
        }
      } finally {
        this.loading = false;
      }
    },
    async onDelete() {
      try {
        this.loading = true;
        const response = await this.$rest.post(
          `/tags/${this.appName}/${this.objectType}/delete`,
          {
            id: this.selectedTag.id,
          },
          {
            no_activity: true,
          },
        );
        if (response) {
          await this.getTagSettings();
        }
        this.resetData();
      } finally {
        this.loading = false;
      }
    },
    async getTagMigrateInfo() {
      try {
        this.loading = true;
        const response = await this.$rest.post(
          `/tags/${this.appName}/${this.objectType}/migrate_all`,
          {
            from_key: this.selectedTag.original_name,
            to_key: this.selectedTag.name,
            do_update: false,
          },
          {
            no_activity: true,
          },
        );
        if (response) {
          this.selectedTagMigrateInfo = response.total;
        }
      } finally {
        this.loading = false;
      }
    },
    initAddingColorItem() {
      this.addingColorItem = { value: "", color: "#FF0000" };
    },
    resetData() {
      this.selectedTag = { ...this.buildTagSetting() };
      this.colorMaps = [];
      this.originalSelectedTag = { ...this.buildTagSetting() };
      this.initAddingColorItem();
    },
    addNewColorSetting() {
      if (!this.addingColorItem.value || !this.addingColorItem.color) {
        return;
      }
      if (!this.selectedTag.attributes.colors) {
        this.selectedTag.attributes.colors = [];
      }
      if (
        this.colorMaps.findIndex(
          item => item.value === this.addingColorItem.value,
        ) > -1
      ) {
        return;
      }
      this.colorMaps.push({
        ...this.addingColorItem,
        menu: false,
      });
      this.initAddingColorItem();
    },
    onColorSettingDelete({ id }) {
      this.colorMaps.splice(id, 1);
    },
    onSelectedTagIdChanged() {
      const tag = this.tagSettings.find(item => item.id === this.selectedTagId);
      if (!tag) {
        this.selectedTag = { ...this.buildTagSetting() };
      } else {
        this.selectedTag = { ...tag };
      }
      this.originalSelectedTag = {
        ...this.selectedTag,
      };
    },
  },
  computed: {
    isEditing() {
      return this.selectedTag && this.selectedTag.id;
    },
    hasChanged() {
      const colors = this.colorMaps.map(item => ({
        value: item.value,
        color: item.color,
      }));

      const check =
        !isEqual(this.selectedTag, this.originalSelectedTag) ||
        !isEqual(
          JSON.parse(
            JSON.stringify(
              _get(this.originalSelectedTag, "attributes.colors", []),
            ),
          ),
          colors,
        );
      return check;
    },
    canSave() {
      return this.selectedTag.name && this.selectedTag.name.length > 0;
    },
  },
  watch: {
    async showDialog(val) {
      if (val) {
        await this.getTagSettings();
      } else {
        this.resetData();
        this.$emit("closed");
      }
    },
    selectedTagId() {
      this.onSelectedTagIdChanged();
    },
    "selectedTag.attributes": {
      deep: true,
      handler() {
        if (
          this.selectedTag.attributes.colors &&
          this.selectedTag.attributes.colors.length > 0
        ) {
          this.colorMaps = this.selectedTag.attributes.colors.map(item => ({
            ...item,
            menu: false,
          }));
        } else {
          this.initAddingColorItem();
          this.colorMaps = [];
        }
      },
    },
    "selectedTag.name"(val) {
      if (
        this.selectedTag.id &&
        val.length > 0 &&
        val !== this.originalSelectedTag.name
      ) {
        this.debouncedGetMigrateInfo();
      }
    },
    errors() {
      if (this.errors && this.errors.length > 0) {
        this.hasError = true;
      }
    },
    hasError() {
      if (this.hasError === false) {
        this.errors = "";
      }
    },
    isEditing() {
      if (this.isEditing) {
        this.hasError = false;
      } else {
        this.selectedTagId = null;
      }
    },
  },
};
</script>

<style scoped>
.item-list {
  height: 500px;
  overflow: auto;
  border-right: 1px solid #e0e0e0;
  border-radius: 0;
}
.item-detail {
}
.color-maps {
  height: 300px;
  overflow: auto;
}
</style>
