<template>
  <div id="app">
    <v-snackbar
      color="cyan darken-2"
      v-model="inMaintain"
      top
      :timeout="0"
      multi-line
    >
      {{ $t("messages.maintenance_1") }}<br />{{ $t("messages.maintenance_2") }}
    </v-snackbar>
    <router-view></router-view>
  </div>
</template>

<script>
import eventBus from "./BusEvent";
import { mapActions, mapState } from "vuex";

export default {
  name: "App",
  created() {
    this.getMaintenanceStatus();
  },
  mounted() {
    eventBus.$on("auth:relogin", () => {
      localStorage.clear();
      this.$router.push({ name: "auth-login" }).catch();
    });
    eventBus.$on("rest:404", () => {
      this.$router.replace({ name: "not-found" }).catch();
    });
  },
  methods: {
    ...mapActions({ getMaintenanceStatus: "getMaintenanceStatus" }),
  },
  computed: {
    ...mapState({
      inMaintain: "inMaintain",
    }),
  },
  watch: {
    $route: "getMaintenanceStatus",
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
