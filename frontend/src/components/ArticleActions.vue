<script setup lang="ts">
import { computed, onMounted, type Ref, ref } from "vue"
import { copy_link, fetch_wrapper } from "../utils"
import type { components } from "../generated/schema.js"
type Article = components["schemas"]["ArticleSerializerFull"]
type UserArticleListsSerializerFull =
  components["schemas"]["UserArticleListsSerializerFull"]

const lists: Ref<UserArticleListsSerializerFull[]> = ref([])

const host = "notizie.calomelano.it"

const props = defineProps<{
  article: Article
}>()

const is_already_saved = computed(() => {
  return lists.value.some(
    (list) => list.articles.indexOf(props.article.id) != -1,
  )
})

async function create_list_and_save(): Promise<void> {
  const name = window.prompt("Dai un nome alla tua nuova lista di articoli:")
  if (name) {
    const list = await postNewList(name)
    if (list) save(list.id)
  }
}

function save(list_id: string): void {
  addArticleToList(list_id)
}

async function addArticleToList(list_id: string): Promise<void> {
  const options = {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ article: props.article.id }),
  }
  const response = await fetch_wrapper(
    `../../api/lists/${list_id}/add_article/`,
    options,
  )
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    fetchLists()
  }
}

async function fetchLists() {
  const response = await fetch_wrapper(`../../api/lists/me/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: UserArticleListsSerializerFull[] = await response.json()
    lists.value = data
  }
}

async function postNewList(
  name: string,
): Promise<UserArticleListsSerializerFull | null> {
  const response = await fetch_wrapper(`../../api/lists/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name: name }),
  })
  if (response.status == 403) {
    document.location = "/accounts/"
    return null
  } else {
    const data: UserArticleListsSerializerFull = await response.json()
    lists.value.push(data)
    return data
  }
}

onMounted(() => {
  console.log("ArticleActions mounted")
  fetchLists()
})
</script>

<template>
  <div
    class="btn-toolbar float-start"
    role="toolbar"
    aria-label="Toolbar with button groups"
  >
    <button
      v-if="lists.length == 0"
      :id="`selected_${article.id}`"
      type="button"
      class="btn btn-outline-primary btn-sm"
      title="Salva in lista"
      @click="create_list_and_save()"
    >
      <img
        class="icon"
        src="~bootstrap-icons/icons/heart-fill.svg"
        alt="fav icon"
        width="18"
        height="18"
      />
    </button>
    <div class="dropdown" role="group" v-else>
      <button
        id="save_menu"
        class="btn btn-sm"
        :class="{
          'btn-primary': is_already_saved,
          'btn-outline-primary': !is_already_saved,
        }"
        type="button"
        data-bs-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="false"
        :title="is_already_saved ? 'Articolo già salvato' : 'Salva in lista'"
      >
        <img
          class="icon"
          src="~bootstrap-icons/icons/heart-fill.svg"
          alt="fav icon"
          width="18"
          height="18"
        />
      </button>
      <div class="dropdown-menu" aria-labelledby="save_menu">
        <div v-for="list in lists" :key="list.id">
          <a
            v-if="list.articles.indexOf(article.id) == -1"
            class="dropdown-item"
            @click="save(list.id)"
            href="#"
            tabindex="-1"
            aria-disabled="true"
            >Salva in <b>{{ list.name }}</b></a
          >
          <RouterLink
            v-else
            class="dropdown-item"
            :to="`/lists/${list.id}`"
            tabindex="-1"
            aria-disabled="true"
            >Articolo già salvato in <b>{{ list.name }}</b>
          </RouterLink>
        </div>
        <a
          class="dropdown-item"
          href="#"
          tabindex="-1"
          aria-disabled="true"
          @click="create_list_and_save()"
          >Crea una nuova lista e salva</a
        >
      </div>
    </div>
    <div class="dropdown" role="group">
      <button
        id="share_menu"
        class="btn btn-outline-success btn-sm"
        type="button"
        data-bs-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="false"
        title="Condividi"
      >
        <img
          class="icon"
          src="~bootstrap-icons/icons/share.svg"
          alt="share icon"
          width="18"
          height="18"
        />
      </button>

      <div class="dropdown-menu" aria-labelledby="share_menu">
        <a class="dropdown-item" href="#" tabindex="-1" aria-disabled="true"
          >Condividi questo articolo:</a
        >
        <a
          class="dropdown-item"
          href="#"
          title="Copia link nel clipboard"
          role="button"
          @click="copy_link(`https://${host}/article/${article.id}`)"
        >
          <img
            class="icon"
            src="~bootstrap-icons/icons/link.svg"
            alt="link icon"
            width="18"
            height="18"
          />
          <span> copia link</span>
        </a>
        <a
          class="dropdown-item"
          :href="`https://bsky.app/intent/compose?text==https%3A%2F%2F${host}%2Farticle%2F${article.id}`"
          title="Condividi con Bluesky"
          role="button"
          target="_blank"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 512 512"
            alt="bluesky icon"
            width="18"
            height="18"
          >
            <!-- Font Awesome Free 6.7.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2025 Fonticons, Inc. -->
            <path
              d="M111.8 62.2C170.2 105.9 233 194.7 256 242.4c23-47.6 85.8-136.4 144.2-180.2c42.1-31.6 110.3-56 110.3 21.8c0 15.5-8.9 130.5-14.1 149.2C478.2 298 412 314.6 353.1 304.5c102.9 17.5 129.1 75.5 72.5 133.5c-107.4 110.2-154.3-27.6-166.3-62.9l0 0c-1.7-4.9-2.6-7.8-3.3-7.8s-1.6 3-3.3 7.8l0 0c-12 35.3-59 173.1-166.3 62.9c-56.5-58-30.4-116 72.5-133.5C100 314.6 33.8 298 15.7 233.1C10.4 214.4 1.5 99.4 1.5 83.9c0-77.8 68.2-53.4 110.3-21.8z"
            />
          </svg>
          <span> bluesky</span>
        </a>
        <a
          class="dropdown-item"
          :href="`https://www.facebook.com/sharer.php?u=https%3A%2F%2F${host}%2Farticle%2F${article.id}`"
          title="Condividi con Facebook"
          role="button"
          target="_blank"
        >
          <img
            class="icon"
            src="~bootstrap-icons/icons/facebook.svg"
            alt="facebook icon"
            width="18"
            height="18"
          />
          <span> facebook</span>
        </a>
        <a
          class="dropdown-item"
          :href="`https://www.linkedin.com/shareArticle?mini=true&url=https%3A%2F%2F${host}%2Farticle%2F${article.id}`"
          title="Condividi con Linkedin"
          role="button"
          target="_blank"
        >
          <img
            class="icon"
            src="~bootstrap-icons/icons/linkedin.svg"
            alt="linkedin icon"
            width="18"
            height="18"
          />
          <span> linkedin</span>
        </a>
        <a
          class="dropdown-item"
          :href="`https://hachyderm.io/share?text=https%3A%2F%2F${host}%2Farticle%2F${article.id}`"
          title="Condividi con Mastodon"
          role="button"
          target="_blank"
        >
          <img
            class="icon"
            src="~bootstrap-icons/icons/mastodon.svg"
            alt="mastodon icon"
            width="18"
            height="18"
          />
          <span> mastodon</span>
        </a>
        <a
          class="dropdown-item"
          :href="`https://www.reddit.com/submit?url=https%3A%2F%2F${host}%2Farticle%2F${article.id}`"
          title="Condividi con Reddit"
          role="button"
          target="_blank"
        >
          <img
            class="icon"
            src="~bootstrap-icons/icons/reddit.svg"
            alt="reddit icon"
            width="18"
            height="18"
          />
          <span> reddit</span>
        </a>
        <a
          class="dropdown-item"
          :href="`https://telegram.me/share/url?url=https%3A%2F%2F${host}%2Farticle%2F${article.id}`"
          title="Condividi con Telegram"
          role="button"
          target="_blank"
        >
          <img
            class="icon"
            src="~bootstrap-icons/icons/telegram.svg"
            alt="linkedin icon"
            width="18"
            height="18"
          />
          <span> telegram</span>
        </a>
        <a
          class="dropdown-item"
          :href="`https://twitter.com/intent/tweet?url=https%3A%2F%2F${host}%2Farticle%2F${article.id}`"
          title="Condividi con Twitter"
          role="button"
          target="_blank"
        >
          <img
            class="icon"
            src="~bootstrap-icons/icons/twitter.svg"
            alt="linkedin icon"
            width="18"
            height="18"
          />
          <span> twitter</span>
        </a>
        <a
          class="dropdown-item"
          :href="`https://api.whatsapp.com/send?text=https%3A%2F%2F${host}%2Farticle%2F${article.id}`"
          title="Condividi con Whatsapp"
          role="button"
          target="_blank"
        >
          <img
            class="icon"
            src="~bootstrap-icons/icons/whatsapp.svg"
            alt="linkedin icon"
            width="18"
            height="18"
          />
          <span> whatsapp</span>
        </a>
      </div>
    </div>
  </div>
</template>
<style>
.inverted-icon {
  filter: invert(1);
}
.dimmed-icon {
  filter: invert(0.7);
}
button:hover .icon {
  filter: invert(1);
}
.green-icon {
  filter: invert(0.4) sepia(1) hue-rotate(90deg);
}
.red-icon {
  filter: invert(0.5) sepia(1) hue-rotate(300deg);
}
</style>
