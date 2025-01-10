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
