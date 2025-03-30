import { defineStore } from "pinia"
import { useLocalStorage, type RemovableRef, StorageSerializers } from "@vueuse/core"
import router from "@/router"

const STORE_NAME = "auth"

type User = null | {
  username: string
  email: string
  groups: string[]
}

export const useAuthStore = defineStore(STORE_NAME, {
  state: () => {
    // initialize state from local storage to enable user to stay logged in
    const user: RemovableRef<User> = useLocalStorage(STORE_NAME, null, {
      serializer: StorageSerializers.object,
    })
    return { user }
  },
  actions: {
    async login(username: string /*, password: string*/) {
      this.user = {
        username: username,
        email: "pablo@example.com",
        groups: ["soci", "staff"],
      }
    },
    logout() {
      this.user = null
      router.push("/account/login")
    },
  },
})
