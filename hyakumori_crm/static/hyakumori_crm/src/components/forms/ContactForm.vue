<template>
  <ValidationObserver ref="form" v-slot="{ dirty, invalid }">
    <v-form>
      <v-row>
        <v-col class="">
          <label class="font-weight-bold">{{
            $t("forms.labels.customer.last_name_kanji")
          }}</label>
          <TextInput
            v-model="form.last_name_kanji"
            :placeholder="$t('forms.placeholders.customer.last_name_kanji')"
            :name="`${fieldNamePrefix}name_kanji.last_name`"
          />
        </v-col>
        <v-col class="">
          <label class="font-weight-bold">{{
            $t("forms.labels.customer.first_name_kanji")
          }}</label>
          <TextInput
            v-model="form.first_name_kanji"
            :placeholder="$t('forms.placeholders.customer.first_name_kanji')"
            :name="`${fieldNamePrefix}name_kanji.first_name`"
          />
        </v-col>
        <v-col class="">
          <label class="font-weight-bold">{{
            $t("forms.labels.customer.last_name_kana")
          }}</label>
          <TextInput
            v-model="form.last_name_kana"
            :placeholder="$t('forms.placeholders.customer.last_name_kana')"
            :name="`${fieldNamePrefix}name_kana.last_name`"
          />
        </v-col>
        <v-col>
          <label class="font-weight-bold">{{
            $t("forms.labels.customer.first_name_kana")
          }}</label>
          <TextInput
            v-model="form.first_name_kana"
            :placeholder="$t('forms.placeholders.customer.first_name_kana')"
            :name="`${fieldNamePrefix}name_kana.first_name`"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col class="">
          <label class="font-weight-bold">{{
            $t("forms.labels.customer.postal_code")
          }}</label>
          <TextInput
            v-model="form.postal_code"
            :placeholder="$t('forms.placeholders.customer.postal_code')"
            :name="`${fieldNamePrefix}postal_code`"
          />
        </v-col>
        <v-col>
          <label class="font-weight-bold">{{
            $t("forms.labels.sector")
          }}</label>
          <TextInput
            v-model="form.sector"
            :placeholder="$t('forms.placeholders.customer.sector')"
            :name="`${fieldNamePrefix}address.sector`"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col class="">
          <label class="font-weight-bold">{{
            $t("forms.labels.prefecture")
          }}</label>
          <TextInput
            v-model="form.prefecture"
            :placeholder="$t('forms.placeholders.customer.prefecture')"
            :name="`${fieldNamePrefix}address.prefecture`"
          />
        </v-col>
        <v-col>
          <label class="font-weight-bold">{{
            $t("forms.labels.municipality")
          }}</label>
          <TextInput
            v-model="form.municipality"
            :placeholder="$t('forms.placeholders.customer.municipality')"
            :name="`${fieldNamePrefix}address.municipality`"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col class="">
          <label class="font-weight-bold">{{
            $t("forms.labels.customer.phone_number")
          }}</label>
          <TextInput
            v-mask="'##-####-####'"
            :maxLength="12"
            :name="`${fieldNamePrefix}telephone`"
            :placeholder="
              $t('forms.placeholders.customer.phone_number') +
                '（00-0000-0000）'
            "
            v-model="form.telephone"
          />
        </v-col>
        <v-col>
          <label class="font-weight-bold">{{
            $t("forms.labels.customer.mobile_number")
          }}</label>
          <TextInput
            v-mask="'###-####-####'"
            :maxLength="13"
            :name="`${fieldNamePrefix}mobilephone`"
            :placeholder="
              $t('forms.placeholders.customer.mobile_number') +
                '（000-0000-0000）'
            "
            v-model="form.mobilephone"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col class="col-6 pe-3">
          <label class="font-weight-bold">{{ $t("forms.labels.email") }}</label>
          <TextInput
            :name="`${fieldNamePrefix}email`"
            :placeholder="$t('forms.placeholders.customer.email')"
            v-model="form.email"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-btn
            @click="submit"
            depressed
            class="mr-2"
            color="primary"
            :disabled="!dirty || invalid"
            :loading="submiting"
            >{{ id ? $t("buttons.save") : $t("buttons.continue") }}</v-btn
          >
          <v-btn @click="handleCancel" text color="#999999" v-if="showCancel">{{
            $t("buttons.cancel")
          }}</v-btn>
        </v-col>
      </v-row>
    </v-form>
  </ValidationObserver>
</template>

<script>
import { ValidationObserver, setInteractionMode } from "vee-validate";
import TextInput from "./TextInput";
import { cloneDeep } from "lodash";

setInteractionMode("eager");

export default {
  components: {
    ValidationObserver,
    TextInput,
  },
  props: [
    "formData",
    "id",
    "toggleEditing",
    "showCancel",
    "handleSubmit",
    "errors",
  ],
  data() {
    return {
      shown: false,
      form: {},
      submiting: false,
    };
  },
  mounted() {
    if (this.formData) {
      this.form = cloneDeep(this.formData);
    }
  },
  computed: {
    fieldNamePrefix() {
      return this.handleSubmit ? "" : "basic_contact.";
    },
  },
  watch: {
    errors: {
      handler(val) {
        this.$refs.form.setErrors(val);
      },
      deep: true,
    },
    form(val) {
      this.$emit("update:formData", val);
    },
  },
  methods: {
    handleCancel() {
      this.form = { ...this.formData };
      this.toggleEditing();
    },
    async submit() {
      this.submiting = true;
      if (this.handleSubmit) {
        await this.handleSubmit();
      } else {
        await this._submit();
      }
      this.submiting = false;
    },
    async _submit() {
      const customerInput = {
        basic_contact: {
          name_kanji: {
            last_name: this.form.last_name_kanji,
            first_name: this.form.first_name_kanji,
          },
          name_kana: {
            last_name: this.form.last_name_kana,
            first_name: this.form.first_name_kana,
          },
          address: {
            sector: this.form.sector,
            prefecture: this.form.prefecture,
            municipality: this.form.municipality,
          },
          postal_code: this.form.postal_code,
          telephone: this.form.telephone,
          mobilephone: this.form.mobilephone,
          email: this.form.email,
        },
      };
      try {
        if (!this.id) {
          const data = await this.$rest.post("/customers", customerInput);
          this.submiting = false;
          this.$router.push({
            name: "customer-detail",
            params: { id: data.id },
          });
        } else {
          await this.$rest.put(`/customers/${this.id}`, customerInput);
          this.$emit("updated");
          this.toggleEditing();
        }
      } catch (error) {
        if (error.response) {
          this.$refs.form.setErrors(error.response.data.errors);
        }
      }
    },
  },
};
</script>
