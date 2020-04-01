<template>
  <div class="page-header">
    <v-img src="../assets/img/app-bar.webp" height="150"></v-img>

    <div class="page-header-content">
      <div class="d-flex justify-space-between">
        <div class="logo-section">
          <img src="../assets/img/logo.webp" alt="Logo big text" height="18" />

          <img
            class="ml-3"
            src="../assets/img/crm.webp"
            alt="Logo small text"
            height="12"
          />
        </div>

        <div class="menu caption pa-7">
          <router-link to="/forests">
            {{ $t("page_header.forest_list") }}
          </router-link>

          <router-link to="/clients" class="ml-4 mr-4">
            {{ $t("page_header.client_list") }}
          </router-link>

          <router-link to="/archives" class="mr-4">
            {{ $t("page_header.archive_list") }}
          </router-link>

          <router-link to="/settings">
            {{ $t("page_header.setting") }}
          </router-link>
        </div>
      </div>

      <div>
        <v-icon class="icon-mode">{{ getPageIcon }}</v-icon>

        <span class="ml-3 white--text">
          {{ getPageTitle }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "page-header",

  data() {
    return {
      mode: {
        FOREST: "forests",
        CLIENT: "clients",
        ARCHIVE: "archives"
      }
    };
  },

  computed: {
    getPageIcon() {
      const routePath = this.$route.path;
      if (routePath.includes(this.mode.FOREST)) {
        return this.$t("icon.forest_icon");
      } else if (routePath.includes(this.mode.CLIENT)) {
        return this.$t("icon.client_icon");
      } else {
        return this.$t("icon.archive_icon");
      }
    },

    getPageTitle() {
      const routePath = this.$route.path;
      if (routePath.includes(this.mode.FOREST)) {
        return this.$t("page_header.forest_list");
      } else if (routePath.includes(this.mode.CLIENT)) {
        return this.$t("page_header.client_list");
      } else if (routePath.includes(this.mode.ARCHIVE)) {
        return this.$t("page_header.archive_list");
      } else {
        return this.$t("page_header.setting");
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.page-header {
  position: relative;

  .page-header-content {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background: linear-gradient(
      87.07deg,
      #1b756a 0%,
      rgba(196, 196, 196, 0) 100%
    );

    .logo-section {
      padding: 28px;
    }

    .menu a {
      color: white;
      text-decoration: none;
    }

    .icon-mode {
      background-color: white;
      margin-left: 28px;
      height: 40px;
      width: 40px;
      padding: 15px;
      border-radius: 50%;
    }
  }
}
</style>
