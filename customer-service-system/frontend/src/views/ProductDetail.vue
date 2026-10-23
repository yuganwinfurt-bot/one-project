<template>
  <div class="page-container product-detail-page" v-loading="loading">
    <div class="content-card detail-toolbar">
      <el-button :icon="ArrowLeft" @click="goBack">
        {{ returnLabel }}
      </el-button>
      <span class="detail-toolbar__title">商品详情</span>
    </div>

    <div v-if="error" class="content-card detail-error">
      <el-empty :description="error">
        <el-button type="primary" @click="load">重新加载</el-button>
        <el-button @click="goBack">
          {{ returnLabel }}
        </el-button>
      </el-empty>
    </div>

    <template v-else-if="detail">
      <section class="content-card product-hero">
        <div class="product-gallery" :class="{ 'product-gallery--out-of-stock': productOutOfStock }">
          <div class="product-gallery__stage">
            <el-image
              v-if="activeImageUrl"
              class="product-gallery__image"
              :src="activeImageUrl"
              :alt="`${detail.product.name}商品图 ${activeImageIndex + 1}`"
              :preview-src-list="productImages"
              :initial-index="activeImageIndex"
              preview-teleported
              fit="contain"
            />
            <div v-else class="product-gallery__empty">
              <el-icon :size="42"><Picture /></el-icon>
              <strong>暂无商品图片</strong>
              <span>商家还没有上传商品主图</span>
            </div>
            <div v-if="productOutOfStock" class="product-gallery__stock-overlay">
              <strong>缺货</strong>
            </div>
            <template v-if="productImages.length > 1">
              <el-button
                class="product-gallery__nav product-gallery__nav--prev"
                circle
                :icon="ArrowLeft"
                aria-label="上一张商品图"
                @click="stepProductImage(-1)"
              />
              <el-button
                class="product-gallery__nav product-gallery__nav--next"
                circle
                :icon="ArrowRight"
                aria-label="下一张商品图"
                @click="stepProductImage(1)"
              />
              <span class="product-gallery__counter">
                {{ activeImageIndex + 1 }} / {{ productImages.length }}
              </span>
            </template>
          </div>
          <div v-if="productImages.length > 1" class="product-gallery__thumbs">
            <button
              v-for="(imageUrl, index) in productImages"
              :key="imageUrl"
              class="product-gallery__thumb"
              :class="{ 'is-active': activeImageIndex === index }"
              type="button"
              :aria-label="`查看第 ${index + 1} 张商品图`"
              @click="activeImageIndex = index"
            >
              <el-image :src="imageUrl" fit="cover" />
            </button>
          </div>
          <div class="product-gallery__caption">
            {{ productImages.length ? `商品图片 ${activeImageIndex + 1} / ${productImages.length} · 点击图片可放大` : '商品图片由商家上传' }}
          </div>
          <div v-if="canEditProduct" class="product-gallery__upload">
            <el-button @click="imageManagerDialogVisible = true">编辑主图</el-button>
          </div>
        </div>

        <div class="product-overview">
          <div class="product-overview__tags">
            <el-tag v-for="tag in productTags" :key="tag" effect="plain" round>{{ tag }}</el-tag>
            <el-button
              v-if="canEditProduct"
              class="product-overview__edit-tags"
              link
              type="primary"
              :icon="Edit"
              @click="openTagsEditor"
            >
              编辑标签
            </el-button>
            <el-tag
              effect="light"
              round
              :type="detail.product.shelf_status === 'on_sale' && !productOutOfStock ? 'success' : 'info'"
            >
              {{ productOutOfStock && detail.product.shelf_status === 'on_sale' ? '缺货' : shelfLabel(detail.product.shelf_status) }}
            </el-tag>
            <el-tag
              effect="light"
              round
              :type="detail.product.review_status === 'pending_review' ? 'warning' : 'success'"
            >
              {{ reviewStatusLabel(detail.product.review_status) }}
            </el-tag>
          </div>

          <h1 class="product-overview__name">
            <button
              v-if="canEditProduct"
              class="product-overview__name-edit"
              type="button"
              title="点击编辑商品名称"
              @click="openNameEditor"
            >
              {{ detail.product.name }}
              <el-icon :size="16"><Edit /></el-icon>
            </button>
            <span v-else>{{ detail.product.name }}</span>
            <el-tag v-if="productBrandName" type="success" size="small">{{ productBrandName }}</el-tag>
          </h1>

          <div class="product-overview__rating">
            <template v-if="detail.review_summary.review_count">
              <el-rate :model-value="detail.review_summary.avg_rating" disabled allow-half />
              <strong>{{ detail.review_summary.avg_rating.toFixed(2) }}</strong>
              <span>{{ detail.review_summary.review_count }} 条评价</span>
            </template>
            <span v-else class="muted">暂无评价与评分</span>
          </div>

          <div v-if="isCustomer" class="customer-product-actions">
            <el-button
              class="buy-now-button"
              type="danger"
              :icon="Lightning"
              :disabled="!productHasAvailableStock || buyNowOpening || buyNowSaving"
              :loading="buyNowOpening || buyNowSaving"
              @click="openBuyNow"
            >
              立即购买
            </el-button>
            <el-button
              type="primary"
              plain
              :icon="ShoppingCart"
              :disabled="!productHasAvailableStock || cartBusy || buyNowOpening"
              :loading="cartBusy"
              @click="openAddToCart"
            >
              加入购物车
            </el-button>
            <el-button
              :icon="favoriteSaved ? StarFilled : Star"
              :disabled="favoriteBusy"
              :loading="favoriteBusy"
              @click.stop="toggleFavorite"
            >
              {{ favoriteSaved ? '取消收藏' : '收藏商品' }}
            </el-button>
          </div>

          <div class="product-price">
            <div class="product-price__heading">
              <span class="product-price__label">售价</span>
              <el-button v-if="canEditProduct && !detail.product.variants?.length" link type="primary" @click="openPricingEditor">
                编辑价格
              </el-button>
            </div>
            <div class="product-price__values">
              <strong>{{ formatMoney(selectedVariantPrice) }}</strong>
              <del v-if="hasProductDiscount">{{ formatMoney(selectedVariantOriginalPrice) }}</del>
              <el-tag v-if="hasProductDiscount" type="danger" effect="light" round>
                优惠 {{ formatPercent(detail.product.discount_percent) }}%
              </el-tag>
            </div>
          </div>

          <div class="product-overview__stats">
            <div class="overview-stat overview-stat--sales">
              <span>已售</span>
              <strong>{{ detail.order_summary.sold_quantity ?? 0 }}</strong>
              <small>件</small>
            </div>
            <div class="overview-stat">
              <span>库存</span>
              <button
                v-if="canEditProduct && !detail.product.variants?.length"
                class="overview-stat__value overview-stat__value--editable"
                type="button"
                title="点击编辑库存"
                @click="openStockEditor"
              >
                {{ detail.product.stock }}
              </button>
              <strong v-else>{{ selectedVariantStock }}</strong>
              <small>件</small>
            </div>
            <div class="overview-stat">
              <span>评价</span>
              <strong>{{ detail.review_summary.review_count }}</strong>
              <small>条</small>
            </div>
          </div>

          <div class="product-description">
            <div class="product-description__heading">
              <div class="section-label">商品介绍</div>
              <el-button v-if="canEditProduct" link type="primary" @click="openDescriptionEditor">
                编辑介绍
              </el-button>
            </div>
            <p>{{ detail.product.description || '暂无商品介绍' }}</p>
          </div>
        </div>
      </section>

      <section v-if="aiDetail || canEditProduct" class="content-card ai-detail-panel">
        <div class="section-heading">
          <div>
            <span class="ai-detail-panel__eyebrow">AI PRODUCT COPY</span>
            <h2>{{ aiDetail?.headline || '商品详情介绍' }}</h2>
            <p>AI 根据商品名称、类目和原有描述整理，发布前请人工核对；价格、销量与评价以实际数据为准。</p>
          </div>
          <div class="ai-detail-panel__actions">
            <el-tag type="success" effect="light" round>商品文案</el-tag>
            <el-button v-if="canEditProduct" @click="openAiDetailEditor">
              {{ aiDetail ? '编辑文案' : '添加文案' }}
            </el-button>
          </div>
        </div>
        <ul v-if="aiDetail?.selling_points?.length" class="ai-detail-panel__points">
          <li v-for="(point, index) in aiDetail.selling_points" :key="`${index}-${point}`">
            <span>{{ String(index + 1).padStart(2, '0') }}</span>
            {{ point }}
          </li>
        </ul>
        <p v-if="aiDetail?.detail" class="ai-detail-panel__body">{{ aiDetail.detail }}</p>
        <el-empty
          v-else
          class="ai-detail-panel__empty"
          description="还没有商品文案，商家可以添加或粘贴 AI 生成的内容"
          :image-size="64"
        />
      </section>

      <AfterSaleRiskCard v-if="canEditProduct" :risk="detail.after_sale_risk" :product="detail.product" @reviewed="detail.product.review_status = $event.review_status" />

      <section class="content-card rating-panel">
        <div class="section-heading">
          <div>
            <h2>商品评价与评级</h2>
            <p>评分来自该商品的买家评价</p>
          </div>
          <div class="rating-panel__summary">
            <strong>{{ detail.review_summary.avg_rating.toFixed(2) }}</strong>
            <span>/ 5 分</span>
          </div>
        </div>

        <div class="rating-panel__body">
          <div class="rating-distribution">
            <div
              v-for="bucket in ratingBuckets"
              :key="bucket.rating"
              class="rating-row"
            >
              <span>{{ bucket.rating }} 星</span>
              <span class="rating-row__track">
                <span
                  class="rating-row__fill"
                  :class="`rating-row__fill--${ratingTone(bucket.rating)}`"
                  :style="{ width: ratingWidth(bucket.count) }"
                ></span>
              </span>
              <span class="rating-row__count">{{ bucket.count }}</span>
            </div>
          </div>
          <div class="rating-summary-cards">
            <div>
              <span>评价总数</span>
              <strong>{{ detail.review_summary.review_count }}</strong>
            </div>
            <div>
              <span>低分评价（1–2 星）</span>
              <strong class="rating-summary-cards__bad">
                {{ detail.review_summary.bad_count }}
              </strong>
            </div>
            <div>
              <span>有效订单销量</span>
              <strong>{{ detail.order_summary.sold_quantity ?? 0 }} 件</strong>
            </div>
          </div>
        </div>
      </section>

      <section class="content-card reviews-panel">
        <div class="section-heading">
          <div>
            <h2>用户评价</h2>
            <p>共 {{ detail.review_summary.review_count }} 条 · 当前筛选 {{ reviewTotal }} 条；点击评论回复，自己的评价可追加评论。</p>
          </div>
        </div>

        <div class="review-filters">
          <el-input
            v-model="reviewFilters.keywords"
            class="review-filters__keyword"
            placeholder="搜索评价内容"
            clearable
            @keyup.enter="handleReviewFilter"
            @clear="handleReviewFilter"
          />
          <el-select v-model="reviewFilters.rating" placeholder="全部星级" clearable @change="handleReviewFilter">
            <el-option v-for="rating in [5, 4, 3, 2, 1]" :key="rating" :label="`${rating} 星`" :value="rating" />
          </el-select>
          <el-select v-model="reviewFilters.replyStatus" placeholder="全部回复状态" clearable @change="handleReviewFilter">
            <el-option label="已回复" value="replied" />
            <el-option label="未回复" value="unreplied" />
          </el-select>
          <el-button type="primary" @click="handleReviewFilter">筛选</el-button>
        </div>

        <ul v-if="reviewRows.length" v-loading="reviewLoading" class="review-list">
          <li
            v-for="review in reviewRows"
            :id="`product-review-${review.id}`"
            :key="review.id"
            class="review-item"
            :class="{ 'review-item--focused': focusReviewId === review.id }"
            role="button"
            tabindex="0"
            :aria-label="isOwnReview(review) ? '追加评论' : '回复评论'"
            @click="beginReviewComment(review)"
            @keydown.enter.self.prevent="beginReviewComment(review)"
          >
            <div class="review-item__head">
              <div class="review-item__author">
                <el-avatar class="review-item__avatar" :size="34">
                  {{ review.buyer_name?.slice(0, 1) || '匿' }}
                </el-avatar>
                <strong>{{ review.buyer_name || '匿名买家' }}</strong>
              </div>
              <el-rate :model-value="review.rating" disabled />
              <span class="review-item__score">{{ review.rating }} 分</span>
              <time>{{ review.create_time || '时间未知' }}</time>
            </div>
            <p>{{ review.content }}</p>
            <el-image
              v-if="review.img"
              class="review-item__image"
              :src="review.img"
              :alt="`${detail.product.name}买家评价图片`"
              title="点击放大评价图片"
              :preview-src-list="[review.img]"
              preview-teleported
              fit="cover"
              @click.stop
            />
            <div v-if="review.merchant_reply && !(reviewReplies[review.id] || []).some(reply => ['admin', 'user'].includes(reply.user_role) && reply.content === review.merchant_reply)" class="review-reply" @click.stop>
              <div class="review-reply__heading">商家回复</div>
              <p>{{ review.merchant_reply }}</p>
            </div>
            <div v-if="reviewReplies[review.id]?.length" class="customer-review-replies">
              <div
                v-for="customerReply in reviewReplies[review.id]"
                :key="customerReply.id"
                class="customer-review-reply"
                role="button"
                tabindex="0"
                aria-label="回复这条评论"
                @click.stop="beginReviewComment(review, customerReply)"
                @keydown.enter.self.prevent.stop="beginReviewComment(review, customerReply)"
              >
                <div class="customer-review-reply__heading">
                  <strong>{{ customerReply.user_name }}</strong>
                  <span>{{ customerReply.kind === 'append' ? '用户追加评论' : ['admin', 'user'].includes(customerReply.user_role) ? '商家回复' : '用户回复' }}{{ customerReply.reply_to_name && customerReply.kind !== 'append' ? ` · 回复 ${customerReply.reply_to_name}` : '' }}</span>
                  <time>{{ customerReply.create_time }}</time>
                </div>
                <p>{{ customerReply.content }}</p>
              </div>
            </div>
            <div v-if="customerReplyEditingId === review.id" class="review-reply-editor" @click.stop @keydown.stop>
              <strong>{{ replyTarget ? `回复 ${replyTarget.user_name}` : isOwnReview(review) ? '追加评论' : '回复评论' }}</strong>
              <el-input
                v-model="customerReplyDraft"
                type="textarea"
                :rows="3"
                maxlength="2000"
                show-word-limit
                :placeholder="isOwnReview(review) && !replyTarget ? '补充你的使用感受，原评价会保留' : '写下你的回复'"
              />
              <div class="review-reply-editor__actions">
                <el-button @click="cancelCustomerReply">取消</el-button>
                <el-button type="primary" :loading="customerReplySaving" @click="saveCustomerReply(review)">
                  {{ isOwnReview(review) && !replyTarget ? '发布追加评论' : '发布回复' }}
                </el-button>
              </div>
            </div>
          </li>
        </ul>
        <el-empty
          v-else-if="!reviewLoading"
          :description="reviewTotal ? '当前筛选条件下没有评价' : '当前条件下没有评价'"
          :image-size="72"
        />
        <div v-if="reviewTotal > reviewPageSize" class="review-pagination">
          <el-pagination
            :current-page="reviewPage"
            :page-size="reviewPageSize"
            :total="reviewTotal"
            background
            layout="total, prev, pager, next"
            @current-change="changeReviewPage"
          />
        </div>
      </section>
    </template>

    <SkuSelectionDialog
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

    <el-dialog v-model="descriptionDialogVisible" title="编辑商品介绍" width="620px">
      <el-input
        v-model="descriptionDraft"
        type="textarea"
        :rows="7"
        maxlength="10000"
        show-word-limit
        placeholder="介绍商品特点、规格或使用信息"
      />
      <template #footer>
        <el-button @click="descriptionDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="descriptionSaving" @click="saveDescription">
          保存介绍
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="nameDialogVisible" title="编辑商品名称" width="480px">
      <el-input
        v-model="nameDraft"
        maxlength="100"
        show-word-limit
        autofocus
        placeholder="请输入商品名称"
        @keyup.enter="saveProductName"
      />
      <template #footer>
        <el-button @click="nameDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="nameSaving" @click="saveProductName">
          保存名称
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="tagsDialogVisible" title="编辑商品标签" width="520px">
      <p class="product-tags-hint">可为商品设置多个标签；在商品首页选择任一标签，都能筛选到此商品。</p>
      <div class="product-tags-picker">
        <el-checkbox-group v-model="tagsDraft" class="product-tags-options">
          <el-checkbox
            v-for="tag in availableTagOptions"
            :key="tag"
            :label="tag"
            border
            :disabled="tagsDraft.length === 1 && tagsDraft.includes(tag)"
          >
            {{ tag }}
          </el-checkbox>
        </el-checkbox-group>
      </div>
      <div class="product-tags-footer">
        <el-button v-if="!customTagInputVisible" link type="primary" @click="customTagInputVisible = true">
          + 新增自定义标签
        </el-button>
        <div v-else class="product-tags-custom-input">
          <el-input
            v-model="customTagDraft"
            size="small"
            maxlength="50"
            placeholder="输入自定义标签"
            @keyup.enter="addCustomTag"
          />
          <el-button size="small" type="primary" @click="addCustomTag">添加</el-button>
          <el-button size="small" @click="customTagInputVisible = false">取消</el-button>
        </div>
        <span>已选 {{ tagsDraft.length }} 个，至少保留一个</span>
      </div>
      <template #footer>
        <el-button @click="tagsDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="tagsSaving" :disabled="!tagsDraft.length" @click="saveProductTags">
          保存标签
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="pricingDialogVisible" title="编辑原价和折扣" width="520px">
      <el-form label-position="top" class="product-pricing-form">
        <el-form-item label="商品原价">
          <el-input-number
            v-model="originalPriceDraft"
            :min="0.01"
            :precision="2"
            :step="10"
            controls-position="right"
          />
        </el-form-item>
        <el-form-item label="优惠幅度（%）">
          <el-input-number
            v-model="discountPercentDraft"
            :min="0"
            :max="99.99"
            :precision="2"
            :step="1"
            controls-position="right"
          />
          <p class="product-pricing-hint">例如输入 20，表示优惠 20%，售价为原价的 80%。</p>
        </el-form-item>
        <div class="product-pricing-preview">
          <span>折后售价</span>
          <strong>{{ formatMoney(discountedPricePreview) }}</strong>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="pricingDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="pricingSaving" @click="saveProductPricing">
          保存价格
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="stockDialogVisible" title="编辑库存" width="420px">
      <el-form label-position="top" class="product-stock-form">
        <el-form-item label="库存数量">
          <el-input-number
            v-model="stockDraft"
            :min="0"
            :max="2147483647"
            :precision="0"
            :step="1"
            controls-position="right"
          />
          <p class="product-pricing-hint">库存必须是 0 或更大的整数。</p>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="stockSaving" @click="saveProductStock">
          保存库存
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="imageManagerDialogVisible" title="编辑商品图片" width="720px">
      <p class="product-images-hint">按住图片拖动可调整顺序，第一张会作为商品主图；替换、下架或新增后会立即保存。</p>
      <div v-if="productImages.length" class="product-images-grid">
        <article
          v-for="(imageUrl, index) in productImages"
          :key="`${imageUrl}-${index}`"
          class="product-image-card"
          :class="{
            'is-dragging': draggedImageIndex === index,
            'is-drop-target': dragOverImageIndex === index && draggedImageIndex !== index
          }"
          @dragover.prevent="handleImageDragOver(index)"
          @drop.prevent.stop="dropProductImage(index)"
        >
          <el-image
            class="product-image-card__preview"
            :src="imageUrl"
            fit="cover"
            :preview-src-list="productImages"
            :initial-index="index"
            preview-teleported
            draggable="true"
            @dragstart.stop="startImageDrag($event, index)"
            @dragend="finishImageDrag"
          />
          <el-tag v-if="index === 0" class="product-image-card__main" type="success" effect="dark" size="small">主图</el-tag>
          <div class="product-image-card__actions">
            <el-upload
              :disabled="imageUploading"
              accept="image/jpeg,image/png,image/gif,image/webp"
              :show-file-list="false"
              :before-upload="validateProductImage"
              :http-request="createReplaceRequest(index)"
            >
              <el-button size="small" :loading="imageUploading">替换图片</el-button>
            </el-upload>
            <el-button size="small" type="danger" plain :disabled="imageUploading" @click="removeProductImage(index)">
              下架图片
            </el-button>
          </div>
        </article>
      </div>
      <el-empty v-else description="当前没有商品图片" :image-size="72" />
      <el-upload
        class="product-images-add"
        :disabled="imageUploading"
        accept="image/jpeg,image/png,image/gif,image/webp"
        :show-file-list="false"
        :before-upload="validateProductImage"
        :http-request="uploadProductImage"
      >
        <el-button type="primary" plain :loading="imageUploading">新增图片</el-button>
      </el-upload>
      <template #footer>
        <el-button @click="imageManagerDialogVisible = false">完成</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="aiDetailDialogVisible" title="编辑商品文案" width="680px">
      <el-form label-position="top">
        <el-form-item label="文案标题">
          <el-input v-model="aiHeadlineDraft" maxlength="120" show-word-limit placeholder="填写商品文案标题" />
        </el-form-item>
        <el-form-item label="商品卖点（每行一条）">
          <el-input
            v-model="aiPointsDraft"
            type="textarea"
            :rows="4"
            maxlength="2000"
            show-word-limit
            placeholder="例如：轻便易携带"
          />
        </el-form-item>
        <el-form-item label="详情正文">
          <el-input
            v-model="aiDetailDraft"
            type="textarea"
            :rows="8"
            maxlength="8000"
            show-word-limit
            placeholder="编辑商品详情文案"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="aiDetailDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="aiDetailSaving" @click="saveAiDetail">
          保存文案
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { customerCoupons, mallActivity, mallPortal } from '@/api/mall'
import { checkoutTotals, couponLabel } from '@/utils/checkout'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
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

defineOptions({ name: 'ProductDetail' })

const route = useRoute()
const router = useRouter()
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
  return route.path.startsWith('/manager/store/products/') ? 'store' : 'products'
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
</script>

<style scoped>
.product-detail-page {
  display: flex;
  flex-direction: column;
  gap: var(--app-space-gap);
}

.detail-toolbar {
  display: flex;
  align-items: center;
  gap: 14px;
}

.detail-toolbar__title {
  color: var(--app-text-secondary);
  font-size: 13px;
}

.detail-error {
  min-height: 280px;
  display: grid;
  place-items: center;
}

.product-hero {
  display: grid;
  grid-template-columns: minmax(280px, 0.9fr) minmax(0, 1.1fr);
  gap: clamp(24px, 4vw, 52px);
  padding: clamp(18px, 3vw, 32px);
}

.product-gallery {
  min-width: 0;
}

.product-gallery__stage {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 360px;
  aspect-ratio: 1 / 1;
  overflow: hidden;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
  background: linear-gradient(145deg, #f5f8f6, #edf4f1);
}

.product-gallery__nav {
  position: absolute;
  top: 50%;
  z-index: 2;
  transform: translateY(-50%);
  border-color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 2px 10px rgba(17, 33, 52, 0.14);
}

.product-gallery__nav--prev {
  left: 14px;
}

.product-gallery__nav--next {
  right: 14px;
}

.product-gallery__counter {
  position: absolute;
  right: 14px;
  bottom: 14px;
  z-index: 2;
  padding: 4px 9px;
  border-radius: 999px;
  color: white;
  background: rgba(17, 33, 52, 0.68);
  font-size: 12px;
  line-height: 1.4;
}

.product-gallery__image {
  width: 100%;
  height: 100%;
}

.product-gallery--out-of-stock .product-gallery__image,
.product-gallery--out-of-stock .product-gallery__empty,
.product-gallery--out-of-stock .product-gallery__thumb {
  filter: grayscale(1);
  opacity: 0.58;
}

.product-gallery__stock-overlay {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: grid;
  place-items: center;
  background: rgba(240, 242, 244, 0.15);
  pointer-events: none;
}

.product-gallery__stock-overlay strong {
  padding: 14px 28px 14px 36px;
  border: 5px solid currentColor;
  border-radius: 12px;
  color: #48525c;
  background: rgba(255, 255, 255, 0.84);
  font-size: clamp(48px, 6vw, 86px);
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: 8px;
  transform: rotate(-12deg);
}

.product-gallery__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 24px;
  color: var(--app-text-secondary);
  text-align: center;
}

.product-gallery__empty strong {
  color: var(--app-text);
  font-size: 15px;
}

.product-gallery__empty span,
.product-gallery__caption {
  font-size: 12px;
}

.product-gallery__caption {
  margin-top: 10px;
  color: var(--app-text-secondary);
  text-align: center;
}

.product-gallery__upload {
  display: flex;
  justify-content: center;
  margin-top: 12px;
}

.product-images-hint {
  margin: 0 0 16px;
  color: var(--app-text-secondary);
  font-size: 13px;
}

.product-images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 14px;
  max-height: min(52vh, 460px);
  overflow-y: auto;
  padding: 2px;
}

.product-image-card {
  position: relative;
  min-width: 0;
  padding: 8px;
  border: 1px solid var(--app-border);
  border-radius: 10px;
  background: var(--app-surface-muted, #f8fafb);
  transition: border-color 0.15s ease, opacity 0.15s ease, transform 0.15s ease;
}

.product-image-card.is-dragging {
  opacity: 0.5;
  transform: scale(0.98);
}

.product-image-card.is-drop-target {
  border-color: var(--app-primary);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--app-primary) 18%, transparent);
}

.product-image-card__preview {
  display: block;
  width: 100%;
  height: 132px;
  border-radius: 6px;
  background: white;
  cursor: grab;
}

.product-image-card__preview:active {
  cursor: grabbing;
}

.product-image-card__main {
  position: absolute;
  top: 14px;
  left: 14px;
}

.product-image-card__actions {
  display: flex;
  justify-content: space-between;
  gap: 6px;
  margin-top: 9px;
}

.product-images-add {
  margin-top: 16px;
}

.product-gallery__thumbs {
  display: flex;
  gap: 10px;
  margin-top: 14px;
  overflow-x: auto;
}

.product-gallery__thumb {
  flex: 0 0 64px;
  width: 64px;
  height: 64px;
  padding: 3px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: white;
  cursor: pointer;
}

.product-gallery__thumb :deep(.el-image) {
  width: 100%;
  height: 100%;
  border-radius: 5px;
}

.product-gallery__thumb.is-active {
  border: 2px solid var(--app-primary);
}

.product-overview {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}

.product-overview__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.product-overview__edit-tags {
  margin-left: 2px;
}

.product-tags-hint {
  margin: 0 0 12px;
  color: var(--app-text-secondary);
  font-size: 13px;
  line-height: 1.6;
}

.product-tags-picker {
  max-height: 240px;
  overflow-y: auto;
  padding: 2px;
}

.product-tags-options {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.product-tags-options :deep(.el-checkbox) {
  margin-right: 0;
}

.product-tags-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 14px;
  color: var(--app-text-secondary);
  font-size: 12px;
}

.product-tags-custom-input {
  display: flex;
  align-items: center;
  gap: 7px;
}

.product-tags-custom-input :deep(.el-input) {
  width: 175px;
}

.product-overview__name {
  margin: 18px 0 12px;
  color: var(--app-text);
  font-size: clamp(22px, 2.4vw, 30px);
  line-height: 1.35;
}

.product-overview__name-edit {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font: inherit;
  text-align: left;
}

.product-overview__name-edit .el-icon {
  color: var(--app-text-secondary);
  opacity: 0.55;
  transition: opacity 0.15s ease;
}

.product-overview__name-edit:hover .el-icon,
.product-overview__name-edit:focus-visible .el-icon {
  opacity: 1;
}

.product-overview__name-edit:focus-visible {
  border-radius: 4px;
  outline: 2px solid var(--app-primary);
  outline-offset: 4px;
}

.product-overview__rating {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 9px;
  color: var(--app-text-secondary);
  font-size: 13px;
}

.product-overview__rating strong {
  color: #d97706;
  font-size: 15px;
}

.customer-product-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.customer-product-actions :deep(.el-button) {
  height: 42px;
  margin: 0;
}

.customer-product-actions :deep(.buy-now-button) {
  min-width: 148px;
  border-color: #e4473d;
  background: #e4473d;
  box-shadow: 0 5px 13px rgba(228, 71, 61, 0.24);
  color: #fff;
  font-weight: 700;
}

.customer-product-actions :deep(.buy-now-button:hover),
.customer-product-actions :deep(.buy-now-button:focus-visible) {
  border-color: #cb382f;
  background: #cb382f;
  color: #fff;
}

.customer-product-actions :deep(.buy-now-button.is-disabled) {
  border-color: #e8a39e;
  background: #e8a39e;
  color: #fff;
}

.buy-now-note {
  color: var(--app-text-secondary);
  font-size: 13px;
}

.buy-now-total {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-radius: 9px;
  background: #f5f7f6;
  color: var(--app-text-secondary);
}

.buy-now-total strong {
  color: #e94b42;
  font-size: 22px;
}

.buy-now-note {
  margin: -6px 0 0;
}

.product-price {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 26px;
  padding: 18px 20px;
  border-radius: var(--app-radius-sm);
  background: #f7f6f1;
}

.product-price__heading,
.product-price__values {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.product-price__heading {
  justify-content: space-between;
}

.product-price__label {
  color: var(--app-text-secondary);
  font-size: 13px;
}

.product-price strong {
  color: #d94841;
  font-size: clamp(28px, 3vw, 38px);
  line-height: 1;
}

.product-price__values del {
  color: var(--app-text-secondary);
  font-size: 14px;
}

.product-pricing-form :deep(.el-input-number) {
  width: 100%;
}

.product-stock-form :deep(.el-form-item__content) {
  display: block;
}

.product-stock-form :deep(.el-input-number) {
  width: 100%;
}

.product-pricing-hint {
  margin: 7px 0 0;
  color: var(--app-text-secondary);
  font-size: 12px;
}

.product-pricing-preview {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 13px 15px;
  border-radius: 8px;
  background: #f6f8f7;
  color: var(--app-text-secondary);
}

.product-pricing-preview strong {
  color: #d94841;
  font-size: 22px;
}

.product-overview__stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin-top: 18px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
}

.overview-stat {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: baseline;
  gap: 4px 8px;
  padding: 14px 16px;
  color: var(--app-text-secondary);
  font-size: 12px;
}

.overview-stat__heading {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.overview-stat + .overview-stat {
  border-left: 1px solid var(--app-border);
}

.overview-stat strong {
  grid-column: 1;
  color: var(--app-text);
  font-size: 22px;
}

.overview-stat__value {
  grid-column: 1;
  justify-self: start;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--app-text);
  font-size: 22px;
  font-weight: 700;
  line-height: inherit;
}

.overview-stat__value--editable {
  cursor: pointer;
}

.overview-stat__value--editable:hover,
.overview-stat__value--editable:focus-visible {
  color: var(--app-primary);
}

.overview-stat small {
  grid-column: 2;
  grid-row: 2;
  font-size: 12px;
}

.overview-stat--sales strong {
  color: var(--app-primary);
}

.product-description {
  margin-top: 24px;
}

.product-description__heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.section-label {
  color: var(--app-text);
  font-size: 14px;
  font-weight: 600;
}

.product-description p {
  margin: 8px 0 0;
  color: var(--app-text-secondary);
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
}

.ai-detail-panel {
  padding: 24px 28px;
}

.ai-detail-panel .section-heading {
  align-items: flex-start;
}

.ai-detail-panel__actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.ai-detail-panel__empty {
  padding: 12px 0 0;
}

.ai-detail-panel__eyebrow {
  display: block;
  margin-bottom: 6px;
  color: #168b75;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.15em;
}

.ai-detail-panel h2 {
  margin: 0;
  color: var(--app-text);
  font-size: 20px;
}

.ai-detail-panel .section-heading p {
  margin: 6px 0 0;
  color: var(--app-text-secondary);
  font-size: 12px;
}

.ai-detail-panel__points {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin: 20px 0;
  padding: 0;
  list-style: none;
}

.ai-detail-panel__points li {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  padding: 13px;
  border: 1px solid #dcebe5;
  border-radius: 10px;
  background: #f6faf7;
  color: #284452;
  font-size: 13px;
  line-height: 1.6;
}

.ai-detail-panel__points li span {
  flex: 0 0 auto;
  color: #16967d;
  font-size: 11px;
  font-weight: 700;
}

.ai-detail-panel__body {
  margin: 0;
  color: #526a78;
  font-size: 14px;
  line-height: 1.9;
  white-space: pre-line;
}

@media (max-width: 760px) {
  .ai-detail-panel__points {
    grid-template-columns: 1fr;
  }
}

.rating-panel,
.reviews-panel {
  padding: 22px 26px;
}

.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.section-heading h2 {
  margin: 0;
  color: var(--app-text);
  font-size: 17px;
}

.section-heading p {
  margin: 5px 0 0;
  color: var(--app-text-secondary);
  font-size: 12px;
}

.rating-panel__summary {
  display: flex;
  align-items: baseline;
  gap: 5px;
  color: var(--app-text-secondary);
}

.rating-panel__summary strong {
  color: #d97706;
  font-size: 28px;
}

.rating-panel__body {
  display: grid;
  grid-template-columns: minmax(240px, 1fr) minmax(260px, 1fr);
  gap: 32px;
  margin-top: 20px;
}

.rating-distribution {
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.rating-row {
  display: grid;
  grid-template-columns: 42px minmax(80px, 1fr) 32px;
  align-items: center;
  gap: 10px;
  color: var(--app-text-secondary);
  font-size: 12px;
}

.rating-row__track {
  height: 9px;
  overflow: hidden;
  border-radius: 999px;
  background: #edf1f0;
}

.rating-row__fill {
  display: block;
  height: 100%;
  border-radius: inherit;
}

.rating-row__fill--bad {
  background: #ef6b62;
}

.rating-row__fill--mid {
  background: #9aa8b8;
}

.rating-row__fill--good {
  background: var(--app-primary-light);
}

.rating-row__count {
  text-align: right;
}

.rating-summary-cards {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.rating-summary-cards > div {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 13px 15px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-sm);
}

.rating-summary-cards > div:last-child {
  grid-column: 1 / -1;
}

.rating-summary-cards span {
  color: var(--app-text-secondary);
  font-size: 12px;
}

.rating-summary-cards strong {
  color: var(--app-text);
  font-size: 20px;
}

.rating-summary-cards .rating-summary-cards__bad {
  color: #dc4b4b;
}

.review-list {
  margin: 16px 0 0;
  padding: 0;
  list-style: none;
}

.review-filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-top: 18px;
}

.review-filters__keyword {
  width: min(280px, 100%);
}

.review-filters :deep(.el-select) {
  width: 150px;
}

.review-item {
  padding: 16px 0;
  border-top: 1px solid var(--app-border);
  cursor: pointer;
}

.review-item:focus-visible, .customer-review-reply:focus-visible {
  outline: 2px solid var(--app-primary);
  outline-offset: 3px;
}

.review-item--focused {
  scroll-margin-top: 110px;
  border-radius: 10px;
  background: #eef8f4;
  box-shadow: 0 0 0 2px rgba(20, 157, 128, 0.32);
}

.review-item__head {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.review-item__author {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 4px;
  color: var(--app-text);
  font-size: 13px;
}

.review-item__avatar {
  flex: none;
  background: #e5f1ec;
  color: #168d76;
  font-weight: 700;
}

.review-item__score {
  color: #a16207;
  font-size: 12px;
}

.review-item time {
  margin-left: auto;
  color: var(--app-text-secondary);
  font-size: 12px;
}

.review-item p {
  margin: 10px 0 0;
  color: var(--app-text);
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-wrap;
}

.review-item__image {
  width: 96px;
  height: 96px;
  margin-top: 10px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  cursor: zoom-in;
}

.review-item__actions {
  margin-top: 8px;
}

.review-reply {
  margin-top: 12px;
  padding: 12px 14px;
  border-left: 3px solid var(--app-primary-light);
  border-radius: 7px;
  background: #f4f8f6;
}

.review-reply__heading {
  color: var(--app-primary);
  font-size: 12px;
  font-weight: 600;
}

.review-reply p {
  margin: 6px 0 0;
  color: var(--app-text);
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
}

.review-reply-editor {
  margin-top: 12px;
}

.review-reply-editor__actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

.customer-review-replies {
  display: grid;
  gap: 8px;
  margin-top: 12px;
}

.customer-review-reply {
  padding: 10px 12px;
  border-left: 3px solid #c9d9d5;
  border-radius: 7px;
  background: #f8faf9;
}

.customer-review-reply__heading {
  display: flex;
  align-items: baseline;
  gap: 7px;
  color: var(--app-text-secondary);
  font-size: 12px;
}

.customer-review-reply__heading strong {
  color: var(--app-primary);
}

.customer-review-reply__heading time {
  margin-left: auto;
}

.customer-review-reply p {
  margin: 6px 0 0;
  color: var(--app-text);
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
}

.review-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}

.muted {
  color: var(--app-text-secondary);
}

.buy-now-coupon-field { width: 100%; display: flex; gap: 10px; align-items: center; }
.buy-now-breakdown { display: flex; justify-content: space-between; margin: 10px 4px; color: var(--app-text-secondary); font-size: 13px; }

@media (max-width: 860px) {
  .product-hero,
  .rating-panel__body {
    grid-template-columns: 1fr;
  }

  .product-gallery__stage {
    min-height: 240px;
  }
}

@media (max-width: 560px) {
  .rating-panel,
  .reviews-panel {
    padding: 18px;
  }

  .product-overview__stats {
    grid-template-columns: 1fr;
  }

  .overview-stat + .overview-stat {
    border-top: 1px solid var(--app-border);
    border-left: 0;
  }

  .rating-panel__body {
    gap: 20px;
  }
}
</style>
