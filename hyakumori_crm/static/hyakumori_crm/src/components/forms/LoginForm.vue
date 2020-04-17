<template>
  <v-card class="pa-0 elevation-24">
    <ValidationObserver v-slot="{ invalid }">
      <form @submit.prevent="onSubmit">
        <v-card-title class="justify-start pb-0 px-6 pt-6">
          {{ $t("page_header.login") }}
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
              <v-col cols="12">
                <label class="font-weight-bold">{{
                  $t("login_form.email")
                }}</label>
                <text-input
                  v-model="form.email"
                  placeholder="abc@example.com"
                  rules="required|email"
                  type="email"
                  name="login_form.email"
                />
              </v-col>
            </v-row>
            <v-row no-gutters class="mt-4">
              <v-col cols="12" class="relative">
                <label class="font-weight-bold">
                  {{ $t("login_form.password") }}
                </label>
                <div class="forgot-password-hint">
                  <router-link
                    :to="{ name: 'auth-forgot-password' }"
                    class="f14"
                  >
                    {{ $t("login_form.forgot_password_hint") }}
                  </router-link>
                </div>
                <text-input
                  type="password"
                  v-model="form.password"
                  rules="required|min:8"
                  placeholder=" ◍ ◍ ◍ ◍ ◍ ◍ ◍ ◍ "
                  name="login_form.password"
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
                  width="100%"
                  :loading="loading"
                  @click="onSubmit"
                  :disabled="invalid || loading"
                  >{{ $t("page_header.login") }}
                </v-btn>
              </v-col>
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
        password: "",
      },
      formError: "",
      loading: false,
      success: false,
    };
  },
  methods: {
    async getPermissions(user_id) {
      const permissions = await this.$rest.get(`/users/${user_id}/permissions`);
      const scopes = [];

      if (permissions.is_admin) {
        scopes.push("admin");
      }
      if (permissions.is_staff) {
        scopes.push("staff");
      }
      permissions.groups.forEach(item => scopes.push(item.name));
      localStorage.setItem("scopes", scopes.join(","));
    },

    async getUserProfile(localStorage) {
      const user = await this.$rest.get("/users/me");
      if (user) {
        localStorage.setItem("user", JSON.stringify(user));
        await this.getPermissions(user.id);
      }
    },

    async onSubmit() {
      try {
        const response = await this.$rest.post("/token/create/", {
          ...this.form,
        });

        if (response) {
          const { access, refresh } = response;
          this.loading = true;

          localStorage.setItem("accessToken", access);
          localStorage.setItem("refreshToken", refresh);

          await this.getUserProfile(localStorage);

          this.success = true;
          this.formError = "";

          setTimeout(() => {
            this.loading = false;
            this.$router.replace("/");
          }, 500);
        }
      } catch (e) {
        this.formError = this.$t("login_form.errors.auth_failed");
        this.success = false;
        setTimeout(() => {
          this.loading = false;
        }, 500);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.forgot-password-hint {
  position: absolute;
  right: 0;
  top: -1px;
  a {
    text-decoration: none !important;
  }
}
</style>
