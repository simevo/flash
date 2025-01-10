const hour = 3600.0
const day = 24.0 * hour
const week = 7.0 * day
const year = 365.2421 * day
const month = year / 12.0

// fuzzily humanize elapsed time
export function secondsToString(seconds: number) {
  const upper_threshold = 1.5
  const lower_threshold = 0.9

  const years = seconds / year
  const months = seconds / month
  const weeks = seconds / week
  const days = seconds / day
  const hours = seconds / hour
  const minutes = seconds / 60.0
  if (years > 10.0) return "un eternità"
  else if (years > upper_threshold) return `${Math.round(years)} anni fa`
  else if (years > lower_threshold) return "un anno fa"
  else if (months > upper_threshold) return `${Math.round(months)} mesi fa`
  else if (months > lower_threshold) return "un mese fa"
  else if (weeks > upper_threshold) return `${Math.round(weeks)} settimane fa`
  else if (weeks > lower_threshold) return "una settimana fa"
  else if (days > upper_threshold) return `${Math.round(days)} giorni fa`
  else if (days > lower_threshold) return "un giorno fa"
  else if (hours > upper_threshold) return `${Math.round(hours)} ore fa`
  else if (hours > lower_threshold) return "un'ora fa"
  else if (minutes > upper_threshold) return `${Math.round(minutes)} minuti fa`
  else if (minutes > lower_threshold) return "un minuto fa"
  else return "or ora"
} // secondsToString

// precisely humanize time interval
export function secondsToString1(seconds: number) {
  const hour = 3600
  const day = 24 * hour
  const week = 7 * day
  const year = 365.2421 * day
  const month = year / 12.0

  const years = Math.round(seconds / year)
  const months = Math.round(seconds / month)
  const weeks = Math.round(seconds / week)
  const days = Math.round(seconds / day)
  const hours = Math.round(seconds / hour)
  const minutes = Math.round(seconds / 60)
  if (years >= 2) return `${years} anni`
  else if (years === 1) return "un anno"
  else if (months >= 2) return `${months} mesi`
  else if (months === 1) return "un mese"
  else if (weeks > 1) return `${weeks} settimane`
  else if (weeks === 1) return "una settimana"
  else if (days >= 2) return `${days} giorni`
  else if (days === 1) return "un giorno"
  else if (hours > 1) return `${hours} ore`
  else if (hours === 1) return "un'ora"
  else if (minutes > 1) return `${minutes} minuti`
  else if (minutes === 1) return "un minuto"
  else if (seconds > 20) return "½ minuto"
  else return "un attimo"
} // secondsToString1
