<template>
  <v-app>
    <v-content fill-height class="main d-flex">
      <div class="gradient-background"></div>
      <v-container
        grid-list-lg
        class="main-container d-flex justify-center flex-column pa-0"
      >
        <div class="d-flex justify-center">
          <img
            :src="require('@/assets/img/crm-logo.png')"
            height="20"
            class="logo"
          />
        </div>

        <router-view class="main-content"></router-view>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
export default {};
</script>

<style lang="scss">
.main {
  position: relative;
  background: url("../assets/img/background.png") no-repeat center center;
  background-size: cover;
}
.logo {
  margin: 70px 0;
  text-align: center;
}
.gradient-background {
  z-index: 1;
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  background: linear-gradient(
    89.57deg,
    rgba(14, 102, 91, 0.69) 0%,
    rgba(13, 255, 226, 0) 100%
  );
}
.main-container {
  max-width: 430px;
  position: relative;
  z-index: 2;
}
.main-content {
  .v-card__title:first-child {
    font-weight: bold;
    font-size: 17px;
  }
}
</style>
