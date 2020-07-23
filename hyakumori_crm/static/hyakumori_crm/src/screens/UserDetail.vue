<template>
  <main-section class="user-detail">
    <template #section>
      <div class="user-detail__section px-7">
        <div id="basic-info">
          <content-header
            content="基本情報"
            toggleEditBtnContent="編集"
            :loading="basicInfo.length === 0 || isLoading"
            @toggleEdit="val => (isUpdate.basicInfo = val)"
          />
          <div class="my-4">
            <ValidationObserver v-slot="{ invalid }">
              <v-row v-if="errors.length > 0">
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
                      :isUpdate="isUpdate.basicInfo"
                    />
                    <select-info
                      v-if="info.type && info.type === 'select'"
                      :items="info.items"
                      :label="info.label"
                      v-model="form[info.key]"
                      :isUpdate="isUpdate.basicInfo"
                    />
                  </v-col>
                </template>
              </v-row>

              <update-button
                class="mb-12"
                :saveDisabled="invalid || isLoading"
                :save="onSave"
                v-if="isUpdate.basicInfo"
                :cancel="cancel.bind(this, 'basicInfo')"
              />
            </ValidationObserver>
          </div>
        </div>
      </div>
    </template>

    <template #right>
      <action-log
        app-name="users"
        object-type="user"
        :object-id="$route.params.id"
      ></action-log>
    </template>
  </main-section>
</template>

<script>
import { ValidationObserver } from "vee-validate";
import MainSection from "../components/MainSection";
import ScreenMixin from "./ScreenMixin";
import ContentHeader from "../components/detail/ContentHeader";
import UpdateButton from "../components/detail/UpdateButton";
import TextInfo from "../components/detail/TextInfo";
import SelectInfo from "../components/detail/SelectInfo";
import ActionLog from "../components/detail/ActionLog";

import { fromNow } from "../helpers/datetime";
import busEvent from "../BusEvent";

export default {
  name: "user-detail",

  mixins: [ScreenMixin],

  components: {
    TextInfo,
    SelectInfo,
    MainSection,
    ContentHeader,
    ActionLog,
    ValidationObserver,
    UpdateButton,
  },

  data() {
    return {
      userId: this.$route.params.id,
      userInfo: null,
      pageIcon: this.$t("icon.user_icon"),
      backBtnContent: this.$t("page_header.user_mgmt"),
      groups: [],
      userPermissions: {},
      form: {
        last_name: "",
        first_name: "",
        username: "",
        group: "",
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
    await this.getGroups();
    await this.getUserPermission();
    await this.getUserDetail();
    await this.setHeaderInfo();
    this.isLoading = false;
  },

  methods: {
    async getUserPermission(callback) {
      const response = await this.$rest.get(
        `/users/${this.$route.params.id}/permissions`,
      );
      if (response) {
        this.userPermissions = response;
        if (callback) {
          callback(response);
        }
      }
    },

    async getGroups() {
      const response = await this.$rest.get(`/permissions/groups`);
      if (response) {
        this.groups = response.groups.map(item => ({
          text: item.name,
          value: item.id,
        }));
      }
    },

    async getUserDetail() {
      const response = await this.$rest.get(`/users/${this.$route.params.id}`);
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

    syncUserProfileInfo() {
      try {
        const userProfile = JSON.parse(localStorage.getItem("user"));
        if (this.userInfo.id === userProfile.id) {
          localStorage.setItem("user", JSON.stringify(this.userInfo));
          busEvent.$emit("profile:refresh");
        }
      } catch {}
    },
    async onSave() {
      try {
        this.isLoading = true;
        const response = await this.$rest.put(
          `/users/${this.$route.params.id}`,
          { ...this.form, is_active: this.form.is_active.value },
        );
        if (response) {
          await this.getUserPermission();
          this.userInfo = response;
          this.setHeaderInfo();
          this.syncUserProfileInfo();

          setTimeout(() => {
            this.isUpdate.basicInfo = false;
            this.errors = [];
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
        backUrl: "/users",
      };

      this.$store.dispatch("setHeaderInfo", info);
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
          }))[0] || {}
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
            name: "user_management.tables.headers.username",
          },
          {
            key: "email",
            label: this.$t("user_management.tables.headers.email"),
            value: userInfo.email,
            rules: "required|email",
            name: "user_management.tables.headers.email",
          },
          {
            key: "group",
            label: this.$t("user_management.tables.headers.roles"),
            value: this.mapUserPermissions(),
            type: "select",
            items: groups,
          },
          {
            key: "is_active",
            label: this.$t("user_management.tables.headers.status"),
            value: {
              value: userInfo.is_active === true,
              text: userInfo.is_active
                ? this.$t("enums.user_status.active")
                : this.$t("enums.user_status.inactive"),
            },
            type: "select",
            items: [
              { value: true, text: this.$t("enums.user_status.active") },
              { value: false, text: this.$t("enums.user_status.inactive") },
            ],
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

.user-detail {
  &__section {
    @extend %detail-section-shared;
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
}
</style>
