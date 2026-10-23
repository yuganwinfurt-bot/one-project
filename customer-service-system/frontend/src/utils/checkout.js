// 使用整数分计算展示金额；服务端会再次校验优惠券和实际应付金额。
export function checkoutTotals(subtotal, coupon = null, shipping = {}) {
  const goods = Math.max(0, Math.round(Number(subtotal || 0) * 100))
  const threshold = Math.round(Number(coupon?.min_amount || 0) * 100)
  const discount = coupon && goods >= threshold
    ? Math.min(Math.max(0, Math.round(Number(coupon.discount || 0) * 100)), Math.max(0, goods - 1)) : 0
  const freeOver = Math.round(Number(shipping.free_over || 0) * 100)
  const fee = goods === 0 || (freeOver > 0 && goods >= freeOver) ? 0 : Math.max(0, Math.round(Number(shipping.base_fee || 0) * 100))
  return { subtotal: goods / 100, discount: discount / 100, shipping: fee / 100, payable: (goods - discount + fee) / 100 }
}

export function couponLabel(coupon) {
  const name = String(coupon.name || '')
  const minimum = Number(coupon.min_amount || 0), discount = Number(coupon.discount || 0)
  return name.replace(/[\s¥￥]/g, '').endsWith(`满${minimum}减${discount}`)
    ? name : `${name} · 满 ¥${minimum} 减 ¥${discount}`
}
