<template>
  <v-dialog v-model="shown" scrollable max-width="720">
    <template v-slot:activator="{ on }">
      <outline-round-btn
        :icon="$t('icon.add')"
        :content="$t('buttons.add_customer')"
        :on="on"
      />
    </template>
    <v-card>
      <v-card-actions class="px-6 py-4">
        <v-card-title class="pa-0">{{
          $t("forms.titles.create_customer")
        }}</v-card-title>
        <v-spacer />
        <v-icon @click="shown = false">mdi-close</v-icon>
      </v-card-actions>
      <v-divider></v-divider>
      <v-card-text style="min-height: 300px;" class="px-6 py-5">
        <ValidationObserver ref="form">
          <v-form>
            <v-row no-gutters>
              <v-col class="pe-2">
                <label class="font-weight-bold">{{
                  $t("forms.labels.customer.last_name_kanji")
                }}</label>
                <TextInput
                  v-model="form.last_name_kanji"
                  :placeholder="
                    $t('forms.placeholders.customer.last_name_kanji')
                  "
                  name="basic_contact.name_kanji.last_name"
                />
              </v-col>
              <v-col class="pe-6">
                <label class="font-weight-bold">{{
                  $t("forms.labels.customer.first_name_kanji")
                }}</label>
                <TextInput
                  v-model="form.first_name_kanji"
                  :placeholder="
                    $t('forms.placeholders.customer.first_name_kanji')
                  "
                  name="basic_contact.name_kanji.first_name"
                />
              </v-col>
              <v-col class="pe-2">
                <label class="font-weight-bold">{{
                  $t("forms.labels.customer.last_name_kana")
                }}</label>
                <TextInput
                  v-model="form.last_name_kana"
                  :placeholder="
                    $t('forms.placeholders.customer.last_name_kana')
                  "
                  name="basic_contact.name_kana.last_name"
                />
              </v-col>
              <v-col>
                <label class="font-weight-bold">{{
                  $t("forms.labels.customer.first_name_kana")
                }}</label>
                <TextInput
                  v-model="form.first_name_kana"
                  :placeholder="
                    $t('forms.placeholders.customer.first_name_kana')
                  "
                  name="basic_contact.name_kana.first_name"
                />
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col class="pe-6">
                <label class="font-weight-bold">{{
                  $t("forms.labels.customer.postal_code")
                }}</label>
                <TextInput
                  v-model="form.postal_code"
                  :placeholder="$t('forms.placeholders.customer.postal_code')"
                  name="basic_contact.postal_code"
                />
              </v-col>
              <v-col>
                <label class="font-weight-bold">{{
                  $t("forms.labels.address")
                }}</label>
                <TextInput
                  v-model="form.address"
                  :placeholder="$t('forms.placeholders.customer.address')"
                  name="basic_contact.address.sector"
                />
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col class="pe-6">
                <label class="font-weight-bold">{{
                  $t("forms.labels.customer.phone_number")
                }}</label>
                <TextInput
                  name="basic_contact.telephone"
                  :placeholder="$t('forms.placeholders.customer.phone_number')"
                  v-model="form.phone_number"
                />
              </v-col>
              <v-col>
                <label class="font-weight-bold">{{
                  $t("forms.labels.customer.mobile_number")
                }}</label>
                <TextInput
                  name="basic_contact.mobilephone"
                  :placeholder="$t('forms.placeholders.customer.mobile_number')"
                  v-model="form.mobile_number"
                />
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col class="col-6 pe-3">
                <label class="font-weight-bold">{{
                  $t("forms.labels.email")
                }}</label>
                <TextInput
                  name="basic_contact.email"
                  :placeholder="$t('forms.placeholders.customer.email')"
                  v-model="form.email"
                />
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col>
                <v-btn text class="primary--text"
                  ><v-icon left>mdi-plus</v-icon
                  >{{ $t("forms.labels.customer.add_more_info") }}</v-btn
                >
              </v-col>
            </v-row>
          </v-form>
        </ValidationObserver>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-btn color="primary" @click="submit">{{ $t("buttons.save") }}</v-btn>
        <v-btn text @click="shown = false">{{ $t("buttons.cancel") }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { ValidationObserver, setInteractionMode } from "vee-validate";
import gql from "graphql-tag";
import TextInput from "./forms/TextInput";
import BusEvent from "../BusEvent";
import OutlineRoundBtn from "../components/OutlineRoundBtn";

setInteractionMode("eager");

export default {
  components: {
    ValidationObserver,
    TextInput,
    OutlineRoundBtn,
  },
  data() {
    return {
      shown: false,
      form: this.initForm(),
    };
  },
  methods: {
    initForm() {
      return {
        first_name_kanji: "",
        last_name_kanji: "",
        first_name_kana: "",
        last_name_kana: "",
        postal_code: "",
        address: "",
        phone_number: "",
        mobile_number: "",
        email: "",
      };
    },
    submit() {
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
            sector: this.form.address,
          },
          postal_code: this.form.postal_code,
          telephone: this.form.phone_number,
          mobilephone: this.form.mobile_number,
          email: this.form.email,
        },
      };
      this.$apollo.mutate({
        mutation: gql`
          mutation($input: CreateCustomerInput!) {
            create_customer(data: $input) {
              ok
              error
            }
          }
        `,
        variables: {
          input: customerInput,
        },
        update: (store, { data: { create_customer } }) => {
          if (!create_customer.ok) {
            this.$refs.form.setErrors(create_customer.error);
          } else {
            this.$refs.form.reset();
            this.initForm();
            BusEvent.$emit("customersChanged");
            this.shown = false;
          }
        },
      });
    },
  },
};
</script>
