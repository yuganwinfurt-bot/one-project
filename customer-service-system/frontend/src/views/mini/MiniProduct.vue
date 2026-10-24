<template>

<div class="m-view"><MiniHeader title="商品详情" back="/mini-store"><template #right><button class="m-icon-button" @click="router.push('/manager/cart')" aria-label="购物车"><el-icon><ShoppingCart /></el-icon></button></template></MiniHeader>
<div class="m-scroll m-product-scroll" v-loading="loading">
  <div v-if="error" class="m-empty"><p>{{ error }}</p><button class="m-secondary" @click="load">重新加载</button></div>
  <template v-if="detail">
    <div class="m-gallery"><el-image v-for="(image,index) in productImages" :key="image" :src="image" :preview-src-list="productImages" :initial-index="index" preview-teleported fit="contain" /><div v-if="!productImages.length" class="m-gallery-empty"><el-icon><Picture /></el-icon><span>暂无商品图片</span></div></div>
    <section class="m-card m-product-info"><div class="m-product-prices"><strong class="m-price">{{ formatMoney(detail.product.price) }}</strong><s v-if="hasProductDiscount">{{ formatMoney(detail.product.original_price) }}</s><span class="m-muted">已售 {{ detail.product.sold_quantity || 0 }}</span></div><h2>{{ detail.product.name }}</h2><p class="m-muted">{{ detail.product.description }}</p><div class="m-tags"><span v-for="tag in productTags" :key="tag" class="m-pill">{{ tag }}</span></div></section>
    <section class="m-card"><button class="m-selection-row" @click="openAddToCart"><span>规格</span><strong>{{ detail.product.variants?.length ? `共 ${detail.product.variants.length} 款规格，点击选择` : '默认规格' }}</strong><b>›</b></button><div class="m-selection-row"><span>库存</span><strong>{{ detail.product.stock }} 件</strong></div></section>
    <section class="m-card" id="mini-product-reviews"><header class="m-review-heading"><h2>商品评价 <small>({{ detail.review_summary?.review_count || 0 }})</small></h2><span>{{ detail.review_summary?.review_count ? `★ ${Number(detail.review_summary.avg_rating).toFixed(1)}` : '暂无评分' }}</span></header>
      <div class="m-rating-filters"><button v-for="entry in [['','全部'],[5,'5星'],[4,'4星'],[3,'3星'],[2,'2星'],[1,'1星']]" :key="entry[0]" :class="{active:reviewFilters.rating===entry[0]}" @click="reviewFilters.rating=entry[0];handleReviewFilter()">{{ entry[1] }}</button></div>
      <form class="m-review-search" @submit.prevent="handleReviewFilter"><input v-model="reviewFilters.keywords" placeholder="搜索评价内容" /><button type="submit">搜索</button></form>
      <article v-for="review in reviewRows" :key="review.id" :id="`product-review-${review.id}`" class="m-review"><header><div class="m-review-avatar">{{ review.buyer_name?.slice(0,1) || '客' }}</div><div><strong>{{ review.buyer_name || '匿名买家' }}</strong><small>{{ review.create_time }}</small></div><span>{{ '★'.repeat(review.rating) }}</span></header><p>{{ review.content }}</p><el-image v-if="review.img" class="m-review-photo" :src="review.img" :preview-src-list="[review.img]" preview-teleported fit="cover" />
        <div v-if="review.merchant_reply && !(reviewReplies[review.id] || []).some(r=>r.content===review.merchant_reply)" class="m-review-reply"><b>商家：</b>{{ review.merchant_reply }}</div>
        <div v-for="reply in reviewReplies[review.id] || []" :key="reply.id" class="m-review-reply" @click="beginReviewComment(review,reply)"><b>{{ reply.user_name }}{{ reply.kind==='append' ? ' 追评' : '' }}：</b>{{ reply.content }}</div>
        <button class="m-quiet m-review-comment" @click="beginReviewComment(review)">{{ isOwnReview(review) ? '追加评价' : '回复' }}</button>
        <div v-if="customerReplyEditingId===review.id" class="m-review-editor"><textarea class="m-native-input" v-model="customerReplyDraft" maxlength="2000" placeholder="写下你的回复" /><div class="m-actions"><button class="m-secondary" @click="cancelCustomerReply">取消</button><button class="m-primary" :disabled="customerReplySaving || !customerReplyDraft.trim()" @click="saveCustomerReply(review)">发布</button></div></div>
      </article>
      <p v-if="!reviewRows.length && !reviewLoading" class="m-muted m-review-empty">还没有符合条件的评价</p><div v-if="reviewTotal>reviewPageSize" class="m-actions"><button class="m-secondary" :disabled="reviewPage<=1" @click="changeReviewPage(reviewPage-1)">上一页</button><span class="m-muted">{{ reviewPage }} / {{ Math.ceil(reviewTotal/reviewPageSize) }}</span><button class="m-secondary" :disabled="reviewPage*reviewPageSize>=reviewTotal" @click="changeReviewPage(reviewPage+1)">下一页</button></div>
    </section>
    <section class="m-card"><h2>商品介绍</h2><p class="m-product-description">{{ detail.product.description || '商家暂未补充商品介绍' }}</p><template v-if="aiDetail"><h3>{{ aiDetail.headline }}</h3><p class="m-product-description">{{ aiDetail.detail }}</p><p v-for="point in aiDetail.points || []" :key="point" class="m-muted">{{ point }}</p></template></section>
  </template>
</div>
<footer v-if="detail" class="m-footer m-product-footer"><button class="m-product-tool" @click="toggleFavorite" :disabled="favoriteBusy || !isCustomer"><el-icon><StarFilled v-if="favoriteSaved" /><Star v-else /></el-icon><span>{{ favoriteSaved ? '已收藏' : '收藏' }}</span></button><button class="m-product-tool" @click="router.push({path:'/manager/messages',query:{tab:'support'}})"><el-icon><ChatDotRound /></el-icon><span>客服</span></button><button class="m-secondary" :disabled="!productHasAvailableStock || !isCustomer" @click="openAddToCart">加入购物车</button><button class="m-primary" :disabled="!productHasAvailableStock || buyNowOpening || !isCustomer" @click="openBuyNow">{{ productHasAvailableStock ? '立即购买' : '暂时缺货' }}</button></footer>
    <SkuSelectionDialog class="m-sku"
      v-if="detail?.product"
      v-model="purchaseSheetVisible"
      :product="detail.product"
      :selected-key="selectedVariantKey"
      :quantity="buyNowQuantity"
      :max-quantity="buyNowMaxQuantity"
      :show-quantity="true"
      :loading="cartBusy || buyNowSaving"
      @update:selected-key="selectPurchaseVariant"
      @update:quantity="buyNowQuantity = $event"
      @confirm="confirmPurchaseSheet"
    >
      <template v-if="purchaseSheetAction === 'buy'" #extra>
        <el-form label-position="top" class="sku-checkout-form">
          <el-form-item label="收货地址">
            <el-select v-model="buyNowAddressId" placeholder="请选择收货地址" style="width: 100%">
              <el-option v-for="address in buyNowAddresses" :key="address.id" :label="addressLabel(address)" :value="address.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="优惠券">
            <div class="buy-now-coupon-field">
              <el-select v-model="buyNowCouponId" clearable placeholder="选择优惠券（可选）" style="width: 100%" no-data-text="暂无符合本次金额的优惠券">
                <el-option v-for="coupon in buyNowUsableCoupons" :key="coupon.claim_id" :value="coupon.claim_id" :label="couponLabel(coupon)" />
              </el-select>
              <el-button link type="primary" @click="router.push('/manager/offers')">去领券</el-button>
            </div>
          </el-form-item>
        </el-form>
        <div class="buy-now-breakdown"><span>商品金额</span><span>{{ formatMoney(buyNowTotals.subtotal) }}</span></div>
        <div class="buy-now-breakdown"><span>优惠券抵扣</span><span>− {{ formatMoney(buyNowTotals.discount) }}</span></div>
        <div class="buy-now-breakdown"><span>运费</span><span>{{ formatMoney(buyNowTotals.shipping) }}</span></div>
        <div class="buy-now-total"><span>应付金额</span><strong>{{ formatMoney(buyNowTotals.payable) }}</strong></div>
        <p class="buy-now-note">提交后生成待付款订单并保留库存。请在 {{ buyNowOrderSettings.unpaid_timeout_minutes || 30 }} 分钟内付款，超时取消后返还库存和优惠券。</p>
      </template>
      <template #footer="{ valid }">
        <el-button :disabled="cartBusy || buyNowSaving" @click="purchaseSheetVisible = false">取消</el-button>
        <el-button
          v-if="purchaseSheetAction === 'cart'"
          type="warning"
          :loading="cartBusy"
          :disabled="!valid || !productCanOrder"
          @click="confirmPurchaseSheet"
        >加入购物车</el-button>
        <el-button
          v-else
          type="danger"
          :loading="buyNowSaving"
          :disabled="!valid || !buyNowAddressId || !productCanOrder || !buyNowOrderSettings.checkout_enabled"
          @click="confirmPurchaseSheet"
        >立即购买</el-button>
      </template>
    </SkuSelectionDialog>
</div>
</template>
<script setup>
import MiniHeader from '@/components/mini/MiniHeader.vue'
import MiniSheet from '@/components/mini/MiniSheet.vue'
import { useProductDetail } from '@/composables/customer/ProductDetail'
defineOptions({ name: 'ProductDetail' })
const {
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
} = useProductDetail()

import {ChatDotRound} from '@element-plus/icons-vue'
</script>
<style scoped>

.m-product-scroll{padding:0 0 16px}.m-gallery{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;background:#fff;scrollbar-width:none}.m-gallery>.el-image{flex:0 0 100%;aspect-ratio:1;scroll-snap-align:center}.m-gallery-empty{display:grid;align-content:center;justify-items:center;gap:12px;width:100%;aspect-ratio:1;color:#b1bcc5;background:linear-gradient(135deg,#f3f5f7,#eceff2)}.m-gallery-empty .el-icon{font-size:42px}.m-product-info{border-radius:0 0 16px 16px}.m-product-info h2{font-size:18px;line-height:1.6;margin:12px 0 6px}.m-product-prices{display:flex;align-items:baseline;gap:10px}.m-product-prices .m-price{font-size:28px}.m-product-prices>s{color:#bac1c9;font-size:13px}.m-product-prices .m-muted{margin-left:auto}.m-tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}.m-selection-row{display:flex;gap:14px;align-items:center;min-height:40px;width:100%;border:0;background:none;text-align:left;font-size:13px}.m-selection-row>span{color:#9ba6af}.m-selection-row>strong{flex:1;font-size:13px;font-weight:400}.m-selection-row>b{color:#aab3bc;font-size:20px}.m-review-heading{display:flex;align-items:center;justify-content:space-between}.m-review-heading h2{margin:0}.m-review-heading small{font-size:12px;font-weight:400;color:#9aa5b0}.m-review-heading>span{color:#e59a4b;font-size:13px}.m-rating-filters{display:flex;overflow-x:auto;gap:8px;margin:16px 0 10px}.m-rating-filters>button{flex:none;padding:7px 15px;border:0;border-radius:18px;background:#f4f5f7;color:#8e99a4;font-size:12px}.m-rating-filters>.active{color:#e96c54;background:#fff0e9}.m-review-search{display:flex;gap:8px;border-radius:8px;padding:8px 10px;background:#f6f7f9}.m-review-search>input{width:0;flex:1;border:0;background:none;font-size:16px;outline:none}.m-review-search>button{border:0;background:none;font-size:12px;color:#8996a2}.m-review{padding:18px 0;border-bottom:1px solid #f0f2f4}.m-review>header{display:flex;align-items:center;gap:9px}.m-review-avatar{display:grid;place-items:center;width:30px;height:30px;border-radius:50%;background:#f0f2f6;color:#9aa5b0}.m-review header>div:nth-child(2){flex:1;display:grid;gap:4px}.m-review header strong{font-size:12px;font-weight:500}.m-review header small{font-size:10px;color:#adb5bd}.m-review header>span{color:#e8a358;font-size:11px}.m-review>p,.m-product-description{white-space:pre-wrap;line-height:1.85;font-size:13px;overflow-wrap:anywhere}.m-review-photo{width:76px;height:76px;border-radius:8px}.m-review-reply{padding:10px;margin-top:8px;background:#f7f8fa;border-radius:8px;font-size:12px;line-height:1.7;overflow-wrap:anywhere}.m-review-reply b{font-weight:500;color:#8c9eaa}.m-review-comment{display:block;margin-left:auto}.m-review-empty{text-align:center;padding:32px 0}.m-product-footer{gap:6px;padding-left:10px;padding-right:10px}.m-product-tool{display:grid;justify-items:center;gap:3px;min-width:36px;min-height:44px;border:0;background:none;color:#8595a0;font-size:10px}.m-product-tool .el-icon{font-size:19px}.m-product-footer .m-primary,.m-product-footer .m-secondary{flex:1;padding:8px 10px;font-size:12px}

</style>
