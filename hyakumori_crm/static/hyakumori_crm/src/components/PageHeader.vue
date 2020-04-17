<template>
  <div class="page-header">
    <v-img :src="getAppBar" :height="isDetail ? 169 : 151"></v-img>

    <div class="page-header__content">
      <div class="page-header__content--center">
        <div class="d-flex justify-space-between">
          <div class="logo-section">
            <img
              src="../assets/img/logo.webp"
              alt="Logo big text"
              height="18"
            />

            <img
              class="ml-3"
              src="../assets/img/crm.webp"
              alt="Logo small text"
              height="12"
            />
          </div>

          <div class="menu caption pa-7">
            <router-link to="/forests">{{
              $t("page_header.forest_info_list")
            }}</router-link>

            <router-link to="/customers" class="ml-4 mr-4">{{
              $t("page_header.customer_list")
            }}</router-link>

            <router-link to="/archives" class="mr-4">{{
              $t("page_header.archive_list")
            }}</router-link>

            <router-link to="/settings">{{
              $t("page_header.setting")
            }}</router-link>
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
                @click="onBack"
                ><v-icon small>mdi-arrow-left</v-icon
                >{{ $store.state.backBtnContent }}</v-btn
              >
              <div class="d-flex align-center">
                <v-icon class="icon-mode">{{ $store.state.pageIcon }}</v-icon>
                <div class="white--text body-2 pl-2">
                  <p class="mb-0">
                    {{ headerInfo.title }}<span
                      class="tag"
                      :class="{'px-2 py-1': headerInfo.title}"
                      :style="{ backgroundColor: headerTagColor }"
                      >{{ headerInfo.tag }}</span
                    >
                  </p>
                  <p class="mb-0 caption">{{ headerInfo.subTitle }}</p>
                </div>
              </div>
            </div>
            <template v-else>
              <v-icon class="icon-mode">{{ $store.state.pageIcon }}</v-icon>
            </template>
            <span v-if="!isDetail" class="ml-3 white--text">{{
              $store.state.pageHeader
            }}</span>
          </div>
          <outline-round-btn
            class="align-self-center"
            v-if="$route.name === 'customer-detail'"
            :icon="$t('icon.add')"
            :content="$t('buttons.add_customer')"
          />
          <CustomerCreateForm v-if="$route.name === 'customers'" />
        </v-container>
      </div>
    </div>
  </div>
</template>

<script>
import CustomerCreateForm from "./CustomerCreateForm";
import AppBarImg from "../assets/img/app-bar.webp";
import AppBarDetailImg from "../assets/img/app-bar-detail.webp";
import OutlineRoundBtn from "./OutlineRoundBtn";

export default {
  name: "page-header",

  components: {
    CustomerCreateForm,
    OutlineRoundBtn,
  },

  methods: {
    onBack() {
      this.$router.go(-1);
    },
  },

  computed: {
    isDetail() {
      return this.$route.name && this.$route.name.includes("detail");
    },

    getAppBar() {
      return this.isDetail ? AppBarDetailImg : AppBarImg;
    },

    headerInfo() {
      return this.$store.state.headerInfo;
    },

    headerTagColor() {
      return this.$store.state.headerTagColor;
    },
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
      }

      .icon-mode {
        background-color: white;
        height: 40px;
        width: 40px;
        padding: 15px;
        border-radius: 50%;
      }

      .tag {
        font-size: 10px;
        font-weight: bold;
        border-radius: 2px;
        margin-left: 8px;
        margin-bottom: -4px;
      }
    }
  }
}
</style>
