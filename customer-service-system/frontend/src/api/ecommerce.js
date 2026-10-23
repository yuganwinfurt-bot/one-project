import request from '@/utils/request'

export function scanAfterSaleRisks() {
  return request({ url: '/api/ecommerce/after-sale-risks/scan', method: 'post' })
}

export function confirmAfterSaleRiskReview(productId) {
  return request({ url: `/api/ecommerce/products/${productId}/after-sale-risk/review`, method: 'post' })
}

/** 首页数据概览（规模 / 趋势 / 评分分布 / 口碑榜单 / 最近预警） */
export function getOverview(params) {
  return request({
    url: '/api/ecommerce/overview',
    method: 'get',
    params
  })
}

/** 商品详情：基础信息 + 评价/订单汇总 + 该商品的报告与预警（只读） */
export function getProductDetail(productId) {
  return request({
    url: `/api/ecommerce/products/${productId}/detail`,
    method: 'get'
  })
}

/** 更新商品主图；后端只允许管理员操作 */
export function updateProductImage(productId, imageUrl) {
  return request({
    url: `/api/ecommerce/products/${productId}/image`,
    method: 'put',
    data: { image_url: imageUrl }
  })
}

/** 更新商品图片列表，第一张为主图，最多三张 */
export function updateProductImages(productId, imageUrls) {
  return request({
    url: `/api/ecommerce/products/${productId}/images`,
    method: 'put',
    data: { image_urls: imageUrls }
  })
}

/** 保存 AI 商品详情文案；运营与管理员可操作 */
export function updateProductAiDetail(productId, aiDetail) {
  return request({
    url: `/api/ecommerce/products/${productId}/ai-detail`,
    method: 'put',
    data: { ai_detail: aiDetail }
  })
}

/** 更新商品介绍；运营与管理员可操作 */
export function updateProductDescription(productId, description) {
  return request({
    url: `/api/ecommerce/products/${productId}/description`,
    method: 'put',
    data: { description }
  })
}

/** 更新商品名称；运营与管理员可操作 */
export function updateProductName(productId, name) {
  return request({
    url: `/api/ecommerce/products/${productId}/name`,
    method: 'put',
    data: { name }
  })
}

/** 更新商品多标签 */
export function updateProductTags(productId, tags) {
  return request({
    url: `/api/ecommerce/products/${productId}/tags`,
    method: 'put',
    data: { tags }
  })
}

/** 更新商品原价和优惠百分比，后端自动计算折后售价 */
export function updateProductPricing(productId, originalPrice, discountPercent) {
  return request({
    url: `/api/ecommerce/products/${productId}/pricing`,
    method: 'put',
    data: { original_price: originalPrice, discount_percent: discountPercent }
  })
}

/** 商品数据页集中更新商品基本信息；price 为折后售价 */
export function updateProduct(productId, product) {
  return request({
    url: `/api/ecommerce/products/${productId}`,
    method: 'put',
    data: product
  })
}

/** 创建商品并直接上架；运营与管理员可操作。 */
export function createProductListing(product) {
  return request({
    url: '/api/ecommerce/products',
    method: 'post',
    data: product
  })
}

/** 保存商品完整资料并上架；运营与管理员可操作。 */
export function updateProductListing(productId, product) {
  return request({
    url: `/api/ecommerce/products/${productId}/listing`,
    method: 'put',
    data: product
  })
}

/** 更新商品上下架状态；运营与管理员可操作 */
export function updateProductShelfStatus(productId, shelfStatus) {
  return request({
    url: `/api/ecommerce/products/${productId}/shelf-status`,
    method: 'put',
    data: { shelf_status: shelfStatus }
  })
}

/** 更新商品库存；运营与管理员可操作。 */
export function updateProductStock(productId, stock) {
  return request({
    url: `/api/ecommerce/products/${productId}/stock`,
    method: 'put',
    data: { stock }
  })
}

/** 分页查询商品（只读） */
export function listProducts(params) {
  return request({
    url: '/api/ecommerce/products',
    method: 'get',
    params
  })
}

/** 商品首页：只展示在售且通过复核的商品 */
export function getStorefrontProducts(params) {
  return request({
    url: '/api/ecommerce/storefront/products',
    method: 'get',
    params
  })
}

/** 分页查询订单（可按数量、实付、状态和下单时间排序） */
export function listOrders(params) {
  return request({
    url: '/api/ecommerce/orders',
    method: 'get',
    params
  })
}

/** 订单详情：订单本身 + 这笔订单的评价（可能没有） */
export function getOrderDetail(orderId) {
  return request({
    url: `/api/ecommerce/orders/${orderId}/detail`,
    method: 'get'
  })
}

/** 将已支付订单标记为已发货；仅管理员或运营可操作 */
export function shipOrder(orderId, trackingNo) {
  return request({
    url: `/api/ecommerce/orders/${orderId}/ship`,
    method: 'post',
    data: { tracking_no: trackingNo }
  })
}

/** 售后中心列表与审核处理 */
export function listAfterSales(params) {
  return request({ url: '/api/ecommerce/after-sales', method: 'get', params })
}

export function processAfterSale(afterSaleId, action, adminNote) {
  return request({
    url: `/api/ecommerce/after-sales/${afterSaleId}/process`,
    method: 'post',
    data: { action, admin_note: adminNote || null }
  })
}

export function submitAfterSaleExchangeShipment(afterSaleId, exchangeTrackingNo) {
  return request({
    url: `/api/ecommerce/after-sales/${afterSaleId}/exchange-shipment`,
    method: 'post',
    data: { exchange_tracking_no: exchangeTrackingNo }
  })
}

export function getAfterSaleMessages(afterSaleId) {
  return request({ url: `/api/ecommerce/after-sales/${afterSaleId}/messages`, method: 'get' })
}

export function sendAfterSaleMessage(afterSaleId, content) {
  return request({
    url: `/api/ecommerce/after-sales/${afterSaleId}/messages`,
    method: 'post',
    data: { content }
  })
}

/** 后台消息中心：新订单、售后、私聊与业务事件通知。 */
export function getStaffMessageCenter() {
  return request({ url: '/api/ecommerce/message-center', method: 'get' })
}

export function markStaffMessageEventRead(eventId) {
  return request({
    url: `/api/ecommerce/message-center/events/${eventId}/read`,
    method: 'post'
  })
}

export function markAllStaffMessageEventsRead() {
  return request({ url: '/api/ecommerce/message-center/events/read-all', method: 'post' })
}

/** 分页查询评价（可按商品、评分与回复状态筛选，并按评分或评价时间排序） */
export function listReviews(params) {
  return request({
    url: '/api/ecommerce/reviews',
    method: 'get',
    params
  })
}

/** 发布或修改商家评价回复；后端只允许管理员操作 */
export function updateReviewReply(reviewId, merchantReply) {
  return request({
    url: `/api/ecommerce/reviews/${reviewId}/reply`,
    method: 'put',
    data: { merchant_reply: merchantReply }
  })
}

/** 分页查询诊断报告（Agent 写操作的产物，只读） */
export function listReports(params) {
  return request({
    url: '/api/ecommerce/reports',
    method: 'get',
    params
  })
}

/** 诊断报告详情与生成时保存的证据明细 */
export function getReportDetail(reportId) {
  return request({
    url: `/api/ecommerce/reports/${reportId}`,
    method: 'get'
  })
}

/** 分页查询预警通知（Agent 写操作的产物，只读） */
export function listAlerts(params) {
  return request({
    url: '/api/ecommerce/alerts',
    method: 'get',
    params
  })
}

/** 预警概览：总数与未读数（页签角标用） */
export function getAlertSummary() {
  return request({
    url: '/api/ecommerce/alerts/summary',
    method: 'get'
  })
}

/** 把一条预警标记为已读（只改通知状态） */
export function markAlertRead(alertId) {
  return request({
    url: `/api/ecommerce/alerts/${alertId}/read`,
    method: 'post'
  })
}

/** 把所有预警标记为已读 */
export function markAllAlertsRead() {
  return request({
    url: '/api/ecommerce/alerts/read-all',
    method: 'post'
  })
}
