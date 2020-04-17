<template>
  <v-content>
    <v-container grid-list-xs class="pa-0">
      <login-form></login-form>
    </v-container>
  </v-content>
</template>

<script>
import LoginForm from "../components/forms/LoginForm";

export default {
  components: { LoginForm },
  mounted() {
    const accessToken = localStorage.getItem("accessToken");
    if (accessToken && accessToken !== "undefined") {
      this.$router.replace("/");
    }
  },
};
</script>
