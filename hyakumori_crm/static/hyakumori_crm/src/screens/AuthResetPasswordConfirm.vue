<template>
  <v-content>
    <v-container grid-list-xs class="pa-0">
      <reset-password-confirm-form></reset-password-confirm-form>
    </v-container>
  </v-content>
</template>
<script>
import ResetPasswordConfirmForm from "../components/forms/ResetPasswordConfirmForm";
export default {
  components: {
    ResetPasswordConfirmForm,
  },
};
</script>
