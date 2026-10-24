// The support system owns merchant after-sales handling. The buyer portal stays here.
export function openSupportTickets(query = {}) {
  const target = new URL(import.meta.env.VITE_CUSTOMER_SERVICE_URL || 'http://127.0.0.1:3000/tickets')
  for (const key of ['afterSaleId', 'productId', 'supportConversationId']) {
    const value = Number(query[key])
    if (Number.isSafeInteger(value) && value > 0) target.searchParams.set(key, String(value))
  }
  window.location.assign(target.toString())
}
