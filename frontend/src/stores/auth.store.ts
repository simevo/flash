import { defineStore } from "pinia"
import { useLocalStorage, type RemovableRef, StorageSerializers } from "@vueuse/core"
import type { components } from "../generated/schema.d.ts"
type PatchedUser = components["schemas"]["PatchedUser"]

const STORE_NAME = "auth"

type User = null | PatchedUser

export const useAuthStore = defineStore(STORE_NAME, {
  state: () => {
    // initialize state from local storage to enable user to stay logged in
    const user: RemovableRef<User> = useLocalStorage(STORE_NAME, null, {
      serializer: StorageSerializers.object,
    })
    return { user }
  },
  actions: {
    async login(user: User) {
      this.user = user
    },
    logout() {
      this.user = null
      document.location = "/accounts/"
    },
  },
})
