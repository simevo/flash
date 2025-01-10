<template>
  <input
    class="form-check-input"
    type="checkbox"
    :checked="value === true"
    :indeterminate="value === null"
    @change="change"
  />
</template>

<script setup lang="ts">
import type { CheckBoxValue } from "../types/CheckBoxValue"

const emit = defineEmits<{
  (e: "change", value: CheckBoxValue): void
}>()

const props = defineProps<{
  value: CheckBoxValue
}>()

function change() {
  if (props.value === null) {
    emit("change", true)
    return
  }
  if (props.value === true) {
    emit("change", false)
    return
  }
  if (props.value === false) {
    emit("change", null)
    return
  }
}
</script>
