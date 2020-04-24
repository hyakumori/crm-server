<template>
  <main-section class="account-profile">
    <template #section>
      <v-content>
        <v-container grid-list-xs class="main-container">
          <ValidationObserver v-slot="{ invalid }">
            <div class="account-profile__section px-7">
              <div id="basic-info">
                <content-header
                  content="基本情報 (登記情報)"
                  editBtnContent="基本情報・編集"
                  :loading="basicInfo.length === 0 || isLoading"
                  :update="isUpdate.basicInfo"
                  @update="val => (isUpdate.basicInfo = val)"
                />
                <div class="my-4">
                  <v-row v-if="errors">
                    <v-col cols="12">
                      <v-alert
                        dense
                        outlined
                        type="error"
                        v-for="error in errors"
                        :key="error.loc"
                      >
                        {{ error.message }}
                      </v-alert>
                    </v-col>
                  </v-row>
                  <v-row>
                    <template v-for="(info, index) in basicInfo">
                      <v-col cols="6" :key="index">
                        <text-info
                          v-if="!info.type || info.type === 'text'"
                          :label="info.label"
                          :rules="info.rules"
                          :name="info.name"
                          v-model="form[info.key]"
                          :isUpdate="isUpdate.basicInfo && !info.disabled"
                        />
                        <select-info
                          v-if="info.type && info.type === 'select'"
                          :items="info.items"
                          :label="info.label"
                          v-model="form[info.key]"
                          :isUpdate="isUpdate.basicInfo && !info.disabled"
                        />
                      </v-col>
                    </template>
                  </v-row>

                  <update-button
                    class="mb-12"
                    :disabled="invalid || isLoading"
                    :save="onSave"
                    v-if="isUpdate.basicInfo"
                    :cancel="cancel.bind(this, 'basicInfo')"
                  />
                </div>
              </div>
            </div>
          </ValidationObserver>
        </v-container>
      </v-content>
    </template>
  </main-section>
</template>

<script>
import { ValidationObserver } from "vee-validate";
import MainSection from "../components/MainSection";
import ScreenMixin from "./ScreenMixin";
import ContentHeader from "../components/detail/ContentHeader";
import actionLogs from "../assets/dump/action_log.json";
import UpdateButton from "../components/detail/UpdateButton";
import TextInfo from "../components/detail/TextInfo";
import SelectInfo from "../components/detail/SelectInfo";
import busEvent from "../BusEvent";

import { fromNow } from "../helpers/datetime";

export default {
  name: "account-profile",

  mixins: [ScreenMixin],

  components: {
    TextInfo,
    SelectInfo,
    MainSection,
    ContentHeader,
    ValidationObserver,
    UpdateButton,
  },

  data() {
    return {
      userId: this.$route.params.id,
      userInfo: null,
      pageIcon: this.$t("icon.user_icon"),
      backBtnContent: this.$t("page_header.user_mgmt"),
      userPermissions: {},
      form: {
        last_name: "",
        first_name: "",
        group: "",
        username: "",
        email: "",
        is_active: false,
      },
      isLoading: false,
      isUpdate: {
        basicInfo: false,
      },
      errors: [],
    };
  },

  async mounted() {
    this.isLoading = true;
    await this.getUserDetail();
    await this.getUserPermission();
    await this.setHeaderInfo();
    this.isLoading = false;
  },

  methods: {
    async getUserPermission(callback) {
      const response = await this.$rest.get(
        `/users/${this.userInfo && this.userInfo.id}/permissions`,
      );
      if (response) {
        this.userPermissions = response;
        if (callback) {
          callback(response);
        }
      }
    },

    async getUserDetail() {
      const response = await this.$rest.get(`/users/me`);
      if (response) {
        this.userInfo = response;
      }
    },

    expandDiscussionList() {
      this.isExpand = !this.isExpand;
    },

    parseErrors(errors) {
      /**
       * {
            "email": [
              "Email existed"
            ],
            "username": [
              "Username existed"
            ]
          }
       */

      let formatedErrors = [];
      Object.keys(errors).forEach(errorKey => {
        formatedErrors.push({
          loc: errorKey,
          message: errors[errorKey].join(", "),
        });
      });

      return formatedErrors;
    },

    async onSave() {
      try {
        this.isLoading = true;
        const response = await this.$rest.put(`/users/me`, {
          ...this.form,
        });
        if (response) {
          await this.getUserPermission();
          this.userInfo = response;
          localStorage.setItem("user", JSON.stringify(this.userInfo));

          busEvent.$emit("profile:refresh");

          setTimeout(() => {
            this.isUpdate.basicInfo = false;
          }, 300);
        }
      } catch (e) {
        this.errors = this.parseErrors(e.response.data);
      } finally {
        setTimeout(() => {
          this.isLoading = false;
        }, 300);
      }
    },

    cancel(val) {
      this.isUpdate[val] = false;
      this.buildBasicInfo();
      this.errors = [];
    },

    setHeaderInfo() {
      const fromNowText = fromNow(this.userInfo.last_login);
      const info = {
        title: this.userInfo.username,
        subTitle:
          fromNowText &&
          `${this.$t(
            "user_management.tables.headers.last_login",
          )} ${fromNowText}`,
      };
      this.$store.dispatch("setHeaderInfo", info);
      this.$store.dispatch("setBackBtnContent", "");
    },

    fallbackText(text) {
      return text || "";
    },

    copyToForm(basicInfo) {
      Object.keys(this.form).forEach(
        key =>
          (this.form[key] = basicInfo.find(item => item.key === key).value),
      );
    },

    mapUserPermissions() {
      if (this.userPermissions && this.userPermissions.groups) {
        return (
          this.userPermissions.groups.map(group => ({
            text: group.name,
            value: group.id,
          }))[0].text || {}
        );
      }
    },

    buildBasicInfo() {
      let basicInfo = [];
      const userInfo = this.userInfo;
      const groups = this.groups;

      if (userInfo) {
        basicInfo = [
          {
            key: "last_name",
            label: this.$t("user_management.tables.headers.last_name"),
            value: userInfo.last_name,
            rules: "required",
            name: "user_management.tables.headers.last_name",
          },
          {
            key: "first_name",
            label: this.$t("user_management.tables.headers.first_name"),
            value: userInfo.first_name,
            rules: "required",
            name: "user_management.tables.headers.first_name",
          },
          {
            key: "username",
            label: this.$t("user_management.tables.headers.username"),
            value: userInfo.username,
            rules: "required",
            disabled: true,
            name: "user_management.tables.headers.username",
          },
          {
            key: "email",
            label: this.$t("user_management.tables.headers.email"),
            value: userInfo.email,
            rules: "required|email",
            disabled: true,
            name: "user_management.tables.headers.email",
          },
          {
            key: "group",
            label: this.$t("user_management.tables.headers.roles"),
            value: this.mapUserPermissions(),
            disabled: true,
          },
          {
            key: "is_active",
            label: this.$t("user_management.tables.headers.status"),
            value: userInfo.is_active
              ? this.$t("enums.user_status.active")
              : this.$t("enums.user_status.inactive"),
            disabled: true,
          },
        ];
        this.copyToForm(basicInfo);
      }

      return basicInfo;
    },
  },

  computed: {
    basicInfo() {
      return this.buildBasicInfo();
    },

    getActionLogs() {
      return actionLogs;
    },
  },
};
</script>

<style lang="scss" scoped>
@import "../styles/variables";

.account-profile {
  &__section {
    @extend %detail-section-shared;
    width: auto;
  }

  &__expand {
    margin-top: 20px;
    margin-bottom: 50px;
    width: fit-content;
    font-size: 14px;
    color: #999999;

    &:hover {
      cursor: pointer;
    }
  }

  &__header {
    &--text {
      display: flex;
      justify-content: center;
      font-size: 14px;
      color: #444444;
      font-weight: bold;

      &__data--color {
        color: #579513;
      }
    }
  }
  .main-container {
    max-width: 974px;
  }
}
</style>
