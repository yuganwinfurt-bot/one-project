// The support system owns merchant after-sales handling. The buyer portal stays here.
export function openSupportTickets(query = {}) {
  const local = ['localhost', '127.0.0.1', '[::1]'].includes(window.location.hostname)
  const fallback = local ? 'http://127.0.0.1:3000/tickets' : '/support/tickets'
  const target = new URL(import.meta.env.VITE_CUSTOMER_SERVICE_URL || fallback, window.location.href)
  for (const key of ['afterSaleId', 'productId', 'supportConversationId']) {
    const value = Number(query[key])
    if (Number.isSafeInteger(value) && value > 0) target.searchParams.set(key, String(value))
  }
  window.location.assign(target.toString())
}
