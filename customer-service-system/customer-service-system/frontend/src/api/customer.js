import request from '@/utils/request'

export function getCart() {
  return request({ url: '/api/customer/cart', method: 'get' })
}

export function addCartItem(productId, quantity = 1) {
  return request({ url: '/api/customer/cart', method: 'post', data: { product_id: productId, quantity } })
}

export function updateCartItem(itemId, quantity) {
  return request({ url: `/api/customer/cart/${itemId}`, method: 'put', data: { quantity } })
}

export function deleteCartItem(itemId) {
  return request({ url: `/api/customer/cart/${itemId}`, method: 'delete' })
}

export function getFavorites() {
  return request({ url: '/api/customer/favorites', method: 'get' })
}

export function addFavorite(productId) {
  return request({ url: `/api/customer/favorites/${productId}`, method: 'post' })
}

export function deleteFavorite(productId) {
  return request({ url: `/api/customer/favorites/${productId}`, method: 'delete' })
}

export function getCustomerMessages() {
  return request({ url: '/api/customer/messages', method: 'get' })
}

export function markCustomerMessagesRead() {
  return request({ url: '/api/customer/messages/read-all', method: 'post' })
}

export function markCustomerMessageRead(type, messageId) {
  return request({
    url: `/api/customer/messages/${type}/${messageId}/read`,
    method: 'post'
  })
}

export function getCustomerAfterSaleMessages(afterSaleId) {
  return request({ url: `/api/customer/messages/after-sales/${afterSaleId}`, method: 'get' })
}

export function sendCustomerAfterSaleMessage(afterSaleId, content) {
  return request({
    url: `/api/customer/messages/after-sales/${afterSaleId}`,
    method: 'post',
    data: { content }
  })
}

export function submitCustomerAfterSaleServiceRating(afterSaleId, rating, feedback) {
  return request({
    url: `/api/customer/after-sales/${afterSaleId}/service-rating`,
    method: 'post',
    data: { rating, feedback }
  })
}

export function getAddresses() {
  return request({ url: '/api/customer/addresses', method: 'get' })
}

export function createAddress(address) {
  return request({ url: '/api/customer/addresses', method: 'post', data: address })
}

export function updateAddress(addressId, address) {
  return request({ url: `/api/customer/addresses/${addressId}`, method: 'put', data: address })
}

export function deleteAddress(addressId) {
  return request({ url: `/api/customer/addresses/${addressId}`, method: 'delete' })
}

export function checkoutCart(addressId, itemIds) {
  return request({
    url: '/api/customer/orders',
    method: 'post',
    data: { address_id: addressId, item_ids: itemIds }
  })
}

export function buyNowProduct(productId, quantity, addressId) {
  return request({
    url: '/api/customer/orders/buy-now',
    method: 'post',
    data: { product_id: productId, quantity, address_id: addressId }
  })
}

export function getCustomerOrders() {
  return request({ url: '/api/customer/orders', method: 'get' })
}

export function createOrderAfterSale(orderId, application) {
  return request({
    url: `/api/customer/orders/${orderId}/after-sales`,
    method: 'post',
    data: application
  })
}

export function submitAfterSaleReturnShipment(afterSaleId, returnTrackingNo) {
  return request({
    url: `/api/customer/after-sales/${afterSaleId}/return-shipment`,
    method: 'post',
    data: { return_tracking_no: returnTrackingNo }
  })
}

export function confirmOrderReceived(orderId) {
  return request({ url: `/api/customer/orders/${orderId}/receive`, method: 'post' })
}

export function createOrderReview(orderId, review) {
  return request({ url: `/api/customer/orders/${orderId}/review`, method: 'post', data: review })
}

export function getCustomerReviewReplies(reviewId) {
  return request({ url: `/api/customer/reviews/${reviewId}/replies`, method: 'get' })
}

export function saveCustomerReviewReply(reviewId, content) {
  return request({
    url: `/api/customer/reviews/${reviewId}/replies`,
    method: 'post',
    data: { content }
  })
}
