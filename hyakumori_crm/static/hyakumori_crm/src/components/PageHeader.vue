<template>
  <div class="page-header">
    <v-img src="../assets/img/app-bar.png" height="169" v-if="!isDetail" />
    <v-img src="../assets/img/app-bar-detail.jpg" height="169" v-else />

    <div class="page-header__content">
      <div class="page-header__content--center">
        <div class="d-flex justify-space-between">
          <div class="logo-section">
            <img
              src="../assets/img/crm-logo.png"
              alt="Logo big text"
              height="20"
            />
          </div>

          <div class="menu caption pa-7">
            <router-link
              to="/forests"
              v-acl-only="['manage_forest', 'view_forest']"
            >
              {{ $t("page_header.forest_mgmt") }}
            </router-link>

            <router-link
              to="/customers"
              class="ml-4 mr-4"
              v-acl-only="['manage_customer', 'view_customer']"
            >
              {{ $t("page_header.customer_mgmt") }}
            </router-link>

            <router-link
              to="/archives"
              class="mr-4"
              v-acl-only="['manage_archive', 'view_archive']"
            >
              {{ $t("page_header.archive_mgmt") }}
            </router-link>

            <router-link
              to="/users"
              class="mr-2"
              v-acl-only="['admin', 'group_admin']"
            >
              {{ $t("page_header.user_mgmt") }}
            </router-link>

            <router-link to="/me" class="me">
              <span class="mr-2">|</span>
              <v-icon class="white--text">mdi-account-circle</v-icon>
              {{ userDisplayName }}
            </router-link>

            <router-link to="/auth/logout" class="ml-2">
              <span class="mr-2">|</span> {{ $t("page_header.logout") }}
            </router-link>
          </div>
        </div>

        <v-container
          fluid
          class="d-flex justify-space-between px-7"
          :class="{ 'py-0': isDetail }"
        >
          <div class="d-flex align-center">
            <div v-if="isDetail" class="d-flex flex-column">
              <v-btn
                class="btn-back mb-2 ml-n4"
                text
                color="white"
                small
                v-if="hasBackBtn"
                @click="onBack"
              >
                <v-icon small>mdi-arrow-left</v-icon>
                {{ $store.state.backBtnContent }}
              </v-btn>
              <div class="d-flex align-center" :class="{ 'mt-3': !hasBackBtn }">
                <v-icon class="icon-mode">{{ $store.state.pageIcon }}</v-icon>
                <div class="white--text page-header__detail__data">
                  <p class="mb-0 page-header__detail__data__title">
                    {{ headerInfo.title }}
                    <span
                      v-for="tag in headerInfo.tag"
                      :key="tag"
                      class="tag"
                      :class="{ 'px-2': headerInfo.title }"
                      :style="{ backgroundColor: headerTagColor }"
                    >
                      {{ tag }}
                    </span>
                  </p>
                  <p class="mb-0 page-header__detail__data__sub-title">
                    {{ headerInfo.subTitle }}
                  </p>
                </div>
              </div>
            </div>

            <template v-else>
              <v-icon class="icon-mode">{{ $store.state.pageIcon }}</v-icon>
            </template>
            <span v-if="!isDetail" class="ml-3 white--text">
              {{ $store.state.pageHeader }}
            </span>
          </div>

          <slot name="bottom-right"></slot>
        </v-container>
      </div>
    </div>
  </div>
</template>

<script>
import busEvent from "../BusEvent";

export default {
  name: "page-header",

  data() {
    return {
      user: null,
    };
  },

  methods: {
    onBack() {
      this.$router.push(this.$store.state.headerInfo.backUrl || -1);
    },

    getUserInfo() {
      try {
        this.user =
          localStorage.getItem("user") &&
          JSON.parse(localStorage.getItem("user"));
      } catch {
        this.user = null;
      }
    },
  },

  computed: {
    isDetail() {
      return (
        (this.$route.meta && this.$route.meta.detail) ||
        (this.$route.name && this.$route.name.includes("detail"))
      );
    },

    headerInfo() {
      return this.$store.state.headerInfo;
    },

    headerTagColor() {
      return this.$store.state.headerTagColor;
    },

    userDisplayName() {
      if (!this.user || Object.keys(this.user).length == 0) {
        return "";
      }

      if (this.user.first_name.length > 0 && this.user.last_name.length > 0) {
        return `${this.user.last_name} ${this.user.first_name}`;
      }

      return this.user.username;
    },

    hasBackBtn() {
      return (
        this.$store.state.backBtnContent &&
        this.$store.state.backBtnContent.length > 0
      );
    },
  },

  created() {
    this.getUserInfo();
    busEvent.$off("profile:refresh");
    busEvent.$on("profile:refresh", () => this.getUserInfo());
  },
};
</script>

<style lang="scss" scoped>
@import "../styles/variables";

.page-header {
  position: relative;
  min-width: 1400px;

  .page-header__content {
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

    &--center {
      width: $content-width;
      margin: auto;

      .logo-section {
        padding: 28px;
      }

      .menu a {
        color: white;
        text-decoration: none;
      }

      .btn-back {
        width: fit-content;
        font-size: 14px;
      }

      .icon-mode {
        background-color: white;
        height: 40px;
        width: 40px;
        padding: 15px;
        border-radius: 50%;
      }

      .tag {
        position: relative;
        top: -3px;
        height: 20px;
        width: fit-content;
        font-size: 10px;
        border-radius: 2px;
        margin-left: 9px;
        padding: 4px 8px;
        font-weight: bold;
      }
    }
  }

  &__detail__data {
    height: 40px;
    padding-left: 9px;

    &__title {
      position: relative;
      font-size: 20px;
      line-height: 20px;
    }

    &__sub-title {
      font-size: 14px;
      line-height: 14px;
    }
  }
}
</style>
