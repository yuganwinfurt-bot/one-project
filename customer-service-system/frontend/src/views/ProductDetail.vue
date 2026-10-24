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
