<template>
  <div class="memo-input ml-6 mb-6" @click.stop="isUpdate = true">
    <h4 class="mb-1">備考</h4>
    <v-progress-linear
      height="2"
      indeterminate
      rounded
      v-if="isLoading"
    ></v-progress-linear>

    <v-card
      class="memo-input__card d-flex"
      flat
      :ripple="false"
      :class="{ 'd-hover': !isUpdate }"
    >
      <div class="d-flex pa-4">
        <div v-if="!isUpdate">
          <p
            class="ma-0"
            v-html="formattedMemo || (isEmpty && $t('memo.empty'))"
            :class="{ 'grey--text': isEmpty }"
          ></p>
        </div>

        <div class="memo-input__value" v-else>
          <ValidationProvider v-slot="{ errors }" slim>
            <v-textarea
              outlined
              name="input-7-4"
              v-model="memo"
              placeholder="テキストを入力してください"
              :error-messages="errors[0]"
            ></v-textarea>

            <update-button
              class="mb-2"
              :saveDisabled="isEmpty"
              :cancel="onCancel"
              :save="onSave"
              :saving="isLoading"
            />
          </ValidationProvider>
        </div>
      </div>
    </v-card>
  </div>
</template>

<script>
import { ValidationProvider } from "vee-validate";
import UpdateButton from "./UpdateButton";

export default {
  props: {
    apiUrl: { type: String },
    value: { type: Object },
  },
  components: {
    ValidationProvider,
    UpdateButton,
  },
  data() {
    return {
      isLoading: false,
      isUpdate: false,
      memo: "",
    };
  },
  methods: {
    async onSave() {
      try {
        this.isLoading = true;
        const response = await this.$rest.post(this.apiUrl, {
          memo: this.memo,
        });
        if (response) {
          this.memo = response.memo;
          this.value.attributes["memo"] = response.memo;
          this.$emit("input", this.value);
        }
      } catch (e) {
      } finally {
        setTimeout(() => {
          this.isLoading = false;
          this.isUpdate = false;
        }, 300);
      }
    },
    onCancel() {
      this.memo = this.value.attributes["memo"];
      this.isLoading = false;
      this.isUpdate = false;
    },
  },
  computed: {
    formattedMemo() {
      return (this.memo && this.memo.replace(/(?:\r\n|\r|\n)/g, "<br>")) || "";
    },
    isEmpty() {
      return !this.memo;
    },
  },
  watch: {
    "value.attributes.memo"() {
      this.memo = this.value.attributes["memo"];
    },
  },
};
</script>

<style lang="scss" scoped>
.memo-input {
  width: 400px;
  cursor: pointer;
  word-break: break-all;
  &__card {
    min-height: 70px;
    box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);
    align-items: center;
    &__input {
      width: 100%;
    }
  }

  ::v-deep .v-input__slot {
    width: 368px;
  }
}
</style>
