<template>
  <v-card class="pa-0 elevation-24">
    <ValidationObserver v-slot="{ invalid }" ref="form">
      <form @submit.prevent="onSubmit">
        <v-card-title class="justify-start pb-0 px-6 pt-6">
          {{ $t("page_header.user_invite") }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-container fluid class="pa-0">
            <v-row no-gutters v-if="formError">
              <v-col cols="12">
                <v-alert dense outlined type="error" dismissible>
                  {{ formError }}
                </v-alert>
              </v-col>
            </v-row>
            <v-row no-gutters v-if="successfulEmail">
              <v-col cols="12">
                <v-alert
                  dense
                  outlined
                  type="success"
                  :value="successfulEmail"
                  dismissible
                >
                  {{
                    $t("messages.invitation_sent", { email: successfulEmail })
                  }}
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
                  >{{ $t("buttons.send") }}
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
  props: {
    show: { type: Boolean },
  },
  data() {
    return {
      form: {
        email: "",
      },
      formError: "",
      loading: false,
      successfulEmail: null,
    };
  },
  methods: {
    randomPassword(length = 8) {
      return Math.random()
        .toString(36)
        .slice(-length);
    },
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
        this.loading = true;
        const password = this.randomPassword();
        const response = await this.$rest.post("/users", {
          ...this.form,
          password,
        });

        if (response) {
          this.loading = false;
          this.formError = "";
          this.$emit("success", response);
          this.successfulEmail = this.form.email;
          this.form = { email: "" };
          this.$refs.form.reset();
        }
      } catch (e) {
        this.formError = this.$t("messages.fail_create_user");
      } finally {
        this.loading = false;
      }
    },
  },
  watch: {
    show(val) {
      if (val) {
        this.loading = false;
        this.successfulEmail = null;
        this.formError = "";
        this.form = {
          email: "",
        };
        this.$refs.form.reset();
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
