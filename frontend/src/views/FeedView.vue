<template>
  <div class="container-fluid my-3" v-if="count_fetch == 0">
    <FeedCard v-if="feed" :feed="feed" :clickable="false" @refresh_feed="refresh_feed" />
    <hr />

    <!-- Accordion for Staff Users -->
    <div class="accordion my-3" v-if="isStaffUser">
      <div class="accordion-item">
        <h2 class="accordion-header" id="feedPollingAccordionHeader">
          <button
            class="accordion-button collapsed"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#feedPollingCollapse"
            aria-expanded="false"
            aria-controls="feedPollingCollapse"
          >
            Monitoring
          </button>
        </h2>
        <div
          id="feedPollingCollapse"
          class="accordion-collapse collapse"
          aria-labelledby="feedPollingAccordionHeader"
        >
          <div class="accordion-body">
            <!-- Sparkline Chart -->
            <div class="mb-3" style="height: 200px">
              <canvas id="feedPollingSparkline"></canvas>
            </div>

            <!-- Paginated Table -->
            <div v-if="feedPollingData.length > 0">
              <table class="table table-striped table-sm">
                <thead>
                  <tr>
                    <th>Poll Start Time</th>
                    <th>Poll End Time</th>
                    <th>HTTP Status</th>
                    <th>Retrieved</th>
                    <th>Failed</th>
                    <th>Stored</th>
                    <th>Error</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in paginatedFeedPollingData" :key="record.id">
                    <td>{{ formatDate(record.poll_start_time) }}</td>
                    <td>{{ formatDate(record.poll_end_time) }}</td>
                    <td>{{ record.http_status }}</td>
                    <td>{{ record.articles_retrieved }}</td>
                    <td>{{ record.articles_failed }}</td>
                    <td>{{ record.articles_stored }}</td>
                    <td :title="record.error_message || ''" style="max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                      {{ record.error_message }}
                    </td>
                  </tr>
                </tbody>
              </table>
              <!-- Pagination Controls -->
              <nav aria-label="Feed polling pagination">
                <ul class="pagination pagination-sm justify-content-center">
                  <li class="page-item" :class="{ disabled: currentPage === 1 }">
                    <button class="page-link" @click="changePage(currentPage - 1)">
                      Previous
                    </button>
                  </li>
                  <li
                    class="page-item"
                    v-for="page in totalPages"
                    :key="page"
                    :class="{ active: currentPage === page }"
                  >
                    <button class="page-link" @click="changePage(page)">
                      {{ page }}
                    </button>
                  </li>
                  <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                    <button class="page-link" @click="changePage(currentPage + 1)">
                      Next
                    </button>
                  </li>
                </ul>
              </nav>
            </div>
            <div v-else class="alert alert-info text-center" role="alert">
              No polling data available for this feed.
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- End Accordion -->

    <div class="row" v-if="articles.length == 0 && count_fetch == 0">
      <div class="col-md-12">
        <div class="alert alert-warning text-center" role="alert">
          Non ci sono articoli da visualizzare.
        </div>
      </div>
    </div>
    <div class="row" v-else-if="articles.length > 0">
      <div class="col-md-12">
        <div class="wrapper">
          <ArticleCard
            v-for="article in articles"
            :key="article.id"
            :article="article"
            :feed_dict="feed_dict"
            :index="1"
            :list_id="null"
          />
        </div>
      </div>
    </div>
  </div>
  <div class="container my-3" v-else>
    <div class="row">
      <div class="text-center col-md-8 offset-md-2">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { fetch_wrapper } from "../utils"
import { onActivated, watch, computed } from "vue" // Added computed
import { useRoute } from "vue-router"
import { ref, onMounted, type Ref } from "vue"
import { Chart, registerables } from "chart.js/auto" // Added Chart
Chart.register(...registerables) // Register all controllers, elements, scales, and plugins

import type { components } from "../generated/schema.d.ts"
type ArticleRead = components["schemas"]["ArticleRead"]
type Feed = components["schemas"]["Feed"]
type PaginatedArticleReadList = components["schemas"]["PaginatedArticleReadList"]
type PatchedFeed = Feed & { my_rating: number }
type UserFeed = components["schemas"]["UserFeed"]
type User = components["schemas"]["User"] // Added User type

// Define FeedPollingRecord type based on the serializer
interface FeedPollingRecord {
  id: number
  feed_id: number
  poll_start_time: string
  poll_end_time: string | null
  http_status: number | null
  error_message: string | null
  articles_retrieved: number | null
  articles_stored: number | null
  articles_failed: number | null
}

import ArticleCard from "../components/ArticleCard.vue"
import FeedCard from "../components/FeedCard.vue"

const articles: Ref<ArticleRead[]> = ref([])
const feeds: Ref<Feed[]> = ref([])
const feed_dict: Ref<{ [key: number]: Feed }> = ref({})
const feed: Ref<PatchedFeed | null> = ref(null)
const count_fetch = ref(3) // Incremented count_fetch to 3 for the new API call (user data)

const route = useRoute()

// New reactive variables
const isStaffUser: Ref<boolean> = ref(false)
const feedPollingData: Ref<FeedPollingRecord[]> = ref([])
const currentPage: Ref<number> = ref(1)
const itemsPerPage: Ref<number> = ref(10)
let sparklineChartInstance: Chart | null = null

export interface Props {
  feed_id: string
}

const props = withDefaults(defineProps<Props>(), {
  feed_id: "",
})

// Computed property for paginated feed polling data
const paginatedFeedPollingData = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return feedPollingData.value.slice(start, end)
})

// Computed property for total pages
const totalPages = computed(() => {
  return Math.ceil(feedPollingData.value.length / itemsPerPage.value)
})

// Function to change page
function changePage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// Format date function
function formatDate(dateTimeString: string | null) {
  if (!dateTimeString) return "N/A"
  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }
  return new Date(dateTimeString).toLocaleString(undefined, options)
}

async function fetchArticles() {
  const response = await fetch_wrapper(`../../api/articles/?feed_id=${props.feed_id}`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else if (response.ok) {
    const data: PaginatedArticleReadList = await response.json()
    articles.value = data.results
  } else {
    console.error("Failed to fetch articles:", response.statusText)
  }
  count_fetch.value -= 1
}

async function fetchFeeds() {
  try {
    const response = await fetch_wrapper(`../../api/feeds/`)
    if (response.status == 403) {
      document.location = "/accounts/"
      return
    }
    if (!response.ok) {
      console.error("Failed to fetch feeds:", response.statusText)
      count_fetch.value -= 1 // Decrement even on error to allow UI to render
      return
    }
    const data: Feed[] = await response.json()

    const response2 = await fetch_wrapper(`../../api/user-feeds/`)
    if (!response2.ok) {
      console.error("Failed to fetch user feeds:", response2.statusText)
      // Proceed with feeds data even if user-feeds fails for now
    } else {
      const ufs: UserFeed[] = await response2.json()
      const ufd: { [key: number]: number | undefined } = {}
      ufs.forEach((element) => {
        ufd[element.feed_id] = element.rating
      })
      feed.value = <PatchedFeed>{
        ...data.find((f) => f.id === Number(props.feed_id)), // More robust way to find the feed
        my_rating: ufd[Number(props.feed_id)],
      }
    }

    feeds.value = data
    feeds.value.forEach((f) => {
      feed_dict.value[f.id] = f
    })
    // Ensure feed.value is set even if user-feeds fails or no rating exists
    if (!feed.value && data.some(f => f.id === Number(props.feed_id))) {
        feed.value = <PatchedFeed>{
            ...data.find(f => f.id === Number(props.feed_id)),
            my_rating: undefined,
        };
    }


  } catch (error) {
    console.error("Error in fetchFeeds:", error)
  } finally {
    count_fetch.value -= 1
  }
}

async function fetchUserData() {
  try {
    const response = await fetch_wrapper(`../../api/users/me/`)
    if (response.ok) {
      const userData: User = await response.json()
      isStaffUser.value = userData.is_staff || false
    } else {
      console.error("Failed to fetch user data:", response.statusText)
      // If user data fails, assume not staff
      isStaffUser.value = false
    }
  } catch (error) {
    console.error("Error fetching user data:", error)
    isStaffUser.value = false
  } finally {
    count_fetch.value -= 1
  }
}

async function fetchFeedPollingData(feedId: string) {
  if (!feedId) return
  // count_fetch.value += 1; // Increment for this specific fetch
  try {
    const response = await fetch_wrapper(`../../api/feed-polling/?feed_id=${feedId}`)
    if (response.ok) {
      const data: FeedPollingRecord[] = await response.json()
      // The API returns paginated results, we need to handle that if we want all.
      // For now, assuming the default pagination of the API is enough or we only care about the first page.
      // If the API returns an object with 'results', use data.results
      if (Array.isArray(data)) {
        feedPollingData.value = data
      } else if (data && Array.isArray((data as any).results)) {
        feedPollingData.value = (data as any).results
      } else {
        console.error("Unexpected format for feed polling data:", data)
        feedPollingData.value = []
      }
      renderSparklineChart()
      currentPage.value = 1 // Reset to first page on new data
    } else {
      console.error("Failed to fetch feed polling data:", response.statusText)
      feedPollingData.value = [] // Clear data on error
    }
  } catch (error) {
    console.error("Error fetching feed polling data:", error)
    feedPollingData.value = [] // Clear data on error
  } finally {
    // count_fetch.value -=1;
  }
}

function renderSparklineChart() {
  const canvas = document.getElementById("feedPollingSparkline") as HTMLCanvasElement
  if (!canvas) return

  if (sparklineChartInstance) {
    sparklineChartInstance.destroy()
  }

  // Prepare data for the chart (last 24 records, articles_retrieved)
  const chartData = feedPollingData.value
    .slice(0, 24) // API returns reverse chronological, so first 24 are latest
    .reverse() // Reverse to show time progression from left to right
    .map((record) => record.articles_retrieved ?? 0) // Use nullish coalescing for undefined/null

  const labels = feedPollingData.value
    .slice(0, 24)
    .reverse()
    .map((record) => formatDate(record.poll_start_time).split(",")[1]) // Just time part for brevity

  sparklineChartInstance = new Chart(canvas, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Articles Retrieved",
          data: chartData,
          borderColor: "rgb(75, 192, 192)",
          tension: 0.1,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
        },
        x: {
          ticks: {
            autoSkip: true,
            maxTicksLimit: 10
          }
        }
      },
      plugins: {
        legend: {
          display: false, // Hide legend for a sparkline feel
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
    },
  })
}

onMounted(() => {
  console.log("FeedView mounted")
  fetchArticles()
  fetchFeeds()
  fetchUserData() // Fetch user data
  // Fetch polling data only if feed_id is available and user is staff,
  // otherwise it will be fetched by the watcher or when isStaffUser becomes true.
  if (props.feed_id && isStaffUser.value) {
     count_fetch.value +=1 // account for this fetch
     fetchFeedPollingData(props.feed_id).finally(() => count_fetch.value -=1);
  }
})

onActivated(() => {
  console.log("FeedView activated")
})

watch(
  () => route.params.feed_id,
  (newId, oldId) => {
    console.log(`FeedView watch id, newId = [${newId}] oldId = [${oldId}]`)
    if (newId && newId != oldId) {
      count_fetch.value += 2 // For fetchArticles and fetchFeeds
      fetchArticles()
      fetchFeeds()
      if (isStaffUser.value) {
        count_fetch.value +=1 // account for this fetch
        fetchFeedPollingData(newId as string).finally(() => count_fetch.value -=1);
      }
    }
  },
)

// Watch for isStaffUser to become true and feed_id to be available, then fetch polling data
watch([isStaffUser, () => props.feed_id], ([staff, feedIdNew], [_, feedIdOld]) => {
  if (staff && feedIdNew) {
    // Check if feedId actually changed or if it's the initial load for a staff user
    if (feedPollingData.value.length === 0 || feedIdNew !== feedIdOld) {
        count_fetch.value +=1 // account for this fetch
        fetchFeedPollingData(feedIdNew as string).finally(() => count_fetch.value -=1);
    }
  }
}, { immediate: false }) // Set immediate to false, onMounted handles initial load if user is already staff


async function refresh_feed(feed_id: number) {
  count_fetch.value = 2 // For fetchArticles and fetchFeeds
  const response = await fetch_wrapper(`../../api/feeds/${feed_id}/refresh/`, {
    method: "POST",
  })
  if (response.status == 403) {
    document.location = "/accounts/"
  } else if (response.ok){
    const data = await response.json()
    alert(`Fonte aggiornata: ${JSON.stringify(data)}`)
    fetchArticles() // This will decrement count_fetch
    fetchFeeds()    // This will also decrement count_fetch
    if (isStaffUser.value) {
      count_fetch.value +=1 // account for this fetch
      fetchFeedPollingData(props.feed_id).finally(() => count_fetch.value -=1);
    }
  } else {
    alert(`Errore durante l'aggiornamento della fonte.`)
    // Still decrement count_fetch as the main operations might have partially succeeded or failed
    // and we need to allow the UI to potentially render error states or existing data.
    count_fetch.value = 0; // Reset to show UI
  }
}
</script>
