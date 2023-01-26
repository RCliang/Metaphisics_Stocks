import { createRouter, createWebHashHistory } from "vue-router"

let routes = [
    { path: "/test", component: () => import("../views/Test.vue") },
    { path: "/login", component: () => import("../views/Login.vue") },
    {
        path: "/performance",
        component: () => import("../views/Performance.vue"),
        beforeEnter: (to, from, next) => {
            console.log(to);
            console.log(from);
            next()
        }
    },
]

const router = createRouter(
    {
        history: createWebHashHistory(),
        routes,
    }
);

export { router, routes };