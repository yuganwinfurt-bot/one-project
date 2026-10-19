// 三种售后在订单、消息卡片、售后列表与右键菜单中使用相同规则。
export const serviceTypeLabel = type => ({ refund: '退款', return: '退货退款', exchange: '换货' }[type] || '售后')
export const serviceTypeTone = type => type === 'refund' ? 'danger' : 'warning'
export const isAfterSaleClosed = application => ['completed', 'rejected'].includes(application?.status)
export const returnShipmentLabel = application => application?.return_tracking_no
  ? '买家已寄回' : application?.status === 'completed' ? '历史寄回信息未留存' : '等待买家提交寄回物流'
export const returnTrackingLabel = application => application?.return_tracking_no || (application?.status === 'completed' ? '历史记录未留存' : '尚未填写')

export function applicationStatusLabel(application, audience = 'customer') {
  if (!application) return '售后处理中'
  const isStaff = audience === 'staff'
  const type = serviceTypeLabel(application.service_type)
  if (application.status === 'pending') return `${type}待${isStaff ? '你' : ''}审核`
  if (application.status === 'rejected') return '售后已拒绝'
  if (application.status === 'completed') return { refund: '已退款', return: '已退货退款', exchange: '已换货' }[application.service_type] || '售后已完成'
  if (application.status === 'approved') {
    if (application.service_type === 'refund') return isStaff ? '待你退款' : '待商家退款'
    if (!application.return_shipped || !application.return_tracking_no) return '等待买家寄回'
    if (application.service_type === 'return') return isStaff ? '待你收货并退款' : '待商家收货并退款'
    if (!application.exchange_tracking_no) return isStaff ? '待你寄出换货商品' : '待商家换货发货'
    return application.order_status === 'completed' ? (isStaff ? '买家已收货，待你完成售后' : '已收换货，待售后完成') : '换货已发货，待买家收货'
  }
  return '售后处理中'
}

export const staffApplicationStatusLabel = application => applicationStatusLabel(application, 'staff')

export function applicationStatusTone(status) {
  return { pending: 'warning', approved: 'warning', rejected: 'danger', completed: 'success' }[status] || 'info'
}

export function completionBlockedReason(application) {
  if (!application) return '售后会话不存在'
  if (application.completion_blocked_reason !== undefined) return application.completion_blocked_reason
  if (isAfterSaleClosed(application)) return '售后已结束，会话已关闭'
  if (application.status !== 'approved') return '需先同意售后申请'
  if (['return', 'exchange'].includes(application.service_type) && !(application.return_shipped && application.return_tracking_no)) return '等待买家寄回商品并提交物流单号'
  if (application.service_type === 'exchange') {
    if (!application.exchange_tracking_no) return '等待商家填写换货发货单号'
    if (application.order_status !== 'completed') return '等待买家确认收到换货商品'
  }
  return ''
}

export function completionActionLabel(application) {
  if (isAfterSaleClosed(application)) return application.status === 'rejected' ? '售后已拒绝，会话已关闭' : '售后已完成，会话已关闭'
  return { refund: '确认退款完成', return: '确认收货并退款', exchange: '确认换货完成' }[application?.service_type] || '完成售后'
}

export function canConfirmExchangeReceived(application) {
  return ['approved', 'completed'].includes(application?.status) && application.service_type === 'exchange' &&
    Boolean(application.exchange_tracking_no) && application.order_status === 'shipped'
}

export function canSubmitReturnShipment(application) {
  return application?.status === 'approved' && ['return', 'exchange'].includes(application.service_type) && !(application.return_shipped && application.return_tracking_no)
}

export function canSubmitExchangeShipment(application) {
  return application?.status === 'approved' && application.service_type === 'exchange' &&
    Boolean(application.return_shipped && application.return_tracking_no) && !application.exchange_tracking_no
}

export function canShipOrder(order) {
  if (order.after_sale && order.after_sale.status !== 'rejected') return false
  if (order.after_sale_status && order.after_sale_status !== 'rejected') return false
  return (order.status === 'paid' && !order.exchange_tracking_no) ||
    (['shipped', 'completed'].includes(order.status) && !order.tracking_no && !order.exchange_tracking_no)
}

export function orderStatusLabel(order, audience = 'customer') {
  if (order.after_sale) return applicationStatusLabel(order.after_sale, audience)
  return { paid: '已支付', shipped: '已发货', completed: '已收货', cancelled: '已取消' }[order.status] || order.status || '—'
}

export const staffOrderStatusLabel = order => orderStatusLabel(order, 'staff')
