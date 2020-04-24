<script>
import { ValidationObserver, setInteractionMode } from "vee-validate";
import TextInput from "./TextInput";

setInteractionMode("eager");

export default {
  components: {
    ValidationObserver,
    TextInput,
  },
  props: ["form", "id", "toggleEditing"],
  data() {
    return {
      shown: false,
      submiting: false,
    };
  },
  methods: {
    async submit() {
      this.submiting = true;
      try {
        const data = await this.$rest.put(
          `/customers/${this.id}/bank`,
          this.form,
        );
        this.submiting = false;
        this.$emit("updated");
        this.toggleEditing();
      } catch (error) {
        console.log(error);
        this.submiting = false;
        if (error.response) {
          this.$refs.form.setErrors(error.response.data.errors);
        }
      }
    },
  },
};
</script>

<template>
  <ValidationObserver ref="form" v-slot="{ dirty, invalid }">
    <v-form>
      <v-row>
        <v-col class="">
          <label class="font-weight-bold">{{
            $t("forms.labels.bank.bank_name")
          }}</label>
          <TextInput v-model="form.bank_name" name="bank_name" />
        </v-col>
        <v-col>
          <label class="font-weight-bold">{{
            $t("forms.labels.bank.branch_name")
          }}</label>
          <TextInput v-model="form.branch_name" name="branch_name" />
        </v-col>
      </v-row>
      <v-row>
        <v-col class="">
          <label class="font-weight-bold">{{
            $t("forms.labels.bank.account_type")
          }}</label>
          <TextInput v-model="form.account_type" name="account_type" />
        </v-col>
        <v-col>
          <label class="font-weight-bold">{{
            $t("forms.labels.bank.account_number")
          }}</label>
          <TextInput v-model="form.account_number" name="account_number" />
        </v-col>
      </v-row>
      <v-row>
        <v-col class="">
          <label class="font-weight-bold">{{
            $t("forms.labels.bank.account_name")
          }}</label>
          <TextInput v-model="form.account_name" name="account_name" />
        </v-col>
        <v-col></v-col>
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
            >{{ $t("buttons.save") }}</v-btn
          >
          <v-btn @click="toggleEditing" text color="#999999">{{
            $t("buttons.cancel")
          }}</v-btn>
        </v-col>
      </v-row>
    </v-form>
  </ValidationObserver>
</template>
