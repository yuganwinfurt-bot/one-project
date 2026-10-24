import { useCustomerRouter } from '@/utils/customerRouter'
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { customerCoupons, mallActivity, mallPortal } from '@/api/mall'
import { checkoutTotals, couponLabel } from '@/utils/checkout'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import { ArrowLeft, ArrowRight, Edit, Lightning, Picture, ShoppingCart, Star, StarFilled } from '@element-plus/icons-vue'
import {
  getProductDetail,
  listReviews,
  updateProductAiDetail,
  updateProductDescription,
  updateProductImages,
  updateProductName,
  updateProductPricing,
  updateProductStock,
  updateProductTags
} from '@/api/ecommerce'
import { uploadFileApi } from '@/api/file'
import {
  addCartItem,
  addFavorite,
  buyNowProduct,
  deleteFavorite,
  getAddresses,
  getFavorites,
  getCustomerReviewReplies
} from '@/api/customer'
import { postReviewComment } from '@/api/community'
import { useUser } from '@/utils/user'
import AfterSaleRiskCard from '@/components/AfterSaleRiskCard.vue'
import SkuSelectionDialog from '@/components/SkuSelectionDialog.vue'

export function useProductDetail() {
const route = useRoute()
const router = useCustomerRouter()
const { userInfo } = useUser()
const productId = computed(() => Number(route.params.id))
const productBrandName = ref('')
const focusReviewId = computed(() => {
  const value = Number(route.query.review_id)
  return Number.isInteger(value) && value > 0 ? value : null
})
const focusReviewPending = ref(Boolean(focusReviewId.value))
const entrySource = computed(() => {
  if (['products', 'reviews', 'store'].includes(route.query.from)) return route.query.from
  return (route.path.startsWith('/manager/store/products/') || route.path.startsWith('/mini-store/products/')) ? 'store' : 'products'
})
const returnLabel = computed(() => ({
  store: '返回商品首页',
  products: '返回商品数据',
  reviews: '返回评价数据'
})[entrySource.value])
const aiDetail = computed(() => {
  const raw = detail.value?.product?.ai_detail
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw)
    return typeof parsed === 'object' && parsed !== null ? parsed : null
  } catch {
    return null
  }
})
const isAdmin = computed(() => userInfo.value?.role === 'admin')
const canEditProduct = computed(() => ['admin', 'user'].includes(userInfo.value?.role))
const isCustomer = computed(() => userInfo.value?.role === 'customer')
const selectedVariantKey = ref('')
const selectedVariant = computed(() =>
  detail.value?.product?.variants?.find((variant) => variant.key === selectedVariantKey.value) || null
)
const selectedVariantPrice = computed(() => Number(selectedVariant.value?.price ?? detail.value?.product?.price ?? 0))
const selectedVariantStock = computed(() => Number(selectedVariant.value?.stock ?? detail.value?.product?.stock ?? 0))
const selectedVariantOriginalPrice = computed(() => {
  if (!selectedVariant.value) return Number(detail.value?.product?.original_price ?? detail.value?.product?.price ?? 0)
  const discount = Number(detail.value?.product?.discount_percent || 0)
  return discount > 0 ? Math.round(selectedVariantPrice.value / (1 - discount / 100) * 100) / 100 : selectedVariantPrice.value
})
const productCanOrder = computed(() => {
  const product = detail.value?.product
  return product?.shelf_status === 'on_sale' && product?.review_status === 'normal' && selectedVariantStock.value > 0 && (!product.variants?.length || Boolean(selectedVariant.value))
})
const productHasAvailableStock = computed(() => {
  const product = detail.value?.product
  if (product?.shelf_status !== 'on_sale' || product?.review_status !== 'normal') return false
  return product.variants?.length
    ? product.variants.some((variant) => Number(variant.stock) > 0)
    : Number(product?.stock) > 0
})
const favoriteSaved = ref(false)
const cartBusy = ref(false)
const favoriteBusy = ref(false)
const buyNowOpening = ref(false)
const purchaseSheetVisible = ref(false)
const purchaseSheetAction = ref('buy')
const buyNowAddresses = ref([])
const buyNowAddressId = ref(null)
const buyNowShipping = ref({ base_fee: 0, free_over: 0 })
const buyNowOrderSettings = ref({ checkout_enabled: true, max_quantity: 99, unpaid_timeout_minutes: 30 })
const buyNowQuantity = ref(1)
const buyNowCoupons = ref([])
const buyNowCouponId = ref(null)
const buyNowUsableCoupons = computed(() => buyNowCoupons.value.filter(coupon => coupon.available && coupon.claim_id && !coupon.used_at && !coupon.reserved && Number(coupon.min_amount) <= selectedVariantPrice.value * buyNowQuantity.value))
const buyNowSelectedCoupon = computed(() => buyNowUsableCoupons.value.find(coupon => coupon.claim_id === buyNowCouponId.value))
const buyNowTotals = computed(() => checkoutTotals(selectedVariantPrice.value * buyNowQuantity.value, buyNowSelectedCoupon.value, buyNowShipping.value))
const buyNowSaving = ref(false)
const buyNowMaxQuantity = computed(() => Math.max(1, Math.min(selectedVariantStock.value || 1, Number(buyNowOrderSettings.value.max_quantity) || 99, 99)))
const loading = ref(false)
const error = ref('')
const detail = ref(null)
watch(buyNowUsableCoupons, coupons => {
  if (buyNowCouponId.value && !coupons.some(coupon => coupon.claim_id === buyNowCouponId.value)) buyNowCouponId.value = null
})
const productOutOfStock = computed(() => detail.value?.product != null && Number(detail.value.product.stock) <= 0)
const activeImageIndex = ref(0)
const productImages = computed(() => {
  const images = detail.value?.product?.image_urls
  if (Array.isArray(images) && images.length) return images.filter(Boolean)
  const mainImage = detail.value?.product?.image_url
  return mainImage ? [mainImage] : []
})
const activeImageUrl = computed(() => productImages.value[activeImageIndex.value] || productImages.value[0] || '')
const productTags = computed(() => {
  const tags = detail.value?.product?.tags
  return Array.isArray(tags) && tags.length ? tags : [detail.value?.product?.category].filter(Boolean)
})
const hasProductDiscount = computed(() => Number(detail.value?.product?.discount_percent || 0) > 0)
const discountedPricePreview = computed(() => {
  const originalPrice = Number(originalPriceDraft.value || 0)
  const discountPercent = Number(discountPercentDraft.value || 0)
  return Math.round(originalPrice * (1 - discountPercent / 100) * 100) / 100
})
const commonTagOptions = [
  '日用', '家居', '数码', '个护', '美妆', '运动', '户外', '办公', '通勤', '服饰',
  '鞋靴', '厨房', '清洁', '儿童', '学生', '玩具', '家电', '寝具', '箱包', '照明'
]
const tagsDraft = ref([])
const availableTagOptions = computed(() =>
  [...new Set([...commonTagOptions, ...productTags.value, ...tagsDraft.value])]
)
const imageUploading = ref(false)
const imageManagerDialogVisible = ref(false)
const draggedImageIndex = ref(null)
const dragOverImageIndex = ref(null)
const reviewLoading = ref(false)
const reviewRows = ref([])
const reviewReplies = ref({})
const reviewTotal = ref(0)
const reviewPage = ref(1)
const reviewPageSize = 5
const reviewFilters = reactive({ keywords: '', rating: '', replyStatus: '' })
const customerReplyEditingId = ref(null)
const customerReplyDraft = ref('')
const customerReplySaving = ref(false)
const replyTarget = ref(null)
const nameDialogVisible = ref(false)
const nameDraft = ref('')
const nameSaving = ref(false)
const tagsDialogVisible = ref(false)
const tagsSaving = ref(false)
const customTagInputVisible = ref(false)
const customTagDraft = ref('')
const pricingDialogVisible = ref(false)
const originalPriceDraft = ref(0)
const discountPercentDraft = ref(0)
const pricingSaving = ref(false)
const stockDialogVisible = ref(false)
const stockDraft = ref(0)
const stockSaving = ref(false)
const descriptionDialogVisible = ref(false)
const descriptionDraft = ref('')
const descriptionSaving = ref(false)
const aiDetailDialogVisible = ref(false)
const aiHeadlineDraft = ref('')
const aiPointsDraft = ref('')
const aiDetailDraft = ref('')
const aiDetailSaving = ref(false)
function goBack() {
  const targets = {
    store: '/manager/store',
    products: '/manager/products',
    reviews: '/manager/reviews'
  }
  router.push(targets[entrySource.value])
}
async function loadFavoriteState() {
  if (!isCustomer.value || !detail.value?.product?.id) return
  try {
    const response = await getFavorites()
    favoriteSaved.value = (response.data?.list || []).some(
      (item) => item.product.id === detail.value.product.id
    )
  } catch {
    favoriteSaved.value = false
  }
}
function openAddToCart() {
  if (!productHasAvailableStock.value || cartBusy.value) return
  purchaseSheetAction.value = 'cart'
  selectedVariantKey.value = ''
  buyNowQuantity.value = 1
  purchaseSheetVisible.value = true
}
function selectPurchaseVariant(key) {
  selectedVariantKey.value = key
  buyNowQuantity.value = 1
  buyNowCouponId.value = null
}
async function addToCart() {
  if (!productCanOrder.value || cartBusy.value) return
  cartBusy.value = true
  try {
    await addCartItem(productId.value, buyNowQuantity.value, selectedVariant.value?.key || null)
    ElMessage.success('已加入购物车')
    window.dispatchEvent(new Event('customer-cart-updated'))
    purchaseSheetVisible.value = false
  } catch (requestError) {
    ElMessage.error(requestError?.message || '加入购物车失败')
  } finally {
    cartBusy.value = false
  }
}
async function toggleFavorite() {
  if (favoriteBusy.value) return
  favoriteBusy.value = true
  try {
    if (favoriteSaved.value) {
      await deleteFavorite(productId.value)
      favoriteSaved.value = false
      ElMessage.success('已取消收藏')
    } else {
      await addFavorite(productId.value)
      favoriteSaved.value = true
      ElMessage.success('已加入收藏')
    }
  } catch (requestError) {
    ElMessage.error(requestError?.message || '更新收藏失败')
  } finally {
    favoriteBusy.value = false
  }
}
function addressLabel(address) {
  return `${address.receiver_name} · ${address.phone} · ${address.province}${address.city}${address.district}${address.detail}`
}
async function openBuyNow() {
  if (!productHasAvailableStock.value || buyNowOpening.value) return
  buyNowOpening.value = true
  try {
    const [response, portalResponse, couponResponse] = await Promise.all([getAddresses(), mallPortal(), customerCoupons()])
    buyNowAddresses.value = response.data?.list || []
    if (!buyNowAddresses.value.length) {
      ElMessage.warning('请先添加收货地址，再购买商品')
      await router.push('/manager/addresses')
      return
    }
    buyNowAddressId.value =
      buyNowAddresses.value.find((address) => address.is_default)?.id || buyNowAddresses.value[0].id
    selectedVariantKey.value = ''
    buyNowQuantity.value = 1
    buyNowShipping.value = portalResponse.data.shipping
    buyNowOrderSettings.value = portalResponse.data.order
    buyNowCoupons.value = couponResponse.data.list
    buyNowCouponId.value = null
    purchaseSheetAction.value = 'buy'
    purchaseSheetVisible.value = true
  } catch (requestError) {
    ElMessage.error(requestError?.message || '读取收货地址失败')
  } finally {
    buyNowOpening.value = false
  }
}
async function confirmBuyNow() {
  if (!buyNowAddressId.value || !productCanOrder.value || buyNowSaving.value) return
  buyNowSaving.value = true
  try {
    const response = await buyNowProduct(productId.value, buyNowQuantity.value, buyNowAddressId.value, selectedVariant.value?.key || null, buyNowSelectedCoupon.value?.claim_id || null)
    purchaseSheetVisible.value = false
    ElMessage.success(response.message || '下单成功')
    await router.push({ path: '/manager/my-orders', query: { pay: response.data.order.id } })
  } catch (requestError) {
    ElMessage.error(requestError?.message || '立即购买失败')
  } finally {
    buyNowSaving.value = false
  }
}
function confirmPurchaseSheet() {
  if (purchaseSheetAction.value === 'cart') return addToCart()
  return confirmBuyNow()
}
function stepProductImage(direction) {
  const count = productImages.value.length
  if (count < 2) return
  activeImageIndex.value = (activeImageIndex.value + direction + count) % count
}
function openNameEditor() {
  nameDraft.value = detail.value?.product?.name || ''
  nameDialogVisible.value = true
}
function openTagsEditor() {
  tagsDraft.value = [...productTags.value]
  customTagDraft.value = ''
  customTagInputVisible.value = false
  tagsDialogVisible.value = true
}
function openPricingEditor() {
  originalPriceDraft.value = Number(detail.value?.product?.original_price ?? detail.value?.product?.price ?? 0)
  discountPercentDraft.value = Number(detail.value?.product?.discount_percent || 0)
  pricingDialogVisible.value = true
}
function openStockEditor() {
  stockDraft.value = Number(detail.value?.product?.stock || 0)
  stockDialogVisible.value = true
}
async function saveProductStock() {
  const stock = Number(stockDraft.value)
  if (!Number.isInteger(stock) || stock < 0 || stock > 2147483647) {
    ElMessage.warning('库存必须是 0 到 2147483647 之间的整数')
    return
  }
  stockSaving.value = true
  try {
    const response = await updateProductStock(productId.value, stock)
    detail.value.product = { ...detail.value.product, ...response.data }
    stockDialogVisible.value = false
    ElMessage.success('商品库存已保存')
  } catch (requestError) {
    ElMessage.error(requestError?.message || '商品库存保存失败')
  } finally {
    stockSaving.value = false
  }
}
function formatPercent(value) {
  return Number(value || 0).toLocaleString('zh-CN', { maximumFractionDigits: 2 })
}
async function saveProductPricing() {
  const originalPrice = Number(originalPriceDraft.value)
  const discountPercent = Number(discountPercentDraft.value)
  if (!Number.isFinite(originalPrice) || originalPrice <= 0) {
    ElMessage.warning('原价必须大于 0')
    return
  }
  if (!Number.isFinite(discountPercent) || discountPercent < 0 || discountPercent > 99.99) {
    ElMessage.warning('优惠幅度必须在 0% 到 99.99% 之间')
    return
  }
  if (discountedPricePreview.value < 0.01) {
    ElMessage.warning('折后售价不能低于 0.01 元')
    return
  }
  pricingSaving.value = true
  try {
    const response = await updateProductPricing(productId.value, originalPrice, discountPercent)
    detail.value.product = { ...detail.value.product, ...response.data }
    pricingDialogVisible.value = false
    ElMessage.success('商品价格已保存')
  } catch (requestError) {
    ElMessage.error(requestError?.message || '商品价格保存失败')
  } finally {
    pricingSaving.value = false
  }
}
function addCustomTag() {
  const tag = customTagDraft.value.trim()
  if (!tag) {
    ElMessage.warning('请输入标签名称')
    return
  }
  if (!tagsDraft.value.includes(tag)) tagsDraft.value = [...tagsDraft.value, tag]
  customTagDraft.value = ''
  customTagInputVisible.value = false
}
async function saveProductTags() {
  const tags = [...new Set(tagsDraft.value.map((tag) => String(tag).trim()).filter(Boolean))]
  if (!tags.length) {
    ElMessage.warning('至少保留一个商品标签')
    return
  }
  tagsSaving.value = true
  try {
    const response = await updateProductTags(productId.value, tags)
    detail.value.product = { ...detail.value.product, ...response.data }
    tagsDialogVisible.value = false
    ElMessage.success('商品标签已保存')
  } catch (requestError) {
    ElMessage.error(requestError?.message || '商品标签保存失败')
  } finally {
    tagsSaving.value = false
  }
}
async function saveProductName() {
  const name = nameDraft.value.trim()
  if (!name) {
    ElMessage.warning('商品名称不能为空')
    return
  }
  nameSaving.value = true
  try {
    const response = await updateProductName(productId.value, name)
    detail.value.product = { ...detail.value.product, ...response.data }
    nameDialogVisible.value = false
    ElMessage.success('商品名称已保存')
  } catch (requestError) {
    ElMessage.error(requestError?.message || '商品名称保存失败')
  } finally {
    nameSaving.value = false
  }
}
function openDescriptionEditor() {
  descriptionDraft.value = detail.value?.product?.description || ''
  descriptionDialogVisible.value = true
}
async function saveDescription() {
  const description = descriptionDraft.value.trim()
  if (!description) {
    ElMessage.warning('商品介绍不能为空')
    return
  }
  descriptionSaving.value = true
  try {
    const response = await updateProductDescription(productId.value, description)
    detail.value.product = { ...detail.value.product, ...response.data }
    descriptionDialogVisible.value = false
    ElMessage.success('商品介绍已保存')
  } catch (requestError) {
    ElMessage.error(requestError?.message || '商品介绍保存失败')
  } finally {
    descriptionSaving.value = false
  }
}
function openAiDetailEditor() {
  aiHeadlineDraft.value = aiDetail.value?.headline || ''
  aiPointsDraft.value = Array.isArray(aiDetail.value?.selling_points)
    ? aiDetail.value.selling_points.join('\n')
    : ''
  aiDetailDraft.value = aiDetail.value?.detail || ''
  aiDetailDialogVisible.value = true
}
async function saveAiDetail() {
  const headline = aiHeadlineDraft.value.trim()
  const body = aiDetailDraft.value.trim()
  if (!headline || !body) {
    ElMessage.warning('请填写文案标题和详情正文')
    return
  }
  const aiCopy = {
    headline,
    selling_points: aiPointsDraft.value.split('\n').map((point) => point.trim()).filter(Boolean),
    detail: body
  }
  const serialized = JSON.stringify(aiCopy)
  if (serialized.length > 12000) {
    ElMessage.warning('文案总长度超过限制，请适当精简')
    return
  }
  aiDetailSaving.value = true
  try {
    const response = await updateProductAiDetail(productId.value, serialized)
    detail.value.product = { ...detail.value.product, ...response.data }
    aiDetailDialogVisible.value = false
    ElMessage.success('商品文案已保存')
  } catch (requestError) {
    ElMessage.error(requestError?.message || '商品文案保存失败')
  } finally {
    aiDetailSaving.value = false
  }
}
const ratingBuckets = computed(() =>
  [...(detail.value?.review_summary?.rating_distribution || [])].reverse()
)
const maxRatingCount = computed(() =>
  Math.max(1, ...ratingBuckets.value.map((bucket) => bucket.count))
)
function formatMoney(value) {
  const amount = Number(value || 0)
  return `¥${amount.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`
}
function shelfLabel(value) {
  return value === 'on_sale' ? '在售' : value === 'off_shelf' ? '已下架' : value || '未知状态'
}
function reviewStatusLabel(value) {
  return value === 'pending_review' ? '待复核' : value === 'normal' ? '正常' : value || '未知状态'
}
function ratingWidth(count) {
  return `${Math.round((count / maxRatingCount.value) * 100)}%`
}
function ratingTone(rating) {
  if (rating <= 2) return 'bad'
  if (rating >= 4) return 'good'
  return 'mid'
}
function validateProductImage(file) {
  if (!file.type?.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return false
  }
  if (file.size > 20 * 1024 * 1024) {
    ElMessage.error('商品主图不能超过 20 MB')
    return false
  }
  return true
}
async function uploadProductImage(options) {
  await saveUploadedProductImage(options, null)
}
function createReplaceRequest(index) {
  return (options) => saveUploadedProductImage(options, index)
}
async function saveUploadedProductImage(options, replaceIndex) {
  imageUploading.value = true
  try {
    const uploaded = await uploadFileApi(options.file)
    const imageUrl = uploaded.data?.url
    if (!imageUrl) throw new Error('图片上传失败，请重试')
    const currentImages = [...productImages.value]
    const nextImages = [...currentImages]
    const nextIndex = replaceIndex === null ? nextImages.length : replaceIndex
    if (replaceIndex === null) nextImages.push(imageUrl)
    else nextImages[replaceIndex] = imageUrl
    const response = await updateProductImages(productId.value, nextImages)
    detail.value.product = response.data
    activeImageIndex.value = nextIndex
    ElMessage.success(replaceIndex === null ? '商品图片已新增' : '商品图片已替换')
    options.onSuccess?.(response)
  } catch (requestError) {
    ElMessage.error(requestError?.message || '商品图片更新失败')
    options.onError?.(requestError)
  } finally {
    imageUploading.value = false
  }
}
async function removeProductImage(index) {
  const confirmed = await ElMessageBox.confirm('下架后，这张图片将不再显示在商品页面。确定继续吗？', '下架商品图片', {
    confirmButtonText: '确认下架',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => true).catch(() => false)
  if (!confirmed) return

  imageUploading.value = true
  try {
    const previousActiveIndex = activeImageIndex.value
    const nextImages = productImages.value.filter((_, imageIndex) => imageIndex !== index)
    const response = await updateProductImages(productId.value, nextImages)
    detail.value.product = response.data
    activeImageIndex.value = nextImages.length
      ? previousActiveIndex === index
        ? Math.min(index, nextImages.length - 1)
        : previousActiveIndex > index
          ? previousActiveIndex - 1
          : previousActiveIndex
      : 0
    ElMessage.success('商品图片已下架')
  } catch (requestError) {
    ElMessage.error(requestError?.message || '商品图片下架失败')
  } finally {
    imageUploading.value = false
  }
}
function startImageDrag(event, index) {
  if (imageUploading.value) {
    event.preventDefault()
    return
  }
  draggedImageIndex.value = index
  dragOverImageIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', String(index))
}
function handleImageDragOver(index) {
  if (draggedImageIndex.value !== null) dragOverImageIndex.value = index
}
async function dropProductImage(targetIndex) {
  const sourceIndex = draggedImageIndex.value
  if (sourceIndex === null || sourceIndex < 0 || sourceIndex >= productImages.value.length || sourceIndex === targetIndex) {
    finishImageDrag()
    return
  }

  const nextImages = [...productImages.value]
  const [movedImage] = nextImages.splice(sourceIndex, 1)
  nextImages.splice(targetIndex, 0, movedImage)
  const previousActiveIndex = activeImageIndex.value

  imageUploading.value = true
  try {
    const response = await updateProductImages(productId.value, nextImages)
    detail.value.product = response.data
    activeImageIndex.value = previousActiveIndex === sourceIndex
      ? targetIndex
      : sourceIndex < previousActiveIndex && previousActiveIndex <= targetIndex
        ? previousActiveIndex - 1
        : targetIndex <= previousActiveIndex && previousActiveIndex < sourceIndex
          ? previousActiveIndex + 1
          : previousActiveIndex
    ElMessage.success('商品图片顺序已保存')
  } catch (requestError) {
    ElMessage.error(requestError?.message || '商品图片排序保存失败')
  } finally {
    imageUploading.value = false
    finishImageDrag()
  }
}
function finishImageDrag() {
  draggedImageIndex.value = null
  dragOverImageIndex.value = null
}
async function loadReviews() {
  reviewLoading.value = true
  try {
    const params = {
      product_id: productId.value,
      page: reviewPage.value,
      page_size: reviewPageSize,
      keywords: reviewFilters.keywords.trim() || undefined,
      rating: reviewFilters.rating || undefined,
      focus_review_id: focusReviewPending.value ? focusReviewId.value || undefined : undefined,
      has_reply: reviewFilters.replyStatus === 'replied'
        ? true
        : reviewFilters.replyStatus === 'unreplied'
          ? false
          : undefined
    }
    const response = await listReviews(params)
    reviewRows.value = response.data?.list || []
    reviewTotal.value = response.data?.total || 0
    await loadCustomerReviewReplies(reviewRows.value)
    if (focusReviewPending.value && focusReviewId.value) {
      await nextTick()
      document.getElementById(`product-review-${focusReviewId.value}`)?.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      })
      focusReviewPending.value = false
    }
  } catch (requestError) {
    reviewRows.value = []
    reviewTotal.value = 0
    ElMessage.error(requestError?.message || '评价加载失败')
  } finally {
    reviewLoading.value = false
  }
}
async function loadCustomerReviewReplies(reviews) {
  if (!reviews.length) {
    reviewReplies.value = {}
    return
  }
  try {
    const entries = await Promise.all(reviews.map(async (review) => {
      const response = await getCustomerReviewReplies(review.id)
      return [review.id, response.data?.list || []]
    }))
    reviewReplies.value = Object.fromEntries(entries)
  } catch (requestError) {
    reviewReplies.value = {}
    ElMessage.error(requestError?.message || '评价回复加载失败')
  }
}
function isOwnReview(review) {
  return review.buyer_user_id === userInfo.value?.id
}
function beginReviewComment(review, target = null) {
  if (customerReplySaving.value) return
  customerReplyEditingId.value = review.id
  customerReplyDraft.value = ''
  replyTarget.value = target?.user_id !== userInfo.value?.id ? target : null
}
function cancelCustomerReply() {
  customerReplyEditingId.value = null
  customerReplyDraft.value = ''
  replyTarget.value = null
}
async function saveCustomerReply(review) {
  const content = customerReplyDraft.value.trim()
  if (!content) {
    ElMessage.warning('请先填写回复内容')
    return
  }
  customerReplySaving.value = true
  try {
    const response = await postReviewComment(review.id, content, replyTarget.value?.user_id)
    const currentRows = reviewReplies.value[review.id] || []
    reviewReplies.value = { ...reviewReplies.value, [review.id]: [...currentRows, response.data] }
    if (canEditProduct.value && !review.merchant_reply && (!replyTarget.value || replyTarget.value.user_id === review.buyer_user_id)) review.merchant_reply = content
    cancelCustomerReply()
    ElMessage.success('评价回复已发布')
  } catch (requestError) {
    ElMessage.error(requestError?.message || '回复发布失败')
  } finally {
    customerReplySaving.value = false
  }
}
function handleReviewFilter() {
  reviewPage.value = 1
  loadReviews()
}
function changeReviewPage(page) {
  reviewPage.value = page
  loadReviews()
}
async function load() {
  if (!Number.isInteger(productId.value) || productId.value < 1) {
    detail.value = null
    error.value = '商品编号无效'
    return
  }

  loading.value = true
  error.value = ''
  try {
    const [response, catalogResponse] = await Promise.all([
      getProductDetail(productId.value), request.get(`/api/mall/product-catalog/${productId.value}`)
    ])
    productBrandName.value = catalogResponse.data.brand_name
    detail.value = response.data || null
    selectedVariantKey.value = ''
    if (isCustomer.value && detail.value) mallActivity({ kind:'footprint', product_id:productId.value }).catch(() => {})
    activeImageIndex.value = 0
    if (!detail.value) error.value = '没有找到该商品'
    else {
      reviewPage.value = 1
      await loadFavoriteState()
      await loadReviews()
    }
  } catch (requestError) {
    detail.value = null
    error.value = requestError?.message || '商品详情加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
watch(
  () => [productId.value, route.query.review_id],
  () => {
    focusReviewPending.value = Boolean(focusReviewId.value)
    load()
  }
)
onMounted(load)
return {
useCustomerRouter,
computed,
nextTick,
onMounted,
reactive,
ref,
watch,
customerCoupons,
mallActivity,
mallPortal,
checkoutTotals,
couponLabel,
request,
ElMessage,
ElMessageBox,
useRoute,
ArrowLeft,
ArrowRight,
Edit,
Lightning,
Picture,
ShoppingCart,
Star,
StarFilled,
getProductDetail,
listReviews,
updateProductAiDetail,
updateProductDescription,
updateProductImages,
updateProductName,
updateProductPricing,
updateProductStock,
updateProductTags,
uploadFileApi,
addCartItem,
addFavorite,
buyNowProduct,
deleteFavorite,
getAddresses,
getFavorites,
getCustomerReviewReplies,
postReviewComment,
useUser,
AfterSaleRiskCard,
SkuSelectionDialog,
route,
router,
userInfo,
productId,
productBrandName,
focusReviewId,
focusReviewPending,
entrySource,
returnLabel,
aiDetail,
isAdmin,
canEditProduct,
isCustomer,
selectedVariantKey,
selectedVariant,
selectedVariantPrice,
selectedVariantStock,
selectedVariantOriginalPrice,
productCanOrder,
productHasAvailableStock,
favoriteSaved,
cartBusy,
favoriteBusy,
buyNowOpening,
purchaseSheetVisible,
purchaseSheetAction,
buyNowAddresses,
buyNowAddressId,
buyNowShipping,
buyNowOrderSettings,
buyNowQuantity,
buyNowCoupons,
buyNowCouponId,
buyNowUsableCoupons,
buyNowSelectedCoupon,
buyNowTotals,
buyNowSaving,
buyNowMaxQuantity,
loading,
error,
detail,
productOutOfStock,
activeImageIndex,
productImages,
activeImageUrl,
productTags,
hasProductDiscount,
discountedPricePreview,
commonTagOptions,
tagsDraft,
availableTagOptions,
imageUploading,
imageManagerDialogVisible,
draggedImageIndex,
dragOverImageIndex,
reviewLoading,
reviewRows,
reviewReplies,
reviewTotal,
reviewPage,
reviewPageSize,
reviewFilters,
customerReplyEditingId,
customerReplyDraft,
customerReplySaving,
replyTarget,
nameDialogVisible,
nameDraft,
nameSaving,
tagsDialogVisible,
tagsSaving,
customTagInputVisible,
customTagDraft,
pricingDialogVisible,
originalPriceDraft,
discountPercentDraft,
pricingSaving,
stockDialogVisible,
stockDraft,
stockSaving,
descriptionDialogVisible,
descriptionDraft,
descriptionSaving,
aiDetailDialogVisible,
aiHeadlineDraft,
aiPointsDraft,
aiDetailDraft,
aiDetailSaving,
goBack,
loadFavoriteState,
openAddToCart,
selectPurchaseVariant,
addToCart,
toggleFavorite,
addressLabel,
openBuyNow,
confirmBuyNow,
confirmPurchaseSheet,
stepProductImage,
openNameEditor,
openTagsEditor,
openPricingEditor,
openStockEditor,
saveProductStock,
formatPercent,
saveProductPricing,
addCustomTag,
saveProductTags,
saveProductName,
openDescriptionEditor,
saveDescription,
openAiDetailEditor,
saveAiDetail,
ratingBuckets,
maxRatingCount,
formatMoney,
shelfLabel,
reviewStatusLabel,
ratingWidth,
ratingTone,
validateProductImage,
uploadProductImage,
createReplaceRequest,
saveUploadedProductImage,
removeProductImage,
startImageDrag,
handleImageDragOver,
dropProductImage,
finishImageDrag,
loadReviews,
loadCustomerReviewReplies,
isOwnReview,
beginReviewComment,
cancelCustomerReply,
saveCustomerReply,
handleReviewFilter,
changeReviewPage,
load
};
}
