import { createRouter, createWebHistory } from "vue-router"

import { useAuthStore } from "../stores/auth.store"

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
      path: "/edit_article/:article_id",
      name: "edit_article",
      props: true,
      component: () => import("../views/ArticleEdit.vue"),
      meta: { requiresAdmin: true },
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
      path: "/lists/:list_id",
      name: "lists-id",
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
      path: "/edit_feed/:feed_id",
      name: "edit_feed",
      props: true,
      component: () => import("../views/FeedEdit.vue"),
      meta: { requiresAdmin: true },
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
  if (to.matched.some((record) => record.meta.requiresAdmin)) {
    const auth = useAuthStore()
    if (!auth.user?.is_staff) {
      alert("Funzione riservata agli utenti di staff")
      return
    }
  }
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
