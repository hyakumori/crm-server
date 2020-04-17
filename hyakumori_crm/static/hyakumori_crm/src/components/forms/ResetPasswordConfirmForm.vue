<template>
  <v-card class="pa-0 elevation-24">
    <ValidationObserver v-slot="{ invalid }">
      <form>
        <v-card-title class="justify-start pb-0 px-6 pt-6">
          {{ $t("page_header.forgot_password") }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-container fluid class="pa-0">
            <v-row no-gutters>
              <p class="grey--text text--darken-3">
                {{ $t("messages.reset_password_confirm_help_text") }}
              </p>
            </v-row>
            <v-row no-gutters>
              <v-col cols="12">
                <label class="font-weight-bold">{{
                  $t("reset_password_form.new_password")
                }}</label>
                <text-input
                  type="password"
                  v-model="form.password"
                  rules="required|min:8"
                  placeholder=" ◍ ◍ ◍ ◍ ◍ ◍ ◍ ◍ "
                  name="reset_password_form.new_password"
                />
              </v-col>
            </v-row>
            <v-row no-gutters class="mt-4">
              <v-col cols="12" class="relative">
                <label class="font-weight-bold">
                  {{ $t("reset_password_form.new_password_retype") }}
                </label>
                <text-input
                  type="password"
                  v-model="form.password_retype"
                  rules="required|min:8|password:@reset_password_form.new_password"
                  placeholder=" ◍ ◍ ◍ ◍ ◍ ◍ ◍ ◍ "
                  name="reset_password_form.new_password_retype"
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
                  color="primary"
                  depressed
                  @click="onSubmit"
                  width="100%"
                  :disabled="invalid"
                  >{{ $t("buttons.send") }}
                </v-btn>
              </v-col>
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
import { ValidationObserver, extend } from "vee-validate";
import TextInput from "../forms/TextInput";

export default {
  components: {
    TextInput,
    ValidationObserver,
  },
  data() {
    return {
      form: {
        password: "",
        password_retype: "",
      },
      formError: "",
      showPassword: false,
      success: false,
    };
  },
  methods: {
    onSubmit() {},
  },
  created() {
    extend("password", {
      params: ["target"],
      validate(value, { target }) {
        return value === target;
      },
      message: this.$t("reset_password_form.password_not_match"),
    });
  },
};
</script>

<style lang="scss" scoped>
.forgot-password-hint {
  position: absolute;
  right: 0;
  top: 0;
  a {
    text-decoration: none !important;
  }
}
</style>
