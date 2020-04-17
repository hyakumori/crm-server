<template>
  <v-content>
    <v-container grid-list-xs class="pa-0">
      <forgot-password-form></forgot-password-form>
    </v-container>
  </v-content>
</template>

<script>
import ForgotPasswordForm from "../components/forms/ForgotPasswordForm";
export default {
  components: {
    ForgotPasswordForm,
  },
};
</script>
