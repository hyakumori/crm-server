<template>
  <div class="page-header">
    <v-img src="../assets/img/app-bar.png" height="169" v-if="!isDetail" />
    <v-img src="../assets/img/app-bar-detail.jpg" height="169" v-else />

    <div class="page-header__content">
      <div class="page-header__content--center">
        <div class="d-flex justify-space-between">
          <div class="logo-section">
            <img
              style="vertical-align:middle;"
              src="../assets/img/crm-logo.png"
              height="25"
            />
            <v-chip
              v-if="inMaintain"
              class="ml-2"
              color="orange"
              text-color="white"
              label
              small
              pill
            >
              <v-icon dense size="small" left>mdi-wrench</v-icon>
              MAINTENANCE
            </v-chip>
          </div>

          <div class="menu caption pa-7">
            <div
              class="menu--item"
              v-acl-only="['manage_forest', 'view_forest']"
            >
              <router-link class="f14" to="/forests">
                {{ $t("page_header.forest_mgmt") }}
              </router-link>
            </div>

            <div
              class="menu--item"
              v-acl-only="['manage_customer', 'view_customer']"
            >
              <router-link class="f14" to="/customers">
                {{ $t("page_header.customer_mgmt") }}
              </router-link>
            </div>

            <div
              class="menu--item"
              v-acl-only="['manage_archive', 'view_archive']"
            >
              <router-link class="f14" to="/archives">
                {{ $t("page_header.archive_mgmt") }}
              </router-link>
            </div>

            <div class="menu--item" v-acl-only="['admin', 'group_admin']">
              <router-link class="f14" to="/users">
                {{ $t("page_header.user_mgmt") }}
              </router-link>
            </div>

            <span class="menu--spacer f14">|</span>

            <div class="menu--item">
              <router-link to="/me" class="me">
                <v-icon class="white--text">mdi-account-circle</v-icon>
                <span class="f14">{{ userDisplayName }}</span>
              </router-link>
            </div>

            <span class="menu--spacer f14">|</span>

            <div class="menu--item">
              <router-link class="f14" to="/auth/logout">
                {{ $t("page_header.logout") }}
              </router-link>
            </div>
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
                class="btn-back ml-n4"
                text
                color="white"
                small
                v-if="hasBackBtn"
                @click="onBack"
              >
                <v-icon small>mdi-arrow-left</v-icon>
                {{ $store.state.backBtnContent }}
              </v-btn>

              <div class="d-flex align-center">
                <v-icon class="icon-mode">{{ $store.state.pageIcon }}</v-icon>
                <div
                  class="white--text page-header__detail__data"
                  :class="{
                    'default-height': isDetail,
                  }"
                >
                  <p
                    class="text-truncate page-header__detail__data__title font-weight-bold"
                    :class="{
                      'mb-2': !headerInfo.desc,
                      'mb-0': !!headerInfo.desc,
                    }"
                  >
                    {{ headerInfo.title }}
                    <span
                      v-for="(tag, index) in headerInfo.tags"
                      :key="index"
                      class="text-truncate tag"
                      :class="{ 'px-2': headerInfo.title }"
                      :style="{ backgroundColor: headerTagColor }"
                      :title="tag"
                    >
                      {{ tag }}
                    </span>
                  </p>
                  <p
                    class="caption mb-0 text-truncate page-header__detail__data__title"
                    v-if="headerInfo.desc"
                  >
                    {{ headerInfo.desc }}
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

            <span v-if="!isDetail" class="f20 fw-normal ml-3 white--text">
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
import { mapState } from "vuex";

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
    ...mapState({ inMaintain: "inMaintain" }),
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
      return this.$store.state.headerTagColor || "#12c7a6";
    },

    userDisplayName() {
      if (!this.user || Object.keys(this.user).length == 0) {
        return "";
      }

      if (this.user.full_name && this.user.full_name.length > 0) {
        return `${this.user.full_name}`;
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

      .me {
        .v-icon {
          position: relative;
          top: -1px;
        }
        span {
          margin-left: 5px;
          position: relative;
          top: -1px;
        }
      }

      .menu {
        display: flex;
        width: auto;

        &--spacer {
          color: white;
        }
        &--item {
          position: relative;
          display: block;
          margin: 0 5px;
          padding: 0 2px;
        }
        a {
          color: white;
          text-decoration: none;

          &:after {
            content: "";
            position: absolute;
            width: 100%;
            height: 1px;
            bottom: 2px;
            left: 0;
            background-color: #fff;
            transform: scaleX(0);
            transform-origin: bottom right;
            transition: transform 0.2s;
          }

          &:hover,
          &.router-link-active {
            &:after {
              transform-origin: bottom left;
              transform: scaleX(1);
            }
          }
        }
      }

      .btn-back {
        width: fit-content;
        font-size: 14px;
      }

      .icon-mode {
        background-color: #f5f5f5;
        height: 40px;
        width: 40px;
        padding: 15px;
        border-radius: 50%;
      }

      .icon-mode:before {
        color: #aaaaaa;
      }

      .tag {
        // position: relative;
        top: -3px;
        max-width: 100px;
        display: inline-block;
        font-size: 10px;
        border-radius: 2px;
        margin-left: 4px;
        padding: 3px 8px;
        font-weight: bold;
        vertical-align: text-bottom;
      }
    }
  }

  &__detail__data {
    height: 40px;
    padding-left: 9px;

    &__title {
      position: relative;
      font-size: 16px;
    }

    &__sub-title {
      font-size: 11px;
      line-height: 11px;
    }
  }
  .default-height {
    height: auto;
  }
}
</style>
