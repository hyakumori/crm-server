<template>
  <v-app>
    <v-content
      :style="cssProps"
      ref="mainContent"
      fill-height
      class="main d-flex"
    >
      <div class="gradient-background"></div>
      <v-container
        grid-list-lg
        class="main-container d-flex justify-center flex-column pa-0"
      >
        <div class="d-flex justify-center">
          <img
            :src="require('@/assets/img/crm-logo.png')"
            height="25"
            class="logo"
          />
        </div>

        <router-view class="main-content"></router-view>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
const imageNum = Math.floor(Math.random() * (3 - 1) + 1);
const background = require(`../assets/img/background${imageNum}.jpg`);

export default {
  data() {
    return {
      cssProps: {
        backgroundImage: `url(${background})`,
      },
    };
  },
};
</script>

<style lang="scss">
.main {
  position: relative;
  background-repeat: no-repeat;
  background-position: center center;
  background-size: cover;
}
.logo {
  margin: 65px 0;
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
    180deg,
    rgba(34, 34, 34, 0.8) 0%,
    rgba(135, 135, 135, 0.3) 15%,
    rgba(255, 255, 255, 0) 30%
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
