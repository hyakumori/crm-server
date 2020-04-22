<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
import eventBus from "./BusEvent";

export default {
  name: "App",
  mounted() {
    eventBus.$on("auth:relogin", () => {
      localStorage.clear();
      this.$router.push({ name: "auth-login" }).catch();
    });
    eventBus.$on("rest:404", () => {
      this.$router.replace({ name: "not-found" }).catch();
    });
  },
};
</script>

<style lang="scss">
$background-color: #f5f5f5;
$content-width: 1400px;

html {
  background-color: $background-color;
  overflow: auto !important;
}

#app {
  height: 100vh;
  background-color: $background-color;
  margin-left: auto;
  margin-right: auto;
}
</style>
