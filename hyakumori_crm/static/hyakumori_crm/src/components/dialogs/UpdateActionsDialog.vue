<template>
  <v-dialog v-model="isShowDialog" max-width="700" transition persistent>
    <ValidationObserver v-slot="{ invalid }">
      <v-card>
        <v-card-title class="display-0">
          {{ $t("action.change_tag_value") }}
        </v-card-title>
        <v-card-text class="pb-0">
          <v-row>
            <v-col cols="6">
              <h4>タグを選択</h4>
              <v-select
                ref="tagList"
                outlined
                dense
                height="45"
                no-data-text="データなし"
                :items="items"
                :loading="loadingItems"
                @change="onItemChange"
              />
            </v-col>
            <v-col cols="6">
              <h4>タグバリュー</h4>
              <text-input
                v-model="newValue"
                label="タグバリュー"
                rules="required|max:255"
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions class="px-4">
          <v-btn text color="primary" :disabled="updating" @click="onCancel"
            >Cancel</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            text
            color="primary"
            @click="onUpdateData"
            :disabled="invalid || isDisableUpdate"
            :loading="updating"
            >OK</v-btn
          >
        </v-card-actions>
      </v-card>
    </ValidationObserver>
  </v-dialog>
</template>

<script>
import { ValidationObserver } from "vee-validate";
import TextInput from "../forms/TextInput";
import { cloneDeep } from "lodash";

export default {
  name: "update-action-dialog",

  components: {
    ValidationObserver,
    TextInput,
  },

  props: {
    items: Array,
    isDisableUpdate: Boolean,
    updateData: Function,
    showDialog: Boolean,
    loadingItems: Boolean,
    updating: Boolean,
    cancel: Function,
  },

  data() {
    return {
      selectedItem: null,
      newValue: null,
      isShowDialog: null,
    };
  },

  methods: {
    onItemChange(val) {
      this.selectedItem = val;
      this.$emit("selected-tag", val);
    },

    setDefault() {
      this.newValue = null;
      this.$refs.tagList.internalValue = null;
      this.isShowDialog = false;
      this.$emit("toggle-show-dialog", this.isShowDialog);
    },

    async onUpdateData() {
      await this.updateData();
      this.setDefault();
    },

    onCancel() {
      this.cancel();
      this.setDefault();
    },
  },

  watch: {
    newValue(val) {
      this.$emit("update-value", val);
    },

    showDialog(val) {
      this.isShowDialog = cloneDeep(val);
    },
  },
};
</script>

<style scoped></style>
