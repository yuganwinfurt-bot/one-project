import test from 'node:test'
import assert from 'node:assert/strict'
import { checkoutTotals } from '../src/utils/checkout.js'

test('discount threshold and free shipping use the same goods subtotal', () => {
  assert.deepEqual(checkoutTotals(199, { min_amount: 199, discount: 25 }, { base_fee: 8, free_over: 199 }), { subtotal: 199, discount: 25, shipping: 0, payable: 174 })
  assert.equal(checkoutTotals(198.99, { min_amount: 199, discount: 25 }, { base_fee: 8, free_over: 199 }).payable, 206.99)
})
test('discount cannot reduce goods below one cent and shipping still applies', () => {
  assert.deepEqual(checkoutTotals(5, { min_amount: 0, discount: 10 }, { base_fee: 8 }), { subtotal: 5, discount: 4.99, shipping: 8, payable: 8.01 })
})
test('empty selection has no shipping fee', () => {
  assert.equal(checkoutTotals(0, null, { base_fee: 8 }).payable, 0)
})
