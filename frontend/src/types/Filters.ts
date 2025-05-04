export type LanguageFilter =
  | "all"
  | "ar"
  | "ca"
  | "fr"
  | "en"
  | "it"
  | "nl"
  | "pt"
  | "ru"
  | "es"
  | "de"
export type WhenFilter =
  | "all"
  | "24-0"
  | "168-0"
  | "720-0"
  | "8760-0"
  | "17520-8760"
  | "26280-17520"
  | "35040-26280"
  | "876000-35040"
export type LengthFilter = "all" | "0-1000" | "1000-5000" | "5000-10000000"
export type Filters = {
  what: string
  language: LanguageFilter
  when: WhenFilter
  length: LengthFilter
  feed_ids: number[]
}
export type FeedCount = {
  feed: string
  image: string
  count: number
  feed_id: number
}
export type FeedCounts = { [feed_id: number]: FeedCount }
