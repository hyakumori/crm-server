<template>
  <v-card class="pa-0 elevation-24">
    <ValidationObserver v-slot="{ invalid }">
      <form @submit.prevent="onSubmit">
        <v-card-title class="justify-start pb-0 px-6 pt-6 text-color-444444">
          {{ $t("page_header.forgot_password") }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-container fluid class="pa-0">
            <v-row no-gutters v-if="formError">
              <v-col cols="12">
                <v-alert dense outlined type="error">
                  {{ formError }}
                </v-alert>
              </v-col>
            </v-row>
            <v-row no-gutters>
              <p class="text--darken-3 text-color-444444">
                {{ $t("messages.forgot_password_help_text") }}
              </p>
            </v-row>
            <v-row no-gutters>
              <v-col cols="12">
                <label class="font-weight-bold text-color-444444">{{
                  $t("login_form.email")
                }}</label>
                <text-input
                  :disabled="success"
                  v-model="form.email"
                  placeholder="abc@example.com"
                  hideDetails="auto"
                  name="login_form.email"
                  type="email"
                  rules="required|email"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>

        <v-card-actions class="pa-6 pt-0">
          <v-container class="pa-0">
            <v-row class="fill-height">
              <v-col class="pt-0 pb-0 text-right" cols="12">
                <v-btn
                  class="font-weight-bold"
                  color="primary"
                  depressed
                  width="100%"
                  @click="onSubmit"
                  :loading="loading"
                  :disabled="invalid || success"
                  >{{ $t("buttons.send") }}
                </v-btn>
              </v-col>
            </v-row>
            <v-row>
              <div class="message ma-3 mb-0" v-if="mailSent">
                {{ $t("messages.reset_password_url_sent") }}
              </div>
            </v-row>
            <v-row>
              <router-link
                class="no-underline f14 pa-4 pt-6 pb-0"
                :to="{ name: 'auth-login' }"
              >
                {{ $t("login_form.go_to_login") }}
              </router-link>
            </v-row>
          </v-container>
        </v-card-actions>
      </form>
    </ValidationObserver>
  </v-card>
</template>

<script>
import { ValidationObserver } from "vee-validate";
import TextInput from "../forms/TextInput";

export default {
  components: {
    TextInput,
    ValidationObserver,
  },
  data() {
    return {
      form: {
        email: "",
      },
      formError: "",
      success: false,
      loading: false,
    };
  },
  methods: {
    async onSubmit() {
      try {
        this.loading = true;
        await this.$rest.post(`/users/reset_password`, {
          email: this.form.email,
        });
        this.success = true;
      } catch (err) {
        if (err.response && err.response.status < 500)
          this.formError = this.$t("messages.email_not_found");
      } finally {
        this.loading = false;
      }
    },
  },
  computed: {
    mailSent: function() {
      return this.success;
    },
  },
  watch: {
    success(val) {
      if (val) {
        this.formError = "";
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.message {
  border-radius: 4px;
  padding: 15px 20px;
  font-size: 14px;
  background: #f5f5f5;
  color: #444444;
}
</style>
