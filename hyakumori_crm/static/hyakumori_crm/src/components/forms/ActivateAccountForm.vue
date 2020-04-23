<template>
  <v-card class="pa-0 elevation-24">
    <ValidationObserver v-slot="{ invalid }">
      <form>
        <v-card-title class="justify-start pb-0 px-6 pt-6">
          {{ $t("page_header.activate_account") }}
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
            <v-row no-gutters v-if="success">
              <v-col cols="12">
                <v-alert dense outlined type="success">
                  {{
                    $t("messages.activate_account_success", {
                      seconds: redirectCount,
                    })
                  }}
                </v-alert>
              </v-col>
            </v-row>
            <v-row no-gutters class="mt-4">
              <v-col cols="12">
                <label class="font-weight-bold">{{
                  $t("activate_form.last_name")
                }}</label>
                <text-input
                  v-model="form.last_name"
                  :placeholder="$t('messages.field_optional')"
                  name="activate_form.last_name"
                />
              </v-col>
            </v-row>
            <v-row no-gutters class="mt-4">
              <v-col cols="12">
                <label class="font-weight-bold">{{
                  $t("activate_form.first_name")
                }}</label>
                <text-input
                  v-model="form.first_name"
                  :placeholder="$t('messages.field_optional')"
                  name="activate_form.first_name"
                />
              </v-col>
            </v-row>
            <v-row no-gutters class="mt-4">
              <v-col cols="12">
                <label class="font-weight-bold">{{
                  $t("activate_form.new_password")
                }}</label>
                <text-input
                  type="password"
                  v-model="form.password"
                  rules="required|min:8"
                  placeholder=" ◍ ◍ ◍ ◍ ◍ ◍ ◍ ◍ "
                  name="activate_form.new_password"
                />
              </v-col>
            </v-row>
            <v-row no-gutters class="mt-4">
              <v-col cols="12" class="relative">
                <label class="font-weight-bold">
                  {{ $t("activate_form.new_password_retype") }}
                </label>
                <text-input
                  type="password"
                  v-model="form.password_retype"
                  rules="required|min:8|password:@activate_form.new_password"
                  placeholder=" ◍ ◍ ◍ ◍ ◍ ◍ ◍ ◍ "
                  name="activate_form.new_password_retype"
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
                  :disabled="invalid || loading || success"
                  >{{ $t("buttons.activate") }}
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
        first_name: "",
        last_name: "",
        password: "",
        password_retype: "",
      },
      formError: "",
      loading: false,
      showPassword: false,
      success: false,
      redirectInterval: null,
      redirectCount: 3,
    };
  },
  methods: {
    async onSubmit() {
      try {
        this.loading = true;
        await this.$rest.post(`/users/activation`, {
          uid: this.$route.params.uid,
          token: this.$route.params.token,
          new_password: this.form.password,
          re_new_password: this.form.password_retype,
          first_name: this.form.first_name,
          last_name: this.form.last_name,
        });
        this.success = true;
        this.redirectInterval = setInterval(() => {
          if (this.redirectCount == 0) {
            clearInterval(this.redirectInterval);
            return this.$router.push({ name: "auth-login" });
          }
          this.redirectCount -= 1;
        }, 1000);
      } catch (err) {
        this.success = false;
        const error_data = err.response.data;
        if (Object.keys(error_data).indexOf("uid") > -1) {
          this.formError = this.$t("messages.uid_not_found");
        } else if (Object.keys(error_data).indexOf("token") > -1) {
          this.formError = this.$t("messages.token_stale");
        } else {
          this.formError = this.$t("messages.error_set_new_password");
        }
      } finally {
        this.loading = false;
      }
    },
  },
  created() {
    extend("password", {
      params: ["target"],
      validate(value, { target }) {
        return value === target;
      },
      message: this.$t("activate_form.password_not_match"),
    });
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
.forgot-password-hint {
  position: absolute;
  right: 0;
  top: 0;
  a {
    text-decoration: none !important;
  }
}
</style>
