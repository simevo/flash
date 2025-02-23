export function fetch_wrapper(
  uri: string,
  options: RequestInit | undefined = undefined,
) {
  const headers = new Headers()
  headers.append("Content-Type", "application/json")
  headers.append("accept", "application/json")
  // requests other than GET, HEAD, OPTIONS or TRACE require the CSRF token
  if (
    options &&
    options.method &&
    !(options.method in ["GET", "HEAD", "OPTIONS", "TRACE"])
  ) {
    const csrftoken = getCookie("csrftoken")
    headers.append("X-CSRFToken", csrftoken)
  }
  return fetch(uri, {
    ...options,
    headers,
  })
}

function getCookie(name: string) {
  let cookieValue = ""
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

export function copy_link(link: string): void {
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

  textArea.value = link

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
    console.log(`Oops, unable to copy; ${err}`)
  }

  document.body.removeChild(textArea)
}
