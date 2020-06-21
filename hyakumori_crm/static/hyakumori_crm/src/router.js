import Archive from "./screens/Archive.vue";
import ArchiveDetail from "./screens/ArchiveDetail.vue";
import Customer from "./screens/Customer.vue";
import CustomerDetail from "./screens/CustomerDetail";
import DefaultLayout from "./layouts/DefaultLayout";
import Forest from "./screens/Forest.vue";
import ForestDetail from "./screens/ForestDetail";
import MainLayout from "./layouts/MainLayout";
import PostalHistory from "./screens/PostalHistory/PostalHistory.vue";
import PostalHistoryDetail from "./screens/PostalHistory/PostalHistoryDetail.vue";

import Vue from "vue";
import VueRouter from "vue-router";

Vue.use(VueRouter);

const UserProfileRoutes = [
  {
    path: "/me",
    component: MainLayout,
    children: [
      {
        path: "",
        name: "my-profile",
        meta: {
          title: "page_header.user_profile",
          isPublic: false,
          detail: true,
        },
        component: () => import("./screens/AccountProfile.vue"),
      },
    ],
  },
];

const AdminRoutes = [
  {
    path: "/users",
    component: MainLayout,
    children: [
      {
        path: "",
        name: "user-list",
        meta: {
          title: "page_header.user_mgmt",
          isPublic: false,
          scopes: ["group_admin"],
        },
        component: () => import("./screens/UserList.vue"),
      },
      {
        path: ":id",
        name: "user-detail",
        meta: {
          title: "page_header.user_detail",
          isPublic: false,
          scopes: ["group_admin"],
        },
        component: () => import("./screens/UserDetail.vue"),
      },
    ],
  },
];

const AuthRoutes = [
  {
    path: "/auth",
    component: DefaultLayout,
    children: [
      {
        path: "",
        redirect: {
          name: "auth-login",
        },
      },
      {
        path: "login",
        name: "auth-login",
        meta: {
          title: "page_header.login",
          isPublic: true,
        },
        component: () => import("./screens/AuthLogin.vue"),
      },
      {
        path: "logout",
        name: "auth-logout",
        meta: {
          title: "page_header.logout",
          isPublic: false,
        },
        component: () => import("./screens/AuthLogout.vue"),
      },
      {
        path: "forgot-password",
        name: "auth-forgot-password",
        meta: {
          title: "page_header.forgot_password",
          isPublic: true,
        },
        component: () => import("./screens/AuthResetPassword.vue"),
      },
      {
        path: "reset-password/:uid/:token",
        name: "auth-reset-password",
        meta: {
          title: "page_header.forgot_password",
          isPublic: true,
        },
        component: () => import("./screens/AuthResetPasswordConfirm.vue"),
      },
      {
        path: "activate/:uid/:token",
        name: "auth-activate",
        meta: {
          title: "page_header.activate_account",
          isPublic: true,
        },
        component: () => import("./screens/AuthActivation.vue"),
      },
      {
        path: "no-permission",
        name: "error-403",
        meta: {
          title: "page_header.no_permission",
          isPublic: true,
        },
        component: () => import("./screens/AuthInsufficientPermission.vue"),
      },
    ],
  },
];

const router = new VueRouter({
  mode: "history",
  routes: [
    {
      path: "",
      component: MainLayout,
      children: [
        {
          path: "",
          meta: {
            isPublic: false,
          },
          redirect: { name: "forests" },
        },
        {
          path: "/forests",
          name: "forests",
          component: Forest,
          meta: {
            title: "page_header.forest_mgmt",
            isPublic: false,
            scopes: ["manage_forest", "view_forest"],
          },
        },
        {
          path: "/forests/:id",
          name: "forest-detail",
          component: ForestDetail,
          props: true,
          meta: {
            title: "page_header.forest_detail",
            isPublic: false,
            scopes: ["manage_forest", "view_forest"],
          },
        },
        {
          path: "/customers",
          name: "customers",
          component: Customer,
          meta: {
            title: "page_header.customer_mgmt",
            isPublic: false,
            scopes: ["manage_customer", "view_customer"],
          },
        },
        {
          path: "/customers/new",
          name: "customer-new",
          component: CustomerDetail,
          meta: {
            detail: true,
            title: "page_header.customer_new",
            isPublic: false,
            scopes: ["manage_customer", "add_customer"],
          },
        },
        {
          path: "/customers/:id",
          name: "customer-detail",
          component: CustomerDetail,
          props: true,
          meta: {
            detail: true,
            title: "page_header.customer_detail",
            isPublic: false,
            scopes: ["manage_customer", "view_customer", "admin"],
          },
        },
        {
          path: "/archives",
          name: "archives",
          component: Archive,
          meta: {
            title: "page_header.archive_mgmt",
            isPublic: false,
            scopes: ["manage_archive", "view_archive"],
          },
        },
        {
          path: "/archives/new",
          name: "archive-new",
          component: ArchiveDetail,
          meta: {
            detail: true,
            title: "page_header.archive_new",
            isPublic: false,
            scopes: ["manage_archive"],
          },
        },
        {
          path: "/archives/:id",
          name: "archive-detail",
          component: ArchiveDetail,
          meta: {
            detail: true,
            title: "page_header.archive_detail",
            isPublic: false,
            scopes: ["manage_archive", "view_archive"],
          },
        },
        {
          path: "/postal-histories",
          name: "postalHistories",
          component: PostalHistory,
          meta: {
            title: "page_header.postalhistory_mgmt",
            isPublic: false,
            scopes: ["manage_postalhistory", "view_postalhistory"],
          },
        },
        {
          path: "/postal-histories/new",
          name: "postalHistoryNew",
          component: PostalHistoryDetail,
          meta: {
            detail: true,
            title: "page_header.postalhistory_new",
            isPublic: false,
            scopes: ["manage_postalhistory"],
          },
        },
        {
          path: "/postal-histories/:id",
          name: "postalHistoryDetail",
          component: PostalHistoryDetail,
          meta: {
            detail: true,
            title: "page_header.postalhistory_detail",
            isPublic: false,
            scopes: ["manage_postalhistory", "view_postalhistory"],
          },
        },
      ],
    },
    ...AdminRoutes,
    ...AuthRoutes,
    ...UserProfileRoutes,
    {
      path: "/not-found",
      component: DefaultLayout,
      children: [
        {
          path: "",
          name: "not-found",
          meta: {
            title: "page_header.not_found",
            isPublic: true,
          },
          component: () => import("./screens/PageNotFound.vue"),
        },
      ],
    },
    {
      path: "/slack/oauth",
      component: DefaultLayout,
      children: [
        {
          path: "",
          name: "slack-oauth",
          meta: {
            title: "Slack Oauth",
            isPublic: true,
          },
          component: () => import("./screens/Slack/Oauth.vue"),
        },
      ],
    },
    {
      path: "*",
      redirect: { name: "not-found" },
    },
  ],
});

// Override for processing NavigationDuplicated exception
const originalPush = VueRouter.prototype.push;
VueRouter.prototype.push = function push(location) {
  return originalPush.call(this, location).catch(err => err);
};

export default router;
