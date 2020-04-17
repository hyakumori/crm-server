import Archive from "./screens/Archive.vue";
import ArchiveDetail from "./screens/ArchiveDetail.vue";
import Customer from "./screens/Customer.vue";
import CustomerDetail from "./screens/CustomerDetail";
import DefaultLayout from "./layouts/DefaultLayout";
import Forest from "./screens/Forest.vue";
import ForestDetail from "./screens/ForestDetail";
import MainLayout from "./layouts/MainLayout";
import Vue from "vue";
import VueRouter from "vue-router";

Vue.use(VueRouter);

const UserProfileRoutes = [
  {
    path: "/me",
    name: "my-profile",
    meta: {
      title: "page_header.user_profile",
      isPublic: false,
    },
    component: MainLayout,
  },
];

const AdminRoutes = [
  {
    path: "/users",
    component: MainLayout,
    children: [
      {
        path: "",
        name: "user-management-list",
        meta: {
          title: "page_header.user_mgmt",
          isPublic: false,
          isAdmin: true,
        },
        component: () => import("./screens/UserManagementList.vue"),
      },
      {
        path: ":id",
        name: "user-management-detail",
        meta: {
          title: "page_header.user_detail",
          isPublic: false,
          isAdmin: true,
        },
        component: () => import("./screens/UserManagementDetail.vue"),
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
            scopes: ["manage_forest", "view_forest", "admin"],
          },
        },
        {
          path: "/forests/:id",
          name: "forest-detail",
          component: ForestDetail,
          meta: {
            title: "page_header.forest_detail",
            isPublic: false,
            scopes: ["manage_forest", "view_forest", "admin"],
          },
        },
        {
          path: "/customers",
          name: "customers",
          component: Customer,
          meta: {
            title: "page_header.customer_mgmt",
            isPublic: false,
            scopes: ["manage_customer", "admin"],
          },
        },
        {
          path: "/customers/:id",
          name: "customer-detail",
          component: CustomerDetail,
          props: true,
          meta: {
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
            scopes: ["manage_archive", "view_archive", "admin"],
          },
        },
        {
          path: "/archives/:id",
          name: "archive-detail",
          component: ArchiveDetail,
          meta: {
            title: "page_header.archive_detail",
            isPublic: false,
            scopes: ["manage_archive", "view_archive", "admin"],
          },
        },
      ],
    },
    ...AdminRoutes,
    ...AuthRoutes,
    ...UserProfileRoutes,
    {
      path: "*",
      name: "not-found",
      component: DefaultLayout,
      children: [
        {
          path: "",
          component: () => import("./screens/PageNotFound.vue"),
        },
      ],
    },
  ],
});

export default router;
