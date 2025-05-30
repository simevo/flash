<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, inject, defineProps, defineEmits, type Ref } from 'vue';
import { fetch_wrapper, find_voice } from '../utils';

// Props
const props = defineProps({
  articles: { type: Array as () => any[], default: () => [] },
  base_language: { type: String, default: 'it' },
  current_list_id: { type: String, default: null }
});

// Emits
const emit = defineEmits(['tts-closed', 'tts-started', 'tts-stopped', 'article-changed']);

// TTS-related data properties
const tts = ref(false);
const tts_open = ref(true); // Initialize to true, as its rendering is controlled by parent
const stopped = ref(true);
const current_article = ref(0);
const speaking = ref(false);
const current_chunk = ref(0);
let voices: SpeechSynthesisVoice[] = []; // declare it, will be populated in onMounted

// Methods moved from ListsView.vue

function tts_init() {
  if ("speechSynthesis" in window) {
    console.log("TTS API available for Toolbar");
    window.speechSynthesis.cancel(); // Clear any previous utterances
    tts.value = true; // Indicates TTS capability is present
    voices = window.speechSynthesis.getVoices();
    if (voices.length === 0) { // Some browsers load voices asynchronously
        window.speechSynthesis.onvoiceschanged = () => {
            voices = window.speechSynthesis.getVoices();
            console.log("Voices loaded:", voices);
        };
    } else {
        console.log("Voices immediately available:", voices);
    }
  } else {
    console.log("No TTS API available for Toolbar!");
    tts.value = false;
  }
}

function beginPlayback() {
  console.log("Speak TTS from Toolbar");
  // tts_open is managed by parent, this component assumes it's open when rendered
  current_article.value = 0;
  current_chunk.value = 0;
  if (window.speechSynthesis) { // Ensure synthesis is available
    // Mobile Safari requires an utterance (even a blank one) during
    // a user interaction to enable further utterances.
    // This might need to be linked to an explicit user action if auto-play is problematic.
    speechSynthesis.speak(new SpeechSynthesisUtterance(""));
  }
  if (props.articles && props.articles.length > 0) {
    emit('tts-started');
    tts_continue(); // This will call read_article
  } else {
    console.log("No articles to play.");
  }
}

onMounted(() => {
  console.log("TtsToolbar mounted");
  tts_init();
  // Automatically start playback if articles are present.
  // Consider if this should be behind a prop or explicit user action.
  if (props.articles.length > 0) {
    beginPlayback();
  }
});

onUnmounted(() => {
  console.log("TtsToolbar unmounted");
  tts_stop(); // Stops current speech and cleans up some state
  tts_cleanup(); // Further cleanup
  window.speechSynthesis.cancel(); // Ensure all utterances are removed
});

// Watch for changes in articles prop to auto-start if list was empty and now has articles
watch(() => props.articles, (newArticles, oldArticles) => {
  if (newArticles.length > 0 && oldArticles.length === 0 && tts_open.value) {
    console.log("Articles prop changed, starting TTS playback.");
    // Reset and start playback only if it was not already speaking or if current_article needs reset
    if (stopped.value || current_article.value >= newArticles.length) {
        current_article.value = 0; // Reset to first article
        current_chunk.value = 0;
        beginPlayback();
    }
  } else if (newArticles.length === 0 && oldArticles.length > 0) {
    console.log("Articles prop now empty, stopping TTS.");
    tts_stop();
  }
});


function tts_continue() {
  console.log("Continue TTS from Toolbar");
  stopped.value = false;
  read_article();
}

function tts_restart() {
  console.log("Restart TTS from Toolbar");
  stopped.value = true;
  window.speechSynthesis.cancel();
  current_article.value = 0;
  current_chunk.value = 0;
  // Mobile Safari requires an utterance (even a blank one) during
  // a user interaction to enable furher utterances
  if (window.speechSynthesis) {
    speechSynthesis.speak(new SpeechSynthesisUtterance(""));
  }
  emit('tts-started');
  tts_continue();
}

function tts_back() {
  console.log("Back TTS from Toolbar");
  stopped.value = true;
  window.speechSynthesis.cancel();
  tts_cleanup(); // Cleanup for the current article's state if any
  if (current_article.value > 0) {
    current_article.value -= 1;
  }
  current_chunk.value = 0;
  emit('tts-started');
  tts_continue();
}

function tts_forward() {
  console.log("Forward TTS from Toolbar");
  stopped.value = true;
  window.speechSynthesis.cancel();
  tts_cleanup(); // Cleanup for the current article's state if any
  if (current_article.value < props.articles.length - 1) {
    current_article.value += 1;
  }
  current_chunk.value = 0;
  emit('tts-started');
  tts_continue();
}

function tts_stop() {
  console.log("Stop TTS from Toolbar");
  stopped.value = true;
  window.speechSynthesis.cancel();
  // tts_cleanup(); // Don't call cleanup here, as it removes visual progress. Parent should handle.
  speaking.value = false;
  emit('tts-stopped');
}

async function read_article() {
  console.log("Reading article from Toolbar: " + current_article.value);
  if (current_article.value >= props.articles.length) {
    console.log("All articles read or out of bounds.");
    tts_close(); // Or emit an event indicating completion
    return;
  }
  if (current_article.value < 0) { // Should not happen if logic is correct
    console.log("Current article index is negative, resetting to 0.");
    current_article.value = 0;
  }

  const article = props.articles[current_article.value];
  if (!article) {
    console.error("Article not found at current index:", current_article.value);
    tts_close();
    return;
  }

  // Emit article changed event
  emit('article-changed', article.id, current_article.value);

  const lang = article.language || props.base_language;
  console.log("Looking for voices with lang = " + lang);
  const voice = find_voice(voices, lang);

  if (voice) {
    console.log("Voice found for Toolbar:", voice);
    // Assuming article object might not have full content, fetch it if necessary.
    // For now, this component will rely on the structure of `props.articles`.
    // If `article.content` is not available or insufficient, `fetchArticle` would be needed here.
    // Let's assume `props.articles` contains objects with `id`, `title`, `content`, `language`.
    // const article_full = await fetchArticle(article.id); // Potentially add back if needed

    const content = article.content; //  article.language === props.base_language ? article_full.content : article_full.content_original;
    const title = article.title; // article.language === props.base_language ? article_full.title : article_full.title_original;

    speaking.value = true;
    const content_stripped = stripHtml(content || "");
    const text = title + ". " + content_stripped;

    console.log("Reading text from Toolbar:", text.substring(0, 100) + "..."); // Log snippet
    const chunks = text.match(/.{1,200}/g); // Adjusted chunk size for potentially better flow

    if (chunks && chunks.length > 0) {
      const trimmed_chunks = chunks.map(chunk => chunk.trim()).filter(chunk => chunk !== "");
      console.log(`Reading ${trimmed_chunks.length} chunks from Toolbar.`);
      // current_chunk.value should be 0 if starting a new article, managed by calling functions like tts_restart, tts_forward etc.
      read(voice, trimmed_chunks, lang);
    } else {
      console.log("No text chunks to read for article:", article.id);
      speaking.value = false;
      // Move to next article or stop
      tts_forward_internal(); // internal skip to next if current is empty
    }
  } else {
    alert("Nessuna voce disponibile per la lingua: " + lang + " (Toolbar)");
    // Skip to the next article
    tts_forward_internal(); // internal skip to next if no voice
  }
}

// Internal helper to advance article without user interaction (e.g. empty content, no voice)
function tts_forward_internal() {
    if (current_article.value < props.articles.length - 1) {
        current_article.value += 1;
        current_chunk.value = 0;
        read_article();
    } else {
        tts_close(); // No more articles
    }
}


async function fetchArticle(article_id: number): Promise<any> { // Using any for now
  // Path needs to be relative to index.html or absolute.
  // Assuming fetch_wrapper handles this. If utils.ts is in src/, then api is sibling to src/
  const response = await fetch_wrapper(`/api/articles/${article_id}/`); // Adjusted path
  const data: any = await response.json();
  return data;
}

function stripHtml(html: string): string {
  if (!html) return "";
  const doc = new DOMParser().parseFromString(html, "text/html");
  return doc.body.textContent || "";
}

function speaker_start() {
  console.log("Speaker started for article " + current_article.value + " chunk " + current_chunk.value + " (Toolbar)");
}

function read(
  voice: SpeechSynthesisVoice,
  chunks: string[],
  lang: string,
) {
  console.log(`${chunks.length - current_chunk.value} chunks left to read for article ${props.articles[current_article.value]?.id} (Toolbar)`);

  if (stopped.value) {
    console.log("TTS stopped, not reading further chunks.");
    speaking.value = false;
    return;
  }

  const utterance = new window.SpeechSynthesisUtterance();
  const my_current_article_index = current_article.value; // Capture current article index for async safety

  function speaker_error(e: SpeechSynthesisErrorEvent) {
    console.error("Speaker error (Toolbar):", e.error, "for article index:", my_current_article_index, "chunk:", current_chunk.value -1);
    // Potentially retry or skip chunk/article
    // For now, stop for this article to avoid loops.
    if (!stopped.value && current_article.value === my_current_article_index) {
      // Simple retry for the same chunk once, then advance.
      // This is a basic error handling, could be more sophisticated.
      // utterance.removeEventListener("error", speaker_error_once_then_advance);
      // utterance.addEventListener("error", speaker_error_final);
      // window.speechSynthesis.speak(utterance);
      // For now, just advance to next chunk or article to avoid getting stuck.
      current_chunk.value +=1; // advance past problematic chunk
       if (!stopped.value && current_article.value === my_current_article_index) {
         read(voice, chunks, lang); // try next chunk
       }
    }
  }

  function speaker_end() {
    console.log(`Speaker ended for chunk ${current_chunk.value -1} of article ${props.articles[my_current_article_index]?.id} (Toolbar)`);
    if (!stopped.value && current_article.value === my_current_article_index) {
      if (current_chunk.value < chunks.length) {
        read(voice, chunks, lang); // Read next chunk
      } else {
        // Finished all chunks for this article
        console.log("Finished all chunks for article:", props.articles[my_current_article_index]?.id);
        speaking.value = false;
        // utterance.removeEventListener("start", speaker_start);
        // utterance.removeEventListener("error", speaker_error);
        // utterance.removeEventListener("end", speaker_end);
        // tts_cleanup(); // Visual cleanup handled by parent

        // Automatically play next article
        setTimeout(() => {
          if (!stopped.value && current_article.value === my_current_article_index) { // ensure still on same article before advancing
            current_article.value += 1;
            current_chunk.value = 0; // Reset chunk for new article
            read_article();
          }
        }, 1000); // Small delay before starting next article
      }
    } else {
        console.log("Speaker ended, but TTS was stopped or article changed. Current article:", current_article.value, "My article index:", my_current_article_index);
    }
  }

  if (current_chunk.value >= chunks.length) {
    // This case should be handled by the end of the last chunk in speaker_end
    // However, as a safeguard:
    console.log("All chunks processed for article (safeguard):", props.articles[my_current_article_index]?.id);
    speaking.value = false;
    // Trigger next article or end
    setTimeout(() => {
        if (!stopped.value && current_article.value === my_current_article_index) {
            current_article.value += 1;
            current_chunk.value = 0;
            read_article();
        }
    }, 100);
    return;
  }

  utterance.voice = voice;
  const chunk_text = chunks[current_chunk.value];
  current_chunk.value += 1;

  // Emit progress? Could be an emit here for current chunk and total chunks.
  // emit('tts-progress', { current: current_chunk.value, total: chunks.length, article_id: props.articles[my_current_article_index].id });

  utterance.text = chunk_text || ""; // Ensure text is not null/undefined
  utterance.lang = lang;
  utterance.addEventListener("start", speaker_start); // Can be defined once if not needing closure over chunk
  utterance.addEventListener("error", speaker_error);
  utterance.addEventListener("end", speaker_end);

  console.log("Speaking chunk:", current_chunk.value -1, "Text:", chunk_text.substring(0,50)+"...");
  window.speechSynthesis.speak(utterance);
}

function tts_close() {
  console.log("Close TTS from Toolbar");
  stopped.value = true;
  window.speechSynthesis.cancel();
  speaking.value = false;
  // tts_open is controlled by parent, this emits that user wants to close
  emit('tts-closed');
  // tts_cleanup(); // Visual cleanup by parent
}

function tts_cleanup() {
  console.log("Cleanup TTS state in Toolbar (not visual elements)");
  // Visual cleanup (like article card backgrounds) should be handled by the parent component (ListsView)
  // based on events or props. This component should not directly manipulate DOM outside its own template.
  window.speechSynthesis.cancel(); // Ensure any speech is stopped.
}

</script>

<template>
  <div
    style="position: fixed; z-index: 1000; bottom: 1em; left: 1em"
    class="btn-group btn-group-sm"
    id="button-tts"
    role="group"
    aria-label="Controlla la lettura"
    v-if="tts"
  >
    <button
      type="button"
      id="button-restart"
      class="btn btn-success"
      title="Dall'inizio"
      @click="tts_restart()"
    >
      <img src="~bootstrap-icons/icons/skip-start-fill.svg" alt="fast backward icon" />
    </button>
    <button
      type="button"
      id="button-back"
      class="btn btn-success"
      title="Indietro"
      @click="tts_back()"
      :disabled="current_article == 0 && current_chunk == 0"
    >
      <img src="~bootstrap-icons/icons/rewind-fill.svg" alt="rewind icon" />
    </button>
    <button
      type="button"
      id="button-stop"
      class="btn btn-success"
      title="Stop"
      @click="tts_stop()"
      :disabled="!speaking"
    >
      <img src="~bootstrap-icons/icons/pause-fill.svg" alt="pause icon" />
    </button>
    <button
      type="button"
      id="button-continue"
      class="btn btn-success"
      title="Continua"
      @click="tts_continue()"
      :disabled="speaking"
    >
      <img src="~bootstrap-icons/icons/play-fill.svg" alt="play icon" />
    </button>
    <button
      type="button"
      id="button-forward"
      class="btn btn-success"
      title="Avanti"
      @click="tts_forward()"
      :disabled="current_article >= (props.articles ? props.articles.length - 1 : 0) && current_chunk == 0"
    >
      <img src="~bootstrap-icons/icons/fast-forward-fill.svg" alt="forward icon" />
    </button>
    <button
      type="button"
      id="button-close"
      class="btn btn-success"
      title="Chiudi"
      @click="tts_close()"
    >
      <img src="~bootstrap-icons/icons/stop-fill.svg" alt="close icon" />
    </button>
  </div>
</template>

<style scoped>
/* Styles will be added if necessary */
</style>
