<template>
  <div
    class="btn-group btn-group-sm"
    role="group"
    aria-label="translate download send share edit"
  >
    <button
      v-if="translatable"
      id="translate"
      class="btn btn-secondary"
      type="button"
      title="Traduci"
      @click="translate()"
    >
      <img
        class="inverted-icon icon"
        src="~bootstrap-icons/icons/globe.svg"
        alt="globe icon"
        width="18"
        height="18"
      />
    </button>
    <div class="dropdown btn-group btn-group-sm" role="group">
      <button
        id="download_menu"
        class="btn btn-primary"
        type="button"
        data-bs-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="false"
        title="Scarica"
      >
        <img
          class="inverted-icon icon"
          src="~bootstrap-icons/icons/download.svg"
          alt="download icon"
          width="18"
          height="18"
        />
      </button>
      <div class="dropdown-menu" aria-labelledby="download_menu">
        <a
          class="dropdown-item disabled"
          href="#"
          tabindex="-1"
          aria-disabled="true"
          >Scarica nel formato che perferisci:</a
        >
        <button
          type="button"
          class="dropdown-item btn-primary"
          title="Scarica in formato html"
          @click="window_open('/api/articles.html?ids=' + ids)"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/filetype-html.svg"
            alt="html icon"
            width="18"
            height="18"
          />
          <span> html</span>
        </button>
        <button
          type="button"
          class="dropdown-item btn-primary"
          title="Scarica come ebook in formato epub"
          @click="window_open('/api/articles.epub?ids=' + ids)"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/book.svg"
            alt="book icon"
            width="18"
            height="18"
          />
          <span> epub</span>
        </button>
        <button
          type="button"
          class="dropdown-item btn-primary"
          title="Scarica come ebook in formato amazon kindle"
          @click="window_open('/api/articles.mobi?ids=' + ids)"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/amazon.svg"
            alt="amazon icon"
            width="18"
            height="18"
          />
          <span> mobi</span>
        </button>
        <button
          type="button"
          class="dropdown-item btn-primary"
          title="Scarica come ebook in formato pdf"
          @click="window_open('/articles_pdf.php?ids=' + ids)"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/filetype-pdf.svg"
            alt="pdf icon"
            width="18"
            height="18"
          />
          <span> pdf</span>
        </button>
        <button
          type="button"
          class="dropdown-item btn-primary"
          title="Scarica in formato testo"
          @click="window_open('/api/articles.txt?ids=' + ids)"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/justify.svg"
            alt="text icon"
            width="18"
            height="18"
          />
          <span> txt</span>
        </button>
      </div>
    </div>
    <!-- download dropdown -->
    <div class="dropdown btn-group btn-group-sm" role="group">
      <button
        id="send_menu"
        class="btn btn-info"
        type="button"
        data-bs-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="false"
        title="Invia per e-mail"
      >
        <img
          class="inverted-icon icon"
          src="~bootstrap-icons/icons/envelope.svg"
          alt="email icon"
          width="18"
          height="18"
        />
      </button>
      <div class="dropdown-menu" aria-labelledby="send_menu">
        <a
          v-if="user"
          class="dropdown-item disabled"
          href="#"
          tabindex="-1"
          aria-disabled="true"
          >Invia per e-mail a {{ user.email }} nel formato che preferisci:</a
        >
        <button
          type="button"
          class="dropdown-item btn-info"
          title="Invia per e-mail in formato html"
          @click="email('html')"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/filetype-html.svg"
            alt="html icon"
            width="18"
            height="18"
          />
          <span> html</span>
        </button>
        <button
          type="button"
          class="dropdown-item btn-info"
          title="Invia per e-mail come ebook in formato epub"
          @click="email('epub')"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/book.svg"
            alt="book icon"
            width="18"
            height="18"
          />
          <span> epub</span>
        </button>
        <button
          type="button"
          class="dropdown-item btn-info"
          title="Invia per e-mail come ebook in formato amazon kindle"
          @click="email('mobi')"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/amazon.svg"
            alt="amazon icon"
            width="18"
            height="18"
          />
          <span> mobi</span>
        </button>
        <button
          type="button"
          class="dropdown-item btn-info"
          title="Invia per e-mail come ebook in formato pdf"
          @click="email('pdf')"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/filetype-pdf.svg"
            alt="pdf icon"
            width="18"
            height="18"
          />
          <span> pdf</span>
        </button>
        <button
          type="button"
          class="dropdown-item btn-info"
          title="Invia per e-mail in formato testo"
          @click="email('txt')"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/justify.svg"
            alt="text icon"
            width="18"
            height="18"
          />
          <span> txt</span>
        </button>
      </div>
    </div>
    <!-- email dropdown -->
    <div v-show="share" class="dropdown btn-group btn-group-sm" role="group">
      <button
        id="share_menu"
        class="btn btn-danger"
        type="button"
        data-bs-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="false"
        title="Condividi"
      >
        <img
          class="inverted-icon icon"
          src="~bootstrap-icons/icons/share.svg"
          alt="share icon"
          width="18"
          height="18"
        />
      </button>
      <div class="dropdown-menu" aria-labelledby="share_menu">
        <a
          class="dropdown-item disabled"
          href="#"
          tabindex="-1"
          aria-disabled="true"
          >Condividi questo articolo:</a
        >
        <a
          class="dropdown-item btn-danger"
          href="#"
          title="Copia link nel clipboard"
          role="button"
          @click="copy_link()"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/link.svg"
            alt="link icon"
            width="18"
            height="18"
          />
          <span> copia link</span>
        </a>
        <a
          class="dropdown-item btn-danger"
          :href="`https://www.facebook.com/sharer.php?u=https%3A%2F%2F${host}%2Farticle%2F${ids}`"
          title="Condividi con Facebook"
          role="button"
          target="_blank"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/facebook.svg"
            alt="facebook icon"
            width="18"
            height="18"
          />
          <span> facebook</span>
        </a>
        <a
          class="dropdown-item btn-danger"
          :href="`https://www.linkedin.com/shareArticle?mini=true&url=https%3A%2F%2F${host}%2Farticle%2F${ids}`"
          title="Condividi con Linkedin"
          role="button"
          target="_blank"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/linkedin.svg"
            alt="linkedin icon"
            width="18"
            height="18"
          />
          <span> linkedin</span>
        </a>
        <a
          class="dropdown-item btn-danger"
          :href="`https://mastodon.social/share?text=https%3A%2F%2F${host}%2Farticle%2F${ids}`"
          title="Condividi con Mastodon"
          role="button"
          target="_blank"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/mastodon.svg"
            alt="mastodon icon"
            width="18"
            height="18"
          />
          <span> mastodon</span>
        </a>
        <a
          class="dropdown-item btn-danger"
          :href="`https://www.reddit.com/submit?url=https%3A%2F%2F${host}%2Farticle%2F${ids}`"
          title="Condividi con Reddit"
          role="button"
          target="_blank"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/reddit.svg"
            alt="reddit icon"
            width="18"
            height="18"
          />
          <span> reddit</span>
        </a>
        <a
          class="dropdown-item btn-danger"
          :href="`https://telegram.me/share/url?url=https%3A%2F%2F${host}%2Farticle%2F${ids}`"
          title="Condividi con Telegram"
          role="button"
          target="_blank"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/telegram.svg"
            alt="linkedin icon"
            width="18"
            height="18"
          />
          <span> telegram</span>
        </a>
        <a
          class="dropdown-item btn-danger"
          :href="`https://twitter.com/intent/tweet?url=https%3A%2F%2F${host}%2Farticle%2F${ids}`"
          title="Condividi con Twitter"
          role="button"
          target="_blank"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/twitter.svg"
            alt="linkedin icon"
            width="18"
            height="18"
          />
          <span> twitter</span>
        </a>
        <a
          class="dropdown-item btn-danger"
          :href="`https://api.whatsapp.com/send?text=https%3A%2F%2F${host}%2Farticle%2F${ids}`"
          title="Condividi con Whatsapp"
          role="button"
          target="_blank"
        >
          <img
            class="inverted-icon icon"
            src="~bootstrap-icons/icons/whatsapp.svg"
            alt="linkedin icon"
            width="18"
            height="18"
          />
          <span> whatsapp</span>
        </a>
      </div>
    </div>
    <!-- share dropdown -->
    <a
      v-if="share && user && user.groups.indexOf('staff') != -1"
      id="edit_menu"
      :href="'/edit_article.php?id=' + ids"
      class="btn btn-warning"
      role="button"
      aria-haspopup="true"
      aria-expanded="false"
      title="Modifica l'articolo"
    >
      <img
        class="inverted-icon icon"
        src="~bootstrap-icons/icons/pencil.svg"
        alt="edit icon"
        width="18"
        height="18"
      />
    </a>
  </div>
  <!-- btn group -->
</template>

<script setup lang="ts">
import { useAuthStore } from "../stores/auth.store"
import { toast } from "vue3-toastify"

const user = useAuthStore().user

const host = window.location.host

const props = defineProps<{
  ids: string
  clean: boolean
  share: boolean
  translatable: boolean
}>()

function translate() {}

function window_open(url: string) {
  window.open(url)
}

function copy_link() {
  // https://stackoverflow.com/a/30810322
  const textArea = document.createElement("textarea")

  // *** This styling is an extra step which is likely not required. ***
  //
  // Why is it here? To ensure:
  // 1. the element is able to have focus and selection.
  // 2. if element was to flash render it has minimal visual impact.
  // 3. less flakyness with selection and copying which **might** occur if
  //    the textarea element is not visible.
  //
  // The likelihood is the element won't even render, not even a
  // flash, so some of these are just precautions. However in
  // Internet Explorer the element is visible whilst the popup
  // box asking the user for permission for the web page to
  // copy to the clipboard.

  // Place in top-left corner of screen regardless of scroll position.
  textArea.style.position = "fixed"
  textArea.style.top = "0"
  textArea.style.left = "0"

  // Ensure it has a small width and height. Setting to 1px / 1em
  // doesn't work as this gives a negative w/h on some browsers.
  textArea.style.width = "2em"
  textArea.style.height = "2em"

  // We don't need padding, reducing the size if it does flash render.
  textArea.style.padding = "0"

  // Clean up any borders.
  textArea.style.border = "none"
  textArea.style.outline = "none"
  textArea.style.boxShadow = "none"

  // Avoid flash of white box if rendered for any reason.
  textArea.style.background = "transparent"

  textArea.value = "https://" + host + "/article/" + props.ids

  document.body.appendChild(textArea)
  /* Select the text field */
  textArea.focus()
  textArea.select()
  textArea.setSelectionRange(0, 99999) // For mobile devices

  try {
    const successful = document.execCommand("copy")
    // TODO: rewrite the above line of code withut using the deprecated execCommand
    // via the Clipboard API: https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API
    // https://stackoverflow.com/a/60239236
    const msg = successful ? "successful" : "unsuccessful"
    console.log("Copying text command was " + msg)
  } catch (err) {
    console.log(`Oops, unable to copy: ${err}`)
  }

  document.body.removeChild(textArea)
}

type Format = "html" | "epub" | "mobi" | "pdf" | "txt"

function email(format: Format) {
  const xhr = new XMLHttpRequest()
  const url = `/email.php?format=${format}&ids=${props.ids}`
  xhr.open("GET", url)
  xhr.onload = function () {
    toast.success(
      `L'estratto notizie è stato inviato per e-mail come ebook nel formato ${format}`,
    )
  }
  xhr.send()
}
</script>
