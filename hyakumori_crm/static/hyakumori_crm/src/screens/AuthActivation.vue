<template>
  <v-content>
    <v-container grid-list-xs class="pa-0">
      <activate-account-form></activate-account-form>
    </v-container>
  </v-content>
</template>
<script>
import ActivateAccountForm from "../components/forms/ActivateAccountForm";
export default {
  components: {
    ActivateAccountForm,
  },
};
</script>
