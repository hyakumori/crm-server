import Archive from "./screens/Archive.vue";
import AuthLayout from "./components/AuthLayout.vue";
import Customer from "./screens/Customer.vue";
import Forest from "./screens/Forest.vue";
import ForestDetail from "./screens/ForestDetail";
import CustomerDetail from "./screens/CustomerDetail";
import Vue from "vue";
import VueRouter from "vue-router";

Vue.use(VueRouter);

const UserProfileRoutes = [
  {
    path: "/me",
    name: "my-profile",
    component: AuthLayout,
  },
];

const AdminRoutes = [
  {
    path: "/users",
    name: "user-management-list",
    meta: {
      isAdmin: true,
    },
    component: () => import("./screens/UserManagementList.vue"),
  },
  {
    path: "/users/:id",
    name: "user-management-detail",
    meta: {
      isAdmin: true,
    },
    component: () => import("./screens/UserManagementDetail.vue"),
  },
];

const AuthRoutes = [
  {
    path: "/auth",
    component: AuthLayout,
    children: [
      {
        path: "login",
        name: "auth-login",
        meta: {
          isPublic: true,
        },
        component: () => import("./screens/AuthLogin.vue"),
      },
      {
        path: "forgot-password",
        name: "auth-forgot-password",
        meta: {
          isPublic: true,
        },
        component: () => import("./screens/AuthResetPassword.vue"),
      },
      {
        path: "reset-password/:uid/:token",
        name: "auth-reset-password",
        meta: {
          isPublic: true,
        },
        component: () => import("./screens/AuthResetPasswordConfirm.vue"),
      },
      {
        path: "no-permission",
        name: "error-403",
        meta: {
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
      path: "/forests",
      name: "forests",
      component: Forest,
      meta: {
        isPublic: false,
        scopes: ["manage_forest", "view_forest"],
      },
    },
    {
      path: "/forests/:id",
      name: "forest-detail",
      component: ForestDetail,
      meta: {
        isPublic: false,
        scopes: ["manage_forest", "view_forest"],
      },
    },
    {
      path: "/customers",
      name: "customers",
      component: Customer,
      meta: {
        isPublic: false,
        scopes: ["manage_customer"],
      },
    },
    {
      path: "/customers/:id",
      name: "customer-detail",
      component: CustomerDetail,
      props: true,
    },
    {
      path: "/archives",
      name: "archives",
      component: Archive,
      meta: {
        isPublic: false,
        scopes: ["manage_archive"],
      },
    },
    ...AdminRoutes,
    ...AuthRoutes,
    ...UserProfileRoutes,
    {
      path: "*",
      name: "not-found",
      component: () => import("./screens/PageNotFound.vue"),
    },
  ],
});

export default router;
