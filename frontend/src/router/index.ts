import { createRouter, createWebHistory } from "vue-router"

const router = createRouter({
  history: createWebHistory("/res/"),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("../views/HomeView.vue"),
      meta: {
        title: "Home",
      },
    },
    {
      path: "/article/:article_id",
      name: "article",
      props: true,
      component: () => import("../views/ArticleView.vue"),
    },
    {
      path: "/lists/",
      name: "lists",
      props: true,
      component: () => import("../views/ListsView.vue"),
      meta: {
        title: "Liste",
      },
    },
    {
      path: "/read/",
      name: "read",
      props: true,
      component: () => import("../views/ReadView.vue"),
      meta: {
        title: "Letti",
      },
    },
    {
      path: "/feeds/",
      name: "feeds",
      props: true,
      component: () => import("../views/FeedsView.vue"),
      meta: {
        title: "Fonti",
      },
    },
    {
      path: "/new_article/",
      name: "new_article",
      props: true,
      component: () => import("../views/NewArticle.vue"),
      meta: {
        title: "Nuovo articolo",
      },
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
    {
      path: "/settings/",
      name: "settings",
      props: true,
      component: () => import("../views/SettingsView.vue"),
      meta: {
        title: "Impostazioni",
      },
    },
  ],
})

router.beforeEach((to, from, next) => {
  if (to.params.article_id) {
    document.title = `Articolo ${to.params.article_id} - Flash`
  } else if (to.params.feed_id) {
    document.title = `Fonte ${to.params.feed_id} - Flash`
  } else if (to.params.author) {
    document.title = `Autore ${to.params.author} - Flash`
  } else {
    document.title = `${to.meta?.title ?? ""} - Flash`
  }
  next()
})

export default router
