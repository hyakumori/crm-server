<template>
  <div class="page-header">
    <v-img src="../assets/img/app-bar.webp" height="160"></v-img>

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

          <router-link to="/customers" class="ml-4 mr-4">
            {{ $t("page_header.customer_list") }}
          </router-link>

          <router-link to="/archives" class="mr-4">
            {{ $t("page_header.archive_list") }}
          </router-link>

          <router-link to="/settings">
            {{ $t("page_header.setting") }}
          </router-link>
        </div>
      </div>

      <v-container fluid class="px-7">
        <v-row>
          <v-col>
            <v-icon class="icon-mode">{{ $store.state.pageIcon }}</v-icon>
            <span class="ml-3 white--text">
              {{ $store.state.pageHeader }}
            </span>
          </v-col>
          <v-col>
            <div class="float-right">
              <CustomerCreateForm v-if="$route.name === 'customers'" />
            </div>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </div>
</template>

<script>
import CustomerCreateForm from "./CustomerCreateForm";
export default {
  name: "page-header",
  components: {
    CustomerCreateForm,
  },
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
      height: 40px;
      width: 40px;
      padding: 15px;
      border-radius: 50%;
    }
  }
}
</style>
