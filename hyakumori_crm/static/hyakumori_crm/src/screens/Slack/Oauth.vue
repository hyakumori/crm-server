<template>
  <v-content>
    <v-container grid-list-xs class="pa-0">
      <auth-form ref="authForm" :onSubmit="slackOauth"></auth-form>
    </v-container>
  </v-content>
</template>

<script>
import AuthForm from "./AuthForm";

export default {
  components: { AuthForm },
  methods: {
    async slackOauth() {
      await this.$rest.post("slack/oauth", {
        ...this.$refs.authForm.form,
        code: this.code,
      });
    },
  },
  computed: {
    code() {
      return this.$route.query.code;
    },
  },
};
</script>
