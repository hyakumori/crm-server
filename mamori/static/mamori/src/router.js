import Vue from 'vue';
import VueRouter from "vue-router";
import Forest from './screens/Forest.vue';

Vue.use(VueRouter)

const router = new VueRouter({
    routes: [
        {
            path: "/forests",
            component: Forest
        }
    ]
});

export default router;