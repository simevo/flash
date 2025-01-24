<template>
  <div class="container">
    <h1>Impostazioni</h1>
    <pre>{{ profile }}</pre>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref, type Ref } from "vue"
import type { components } from "../generated/schema.d.ts"
import { fetch_wrapper } from "@/utils.js"
type Profile = components["schemas"]["Profile"]

const profile: Ref<Profile | null> = ref(null)

// Fetch the profile data
async function fetchProfile() {
  const response = await fetch_wrapper(`../../api/profile/me/`)
  if (response.status == 403) {
    document.location = "/accounts/"
  } else {
    const data: Profile = await response.json()
    profile.value = data
  }
}

// Fetch the profile data when the component is mounted
onMounted(() => {
  console.log("SettingsView mounted")
  fetchProfile()
})
</script>
