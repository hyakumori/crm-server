<template>
  <v-dialog v-model="isShowDialog" max-width="540" transition persistent>
    <ValidationObserver ref="form" v-slot="{ invalid }">
      <form @submit.prevent="onUpdateData">
        <v-card>
          <v-card-title class="display-0">
            {{ $t("action.change_tag_value") }}
          </v-card-title>
          <v-card-text class="pb-0">
            <v-row>
              <v-col cols="6">
                <h4>タグを選択</h4>
                <ValidationProvider
                  rules="required|max:255"
                  v-slot="{ errors }"
                  name="キー"
                >
                  <v-combobox
                    ref="tagList"
                    outlined
                    dense
                    height="45"
                    no-data-text="データなし"
                    :items="items"
                    :loading="loadingItems"
                    v-model="selectedItem"
                    :error-messages="errors[0]"
                    @change="onItemChange"
                  />
                </ValidationProvider>
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
            <v-btn text color="primary" :disabled="updating" @click="onCancel">
              {{ $t("buttons.cancel") }}
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn
              text
              color="primary"
              @click="onUpdateData"
              :disabled="invalid"
              :loading="updating"
            >
              {{ $t("buttons.ok") }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </ValidationObserver>
  </v-dialog>
</template>

<script>
import { ValidationObserver, ValidationProvider } from "vee-validate";
import TextInput from "../forms/TextInput";
import { cloneDeep } from "lodash";

export default {
  name: "update-actions-dialog",

  components: {
    ValidationObserver,
    ValidationProvider,
    TextInput,
  },

  props: {
    items: Array,
    updateData: Function,
    showDialog: Boolean,
    loadingItems: Boolean,
    updating: Boolean,
    cancel: Function,
  },

  data() {
    return {
      selectedItem: "",
      newValue: "",
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
      this.$refs.form.reset();
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
