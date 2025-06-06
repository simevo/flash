declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    base_language: string
  }
}

declare global {
  const VUE_APP_VERSION: string
}

export {}
