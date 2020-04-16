<template>
  <div>
    <h1>Login</h1>
    <v-btn @click="doLogin">Login</v-btn>
  </div>
</template>

<script>
export default {
  methods: {
    doLogin() {
      localStorage.setItem("accessToken", "dummytoken");
    },
  },
};
</script>
