<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: "App",
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
