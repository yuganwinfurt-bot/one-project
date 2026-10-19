import assert from 'node:assert/strict'
import test from 'node:test'
import {
  applicationStatusLabel, canConfirmExchangeReceived, canSubmitReturnShipment,
  canSubmitExchangeShipment, canShipOrder, completionBlockedReason, isAfterSaleClosed,
  orderStatusLabel, serviceTypeTone, returnShipmentLabel, returnTrackingLabel,
  staffApplicationStatusLabel, staffOrderStatusLabel, completionActionLabel
} from '../src/utils/afterSale.js'

test('退货状态覆盖原订单的已发货，并按寄回物流推进', () => {
  const application = { service_type: 'return', status: 'approved', return_shipped: false }
  const order = { status: 'shipped', after_sale: application }
  assert.equal(orderStatusLabel(order), '等待买家寄回')
  assert.equal(canSubmitReturnShipment(application), true)
  assert.ok(completionBlockedReason(application))
  Object.assign(application, { return_shipped: true, return_tracking_no: 'RETURN-001' })
  assert.equal(orderStatusLabel(order), '待商家收货并退款')
  assert.equal(completionBlockedReason(application), '')
  assert.equal(canSubmitExchangeShipment(application), false)
  assert.equal(canShipOrder(order), false)
  application.return_tracking_no = null
  assert.equal(canSubmitReturnShipment(application), true, '旧数据已寄回但缺少物流单号时允许补填')
})

test('换货发货不能直接结束，买家收货后才允许商家完成', () => {
  const application = { service_type: 'exchange', status: 'approved', return_shipped: true, return_tracking_no: 'RETURN-1', order_status: 'completed' }
  assert.equal(canSubmitExchangeShipment(application), true)
  Object.assign(application, { exchange_tracking_no: 'EXCHANGE-1', order_status: 'shipped' })
  assert.equal(canSubmitExchangeShipment(application), false)
  assert.equal(canConfirmExchangeReceived(application), true)
  assert.match(completionBlockedReason(application), /确认收到/)
  application.order_status = 'completed'
  assert.equal(canConfirmExchangeReceived(application), false)
  assert.equal(completionBlockedReason(application), '')
  assert.equal(applicationStatusLabel(application), '已收换货，待售后完成')
  application.status = 'completed'
  assert.equal(applicationStatusLabel(application), '已换货')
  assert.equal(isAfterSaleClosed(application), true)
  application.order_status = 'shipped'
  assert.equal(canConfirmExchangeReceived(application), true, '兼容旧数据：售后提前结束但换货还未收货')
})

test('退款、拒绝和完成显示真实结果，不混成已收货', () => {
  for (const [kind, result, tone] of [['refund', '已退款', 'danger'], ['return', '已退货退款', 'warning'], ['exchange', '已换货', 'warning']]) {
    const application = { service_type: kind, status: 'completed' }
    assert.equal(orderStatusLabel({ status: 'completed', after_sale: application }), result)
    assert.equal(serviceTypeTone(kind), tone)
    assert.ok(completionBlockedReason(application))
  }
  const rejected = { service_type: 'refund', status: 'rejected' }
  assert.equal(orderStatusLabel({ status: 'completed', after_sale: rejected }), '售后已拒绝')
  assert.equal(isAfterSaleClosed(rejected), true)
  assert.equal(canSubmitReturnShipment(rejected), false)
  assert.equal(returnTrackingLabel({ service_type: 'return', status: 'completed' }), '历史记录未留存')
  assert.equal(returnShipmentLabel({ service_type: 'return', status: 'completed' }), '历史寄回信息未留存')
})

test('商家待办使用商家视角，买家状态保留等待商家的说明', () => {
  const application = { service_type: 'return', status: 'approved', return_shipped: true, return_tracking_no: 'RETURN-1' }
  assert.equal(applicationStatusLabel(application), '待商家收货并退款')
  assert.equal(staffApplicationStatusLabel(application), '待你收货并退款')
  assert.equal(staffOrderStatusLabel({ status: 'shipped', after_sale: application }), '待你收货并退款')
  assert.equal(completionActionLabel(application), '确认收货并退款')
  application.service_type = 'refund'
  assert.equal(staffApplicationStatusLabel(application), '待你退款')
  application.service_type = 'exchange'
  assert.equal(staffApplicationStatusLabel(application), '待你寄出换货商品')
})
