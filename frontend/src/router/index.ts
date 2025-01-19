import { createRouter, createWebHistory } from "vue-router"
import ResHomeView from "../views/HomeView.vue"

const router = createRouter({
  history: createWebHistory("/res/"),
  routes: [
    {
      path: "/",
      name: "home",
      component: ResHomeView,
    },
    {
      path: "/article/:article_id",
      name: "article",
      props: true,
      component: () => import("../views/ArticleView.vue"),
    },
    {
      path: "/feeds/",
      name: "feeds",
      props: true,
      component: () => import("../views/FeedsView.vue"),
    },
    {
      path: "/new_article/",
      name: "new_article",
      props: true,
      component: () => import("../views/NewArticle.vue"),
    },
    {
      path: "/feed/:feed_id",
      name: "feed",
      props: true,
      component: () => import("../views/FeedView.vue"),
    },
    {
      path: "/author/:author",
      name: "author",
      props: true,
      component: () => import("../views/AuthorView.vue"),
    },
  ],
})

export default router
