<template>
  <v-card class="pa-0 elevation-24">
    <ValidationObserver ref="form" v-slot="{ invalid }">
      <form @submit.prevent="doSubmit" v-on:keyup.enter="doSubmit">
        <v-card-title class="justify-start pb-0 px-6 pt-6 text-color-444444">
          続行するには認証してください
        </v-card-title>

        <v-card-text class="pa-6">
          <v-container fluid class="pa-0">
            <v-row no-gutters v-if="formError">
              <v-col cols="12">
                <v-alert dense outlined type="error">
                  {{ formError }}
                </v-alert>
                戻る...
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="12">
                <label class="font-weight-bold text-color-444444">{{
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
                <label class="font-weight-bold text-color-444444">
                  {{ $t("login_form.password") }}
                </label>
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
                  class="font-weight-bold"
                  color="primary"
                  depressed
                  width="100%"
                  :loading="loading"
                  @click="doSubmit"
                  :disabled="invalid || loading"
                  >認証する
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
import TextInput from "@/components/forms/TextInput";

export default {
  components: {
    TextInput,
    ValidationObserver,
  },
  props: {
    onSubmit: {
      type: Function,
    },
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
    async doSubmit() {
      this.loading = true;
      try {
        const resp = await this.onSubmit();
        this.success = true;
        this.$router.push({ name: "my-profile" });
      } catch (e) {
        this.$refs.form.setErrors(e.response.data);
        this.success = false;
        this.formError = e.response.data.error;
        setTimeout(() => {
          this.$router.push({ name: "my-profile" });
        }, 1500);
      } finally {
        this.loading = false;
      }
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
.forgot-password-hint {
  position: absolute;
  right: 0;
  top: -1px;
  a {
    text-decoration: none !important;
  }
}
</style>
