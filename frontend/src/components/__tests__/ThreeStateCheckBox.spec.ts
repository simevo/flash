import { describe, it, expect } from "vitest"

import { mount } from "@vue/test-utils"

import ThreeStateCheckBox from "../ThreeStateCheckBox.vue"

describe("ThreeStateCheckBox", () => {
  it("renders properly when true", () => {
    const wrapper = mount(ThreeStateCheckBox, { props: { value: true } })
    expect(wrapper.find("input").element.checked).toBe(true)
  })
  it("renders properly when false", () => {
    const wrapper = mount(ThreeStateCheckBox, { props: { value: false } })
    expect(wrapper.find("input").element.checked).toBe(false)
  })
  it("renders properly when null", () => {
    const wrapper = mount(ThreeStateCheckBox, { props: { value: null } })
    expect(wrapper.find("input").element.indeterminate).toBe(true)
  })
})
