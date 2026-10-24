<template>
  <main class="mini-store" :class="{ 'mini-store--staff': !isCustomer }" :style="{'--mini-vh': miniViewportHeight}">
    <div class="mini-store__shell">
      <header v-if="!miniPage" class="mini-header">
        <div class="mini-header__brand">
          <strong>{{ activeTab === 'profile' ? '个人中心' : shopName }}</strong>
          <div class="mini-header__actions">
            <button type="button" class="mini-header__browser" @click="openMiniPage('messages', {tab:'inbox'})">消息 <b v-if="unreadMessages" class="mini-unread">{{ unreadMessages > 99 ? '99+' : unreadMessages }}</b></button>
            <button class="mini-header__browser" type="button" title="打开用户商品浏览页" @click="openUserBrowserPage">跳转浏览器</button>
            <button v-if="user && !isCustomer" class="mini-header__back" type="button" @click="router.push('/manager/home')">返回后台</button>
          </div>
        </div>
        <form v-if="['home','category'].includes(activeTab)" class="mini-search" role="search" @submit.prevent="search">
          <el-icon><Search /></el-icon>
          <input v-model="keyword" aria-label="搜索商品" placeholder="点击前往搜索" />
          <button v-if="keyword" type="button" aria-label="清空搜索" @click="keyword = ''; search()">×</button>
        </form>
      </header>

      <div ref="miniContent" class="mini-content" :class="{'mini-content--detail':miniPage}" v-loading="loading">
        <section v-if="miniPage" class="mini-shared-page">

          <router-view v-slot="{ Component }"><component :is="Component" :key="route.path" v-on="route.path === '/mini-store/cart' ? {'cart-updated': syncCartCount} : {}" /></router-view>
        </section>
        <section v-else-if="activeTab === 'home'" class="mini-home">
          <section class="mini-hero" aria-label="商城推荐">
            <el-carousel v-if="portal.ads?.length" height="270px" :interval="5000" :autoplay="portal.ads.length > 1" arrow="always">
              <el-carousel-item v-for="ad in portal.ads" :key="ad.id">
                <button class="mini-hero__slide" type="button" @click="openAd(ad)">
                  <img v-if="ad.image_url" :src="ad.image_url" :alt="ad.name" />
                  <span class="mini-hero__shade"></span>
                  <span class="mini-hero__caption"><small>精选推荐</small><strong>{{ ad.name }}</strong><span>进店看看 <b>›</b></span></span>
                </button>
              </el-carousel-item>
            </el-carousel>
            <button v-else class="mini-hero__fallback" type="button" @click="scrollToProducts">
              <span class="mini-hero__fallback-copy"><small>GOOD THINGS, EVERY DAY</small><strong>把喜欢的好物<br />带回家</strong><span>逛逛精选商品　›</span></span>
              <span class="mini-hero__shape" aria-hidden="true">好物</span>
            </button>
          </section>

          <section v-if="categories.length" class="mini-categories" aria-label="商品分类">
            <button v-for="(category, index) in categories.slice(0, 10)" :key="category" type="button" @click="openCategory(category)">
              <span class="mini-categories__icon">{{ categoryIcon(category, index) }}</span>
              <span>{{ category }}</span>
            </button>
          </section>

          <section v-if="portal.coupons?.length" id="mini-coupons" class="mini-section mini-coupons">
            <div class="mini-section__heading"><div><small>MEMBER BENEFITS</small><h2>优惠券</h2></div><span>好券限时领</span></div>
            <article v-for="coupon in portal.coupons.slice(0, 4)" :key="coupon.id" class="mini-coupon">
              <div class="mini-coupon__amount"><small>¥</small>{{ money(coupon.discount) }}<span v-if="Number(coupon.min_amount) > 0">满{{ money(coupon.min_amount) }}可用</span><span v-else>无门槛</span></div>
              <div class="mini-coupon__details"><strong>{{ coupon.name }}</strong><span>有效期至 {{ formatDate(coupon.ends_at) }}</span></div>
              <button type="button" :disabled="couponButtonState(coupon).disabled || claimingId === coupon.id" @click="claim(coupon)">{{ claimingId === coupon.id ? '领取中' : couponButtonState(coupon).label }}</button>
            </article>
          </section>

          <section v-if="groupRules.length" class="mini-section mini-groups">
            <div class="mini-section__heading"><div><small>JOIN TO SAVE</small><h2>拼团优惠</h2></div><span>邀请好友一起买</span></div>
            <button v-for="rule in groupRules.slice(0, 3)" :key="rule.id" class="mini-group" type="button" @click="openGroup(rule)">
              <span class="mini-group__badge">{{ rule.target_size }}人团</span><span class="mini-group__name">{{ rule.name }}</span><strong>¥{{ money(rule.price) }}<small> / 人</small></strong><span class="mini-group__arrow">›</span>
            </button>
          </section>

          <section v-if="portal.topics?.length" class="mini-section">
            <div class="mini-section__heading"><div><small>SHOPPING STORIES</small><h2>逛逛专题</h2></div></div>
            <div class="mini-topics">
              <button v-for="topic in portal.topics.slice(0, 4)" :key="topic.id" type="button" @click="openTopic(topic)">
                <img v-if="topic.image_url" :src="topic.image_url" :alt="topic.name" />
                <span v-else class="mini-topics__placeholder">精选专题</span>
                <strong>{{ topic.name }}</strong><small>{{ topic.content }}</small>
              </button>
            </div>
          </section>

          <section id="mini-products" class="mini-section mini-product-section">
            <div class="mini-section__heading"><div><small>HAND PICKED FOR YOU</small><h2>{{ keyword ? '搜索结果' : '猜你喜欢' }}</h2></div><button type="button" @click="showCategoryTab">全部分类　›</button></div>
            <div v-if="products.length" class="mini-products">
              <button v-for="product in products" :key="product.id" class="mini-product" type="button" @click="openProduct(product)">
                <div class="mini-product__image"><img v-if="product.image_url" :src="product.image_url" :alt="product.name" /><span v-else>好物</span><small v-if="product.has_variants">多规格</small></div>
                <strong>{{ product.name }}</strong><span class="mini-product__description">{{ product.description || product.category || '精选好物' }}</span>
                <span class="mini-product__rating">{{ Number(product.review_count || 0) ? `★ ${Number(product.avg_rating || 0).toFixed(1)} · ${product.review_count} 条评价` : '暂无评价' }}</span><span class="mini-product__price"><b>¥{{ money(product.price) }}</b><small>已售 {{ product.sold_quantity || 0 }}</small></span>
              </button>
            </div>
            <el-empty v-else-if="!loading" description="暂时没有找到商品" />
            <button v-if="total > products.length" class="mini-load-more" type="button" :disabled="loading" @click="loadMore">{{ loading ? '加载中…' : '查看更多商品' }}</button>
          </section>
        </section>

        <section v-else-if="activeTab === 'category'" class="mini-category-page">
          <div class="mini-section__heading"><div><small>FIND WHAT YOU NEED</small><h2>全部分类</h2></div></div>
          <div class="mini-category-page__list">
            <button type="button" :class="{ active: !selectedCategory }" @click="openCategory('')">全部商品</button>
            <button v-for="(category, index) in categories" :key="category" type="button" :class="{ active: selectedCategory === category }" @click="openCategory(category)">{{ categoryIcon(category, index) }}　{{ category }}</button>
          </div>
          <div class="mini-products">
            <button v-for="product in products" :key="product.id" class="mini-product" type="button" @click="openProduct(product)">
              <div class="mini-product__image"><img v-if="product.image_url" :src="product.image_url" :alt="product.name" /><span v-else>好物</span><small v-if="product.has_variants">多规格</small></div>
              <strong>{{ product.name }}</strong><span class="mini-product__description">{{ product.description || product.category || '精选好物' }}</span>
              <span class="mini-product__rating">{{ Number(product.review_count || 0) ? `★ ${Number(product.avg_rating || 0).toFixed(1)} · ${product.review_count} 条评价` : '暂无评价' }}</span><span class="mini-product__price"><b>¥{{ money(product.price) }}</b><small>已售 {{ product.sold_quantity || 0 }}</small></span>
            </button>
          </div>
          <el-empty v-if="!loading && !products.length" description="这个分类暂时没有商品" />
          <button v-if="total > products.length" class="mini-load-more" type="button" :disabled="loading" @click="loadMore">{{ loading ? '加载中…' : '查看更多商品' }}</button>
        </section>
        <section v-else-if="activeTab === 'profile'" class="mini-profile-page">
          <template v-if="isCustomer">
            <section class="mini-me-banner"><div class="mini-me-avatar"><img v-if="user?.avatar" :src="user.avatar" alt="头像" /><span v-else>{{ (user?.name || user?.username || '我').slice(0,1) }}</span></div><div><strong>{{ user?.name || user?.username }}</strong><p>{{ user?.username }}</p></div><button type="button" @click="openMiniPage('profile')">编辑 ›</button></section>
            <section class="mini-me-card"><header><strong>我的订单</strong><button type="button" @click="openMiniPage('orders')">全部订单 ›</button></header><div class="mini-order-shortcuts"><button v-for="entry in [['unpaid','◷','待付款'],['paid','▣','待发货'],['shipped','⌁','待收货'],['review','☆','待评价']]" :key="entry[0]" type="button" @click="openMiniPage('orders',{status:entry[0]})"><span>{{ entry[1] }}</span>{{ entry[2] }}</button></div></section>
            <section class="mini-me-card mini-me-services"><button v-for="entry in [['favorites','♡','我的收藏'],['messages','◌','我的消息'],['support','♧','联系客服'],['offers','◇','优惠团购'],['feedback','✎','意见反馈'],['help','ⓘ','公告帮助']]" :key="entry[0]" type="button" @click="openMiniPage(entry[0] === 'support' ? 'messages' : entry[0],entry[0] === 'support' ? {tab:'support'} : {})"><span>{{ entry[1] }}<i v-if="entry[0] === 'messages' && unreadMessages">{{ unreadMessages > 99 ? '99+' : unreadMessages }}</i></span>{{ entry[2] }}</button></section>
            <section class="mini-me-card mini-me-settings"><button type="button" @click="showAddresses">收货地址 <span>›</span></button><button type="button" @click="openMiniPage('profile')">个人资料 <span>›</span></button><button type="button" @click="openMiniPage('password')">账号安全 <span>›</span></button></section>
            <div class="mini-me-signout"><button type="button" @click="switchBuyerAccount">切换买家账号</button><button type="button" @click="signOutBuyerAccount">退出登录</button></div>
          </template>
          <section v-else class="mini-login-card">
            <div class="mini-login-card__avatar">♡</div>
            <h2>欢迎来到商城</h2>
            <p>登录买家账号后，可以购买商品、查看购物车并管理收货地址。</p>
            <el-button type="primary" @click="openMiniLogin">用户登录 / 切换买家账号</el-button>
          </section>
        </section>
        <section v-else-if="activeTab === 'login'" class="mini-auth-page">
          <button class="mini-addresses-back" type="button" @click="goProfile">‹　返回我的</button>
          <section class="mini-login-card">
            <div class="mini-login-card__avatar">{{ miniAuthMode === 'login' ? '♡' : '+' }}</div>
            <h2>{{ miniAuthMode === 'login' ? '买家登录' : '注册买家账号' }}</h2>
            <p>账号操作在商城内完成，登录后会回到这里。</p>
            <el-form ref="miniAuthFormRef" :model="miniAuthForm" :rules="miniAuthRules" class="mini-auth-form" @keyup.enter="submitMiniAuth">
              <el-form-item prop="username"><el-input v-model="miniAuthForm.username" autocomplete="username" placeholder="买家账号" /></el-form-item>
              <el-form-item prop="password"><el-input v-model="miniAuthForm.password" type="password" autocomplete="current-password" show-password placeholder="密码" /></el-form-item>
              <el-form-item v-if="miniAuthMode === 'register'" prop="confirmPassword"><el-input v-model="miniAuthForm.confirmPassword" type="password" autocomplete="new-password" show-password placeholder="确认密码" /></el-form-item>
              <el-button type="primary" :loading="miniAuthBusy" @click="submitMiniAuth">{{ miniAuthMode === 'login' ? '登录商城' : '注册账号' }}</el-button>
            </el-form>
            <button class="mini-auth-toggle" type="button" @click="toggleMiniAuthMode">{{ miniAuthMode === 'login' ? '没有账号？立即注册' : '已有账号？返回登录' }}</button>
          </section>
        </section>
      </div>

      <nav v-if="showTabbar" class="mini-tabbar" aria-label="商城导航">
        <button type="button" :class="{ active: activeTab === 'home' }" @click="goHome">
          <svg class="mini-tabbar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3.5 14.1 9.9 20.5 12l-6.4 2.1L12 20.5l-2.1-6.4L3.5 12l6.4-2.1L12 3.5Z"/><circle cx="12" cy="12" r="9"/></svg>
          <span>精选</span>
        </button>
        <button type="button" :class="{ active: activeTab === 'category' }" @click="showCategoryTab">
          <svg class="mini-tabbar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><rect x="14" y="14" width="6" height="6" rx="1"/></svg>
          <span>分类</span>
        </button>
        <button type="button" :class="{ active: activeTab === 'cart' }" @click="goCart">
          <svg class="mini-tabbar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3.5 4h2l2.1 11.1a2 2 0 0 0 2 1.6h8.8a2 2 0 0 0 1.9-1.5L22 8H6.1"/><circle cx="10" cy="20" r="1.2"/><circle cx="18" cy="20" r="1.2"/></svg>
          <span>购物车</span><i v-if="cartCount">{{ cartCount > 99 ? '99+' : cartCount }}</i>
        </button>
        <button type="button" :class="{ active: activeTab === 'profile' || (miniPage && !route.path.includes('/products/') && activeTab !== 'cart') }" @click="goProfile">
          <svg class="mini-tabbar__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="3.5"/><path d="M4.5 20a7.5 7.5 0 0 1 15 0"/></svg>
          <span>我的</span>
        </button>
      </nav>
    </div>

    <el-dialog v-model="topicVisible" :title="selectedTopic?.name || '专题商品'" width="min(680px, 92vw)">
      <p class="mini-dialog-copy">{{ selectedTopic?.content }}</p>
      <div v-loading="topicLoading" class="mini-topic-products">
        <button v-for="product in topicProducts" :key="product.id" type="button" @click="openProduct(product)"><img v-if="product.image_url" :src="product.image_url" :alt="product.name" /><strong>{{ product.name }}</strong><span>¥{{ money(product.price) }}</span></button>
      </div>
      <el-empty v-if="!topicLoading && !topicProducts.length" description="专题暂未关联在售商品" />
    </el-dialog>
  </main>
</template>

<script setup>
import '@/assets/css/mini-mobile.css'
import { computed, onMounted, onUnmounted, watch, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { loginApi, registerApi } from '@/api/auth'
import { getStorefrontProducts } from '@/api/ecommerce'
import { getCart, getCustomerMessages } from '@/api/customer'
import { claimCoupon, customerCoupons, mallActivity, mallPortal, mallTopicProducts } from '@/api/mall'
import { logout as clearAuth } from '@/utils/auth'
import { useUser } from '@/utils/user'

const router = useRouter()
const route = useRoute()
const { userInfo, saveLoginData, reloadUser } = useUser()
const user = computed(() => userInfo.value)
const isCustomer = computed(() => userInfo.value?.role === 'customer')
const shopName = ref('商城精选')
const miniPage = computed(() => route.path !== '/mini-store')
const miniContent = ref(null)
const miniViewportHeight = ref('100dvh')
const showTabbar = computed(() => !miniPage.value || ['/mini-store/cart','/mini-store/favorites'].includes(route.path) || (route.path === '/mini-store/messages' && !route.query.afterSaleId && !route.query.conversationId && route.query.tab !== 'support'))
function fitMiniViewport() { miniViewportHeight.value = `${window.visualViewport?.height || window.innerHeight}px` }
const activeTab = computed({
  get: () => miniPage.value ? (route.path === '/mini-store/cart' ? 'cart' : 'detail') : (['home','category','profile','login'].includes(route.query.tab) ? route.query.tab : 'home'),
  set: tab => router.push({path:'/mini-store',query:tab === 'home' ? {} : {tab}})
})
const unreadMessages = ref(0)
let buyerTimer
function syncCartCount(items) {
  cartCount.value = (Array.isArray(items) ? items : []).reduce((sum,item)=>sum + Number(item.quantity || 0), 0)
}
function refreshBuyerState() { if (isCustomer.value) void loadBuyerState() }
async function refreshMessages() {
  if (!isCustomer.value) { unreadMessages.value = 0; return }
  try { unreadMessages.value = Number((await getCustomerMessages()).data?.unread_count || 0) } catch {}
}
function openMiniPage(path, query = {}) {
  if (!isCustomer.value && !['help'].includes(path)) { router.push({path:'/mini-store',query:{tab:'login',next:`/mini-store/${path}`}}); return }
  router.push({path:`/mini-store/${path}`,query})
}
watch(() => `${route.path}|${route.path === '/mini-store' ? route.query.tab || '' : ''}`, () => { if (miniContent.value) miniContent.value.scrollTop = 0; refreshMessages(); if (isCustomer.value) loadBuyerState() })
watch(() => userInfo.value?.id, () => { refreshMessages(); if (isCustomer.value) loadBuyerState() })
const miniAuthMode = ref('login')
const miniAuthForm = reactive({ username: '', password: '', confirmPassword: '' })
const miniAuthFormRef = ref(null)
const miniAuthBusy = ref(false)
const miniAuthRules = computed(() => {
  const rules = {
    username: [{ required: true, message: '请输入买家账号', trigger: 'blur' }],
    password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
  }
  if (miniAuthMode.value === 'register') {
    rules.password.push({ min: 6, max: 64, message: '密码长度为 6 到 64 位', trigger: 'blur' })
    rules.confirmPassword = [{ required: true, message: '请确认密码', trigger: 'blur' }, { validator: validateMiniConfirmPassword, trigger: 'blur' }]
  }
  return rules
})
const keyword = ref('')
const selectedCategory = ref('')
const portal = ref({})
const products = ref([])
const categories = ref([])
const couponClaims = ref([])
const cartCount = ref(0)
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const claimingId = ref(null)
const topicVisible = ref(false)
const topicLoading = ref(false)
const selectedTopic = ref(null)
const topicProducts = ref([])
const groupRules = computed(() => portal.value['group-rules'] || [])
function money(value) { return Number(value || 0).toFixed(2).replace(/\.00$/, '') }
function formatDate(value) { return value ? String(value).slice(0, 10) : '长期有效' }
function categoryIcon(name, index) {
  const value = String(name || '')
  if (/家|居|家具/.test(value)) return '⌂'
  if (/餐|食|饮|食品/.test(value)) return '♨'
  if (/数码|电器|手机/.test(value)) return '▣'
  if (/服|鞋|包/.test(value)) return '♧'
  if (/美|护|妆/.test(value)) return '✿'
  if (/母婴|儿童|玩具/.test(value)) return '♡'
  return ['◇', '▤', '✦', '◉'][index % 4]
}

async function loadProducts({ append = false } = {}) {
  if (loading.value) return
  loading.value = true
  try {
    const response = await getStorefrontProducts({
      page: append ? page.value + 1 : 1,
      page_size: 12,
      keywords: keyword.value.trim() || undefined,
      category: selectedCategory.value || undefined
    })
    const data = response.data || {}
    products.value = append ? [...products.value, ...(data.list || [])] : (data.list || [])
    categories.value = data.categories || categories.value
    total.value = data.total || 0
    page.value = append ? page.value + 1 : 1
  } catch (error) {
    ElMessage.error(error?.message || '商品加载失败')
  } finally { loading.value = false }
}

async function loadMore() { await loadProducts({ append: true }) }
function search() {
  selectedCategory.value = ''
  if (isCustomer.value && keyword.value.trim()) mallActivity({ kind: 'search', keyword: keyword.value.trim().slice(0, 100) }).catch(() => {})
  loadProducts()
}
function openCategory(category) {
  selectedCategory.value = category
  activeTab.value = 'category'
  loadProducts()
}
function goHome() {
  activeTab.value = 'home'
  if (selectedCategory.value) { selectedCategory.value = ''; loadProducts() }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
function showCategoryTab() {
  activeTab.value = 'category'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
function scrollToProducts() { document.getElementById('mini-products')?.scrollIntoView({ behavior: 'smooth', block: 'start' }) }
function openProduct(product) {
  const id = Number(typeof product === 'object' ? product.id : product)
  if (Number.isInteger(id) && id > 0) { topicVisible.value = false; router.push({path:`/mini-store/products/${id}`,query:{from:'store'}}) }
}
function openAd(ad) {
  if (ad.product_id) { openProduct({ id: ad.product_id }); return }
  const link = String(ad.link || '').trim()
  if (!link) return
  try {
    const target = new URL(link, window.location.origin)
    const isLocalBackend = target.origin === window.location.origin && (target.pathname === '/manager' || target.pathname.startsWith('/manager/'))
    if (isLocalBackend) { ElMessage.info('该广告暂不支持在商城内打开'); return }
    if (target.protocol === 'http:' || target.protocol === 'https:') window.open(target.href, '_blank', 'noopener,noreferrer')
  } catch { ElMessage.warning('广告链接无效') }
}
function couponButtonState(coupon) {
  if (!isCustomer.value) return { label: '买家登录', disabled: false }
  const claim = couponClaims.value.find(item => item.id === coupon.id || item.claim_id && item.id === coupon.id)
  if (claim?.claim_id) return { label: claim.used_at ? '已使用' : '已领取', disabled: true }
  if (Number(coupon.claimed || 0) >= Number(coupon.quantity || 0)) return { label: '已领完', disabled: true }
  return { label: '立即领取', disabled: false }
}
async function claim(coupon) {
  if (!isCustomer.value) { openMiniLogin(); return }
  if (couponButtonState(coupon).disabled) return
  claimingId.value = coupon.id
  try {
    await claimCoupon(coupon.id)
    const response = await customerCoupons()
    couponClaims.value = response.data?.list || []
    coupon.claimed = Number(coupon.claimed || 0) + 1
    ElMessage.success('优惠券已放入账户')
  } catch (error) { ElMessage.error(error?.message || '领取失败') }
  finally { claimingId.value = null }
}
async function openTopic(topic) {
  selectedTopic.value = topic
  topicProducts.value = []
  topicVisible.value = true
  topicLoading.value = true
  try { topicProducts.value = (await mallTopicProducts(topic.id)).data?.list || [] }
  catch (error) { ElMessage.error(error?.message || '专题商品加载失败') }
  finally { topicLoading.value = false }
}
function openGroup(rule) {
  openMiniPage('offers')
}
function goCart() {
  if (!isCustomer.value) { openMiniLogin(); return }
  router.push('/mini-store/cart')
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
function goProfile() {
  activeTab.value = 'profile'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
function showAddresses() {
  if (!isCustomer.value) { openMiniLogin(); return }
  router.push('/mini-store/addresses')
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
function showCoupons() { openMiniPage('offers') }
function validateMiniConfirmPassword(_rule, value, callback) {
  if (!value) callback(new Error('请确认密码'))
  else if (value !== miniAuthForm.password) callback(new Error('两次密码输入不一致'))
  else callback()
}
function resetMiniAuthForm() {
  miniAuthForm.username = ''
  miniAuthForm.password = ''
  miniAuthForm.confirmPassword = ''
  miniAuthFormRef.value?.clearValidate()
}
function openMiniLogin() {
  miniAuthMode.value = 'login'
  resetMiniAuthForm()
  activeTab.value = 'login'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
function toggleMiniAuthMode() {
  miniAuthMode.value = miniAuthMode.value === 'login' ? 'register' : 'login'
  resetMiniAuthForm()
}
function switchBuyerAccount() {
  clearAuth()
  reloadUser()
  cartCount.value = 0
  couponClaims.value = []
  openMiniLogin()
}
function signOutBuyerAccount() {
  switchBuyerAccount()
  ElMessage.success('已退出买家账号')
}
async function loadBuyerState() {
  const [couponResult, cartResult] = await Promise.allSettled([customerCoupons(), getCart()])
  couponClaims.value = couponResult.status === 'fulfilled' ? couponResult.value.data?.list || [] : []
  cartCount.value = cartResult.status === 'fulfilled'
    ? (cartResult.value.data?.list || []).reduce((sum, item) => sum + Number(item.quantity || 0), 0)
    : 0
}
async function submitMiniAuth() {
  const valid = await miniAuthFormRef.value?.validate().catch(() => false)
  if (!valid || miniAuthBusy.value) return
  miniAuthBusy.value = true
  try {
    if (miniAuthMode.value === 'register') {
      const response = await registerApi({ ...miniAuthForm }, { silentError: true })
      if (response.code !== 200) throw new Error(response.message || '注册失败')
      ElMessage.success('注册成功，请登录')
      miniAuthMode.value = 'login'
      miniAuthForm.password = ''
      miniAuthForm.confirmPassword = ''
      return
    }
    const response = await loginApi({ username: miniAuthForm.username, password: miniAuthForm.password, login_type: 'user' }, { silentError: true })
    if (response.code !== 200) throw new Error(response.message || '登录失败')
    if (response.data?.user?.role !== 'customer') throw new Error('该账号不是买家账号，请使用买家账号登录')
    saveLoginData(response.data)
    await loadBuyerState()
    const next = String(route.query.next || '')
    await router.replace(next.startsWith('/mini-store/') && !next.startsWith('//') ? next : {path:'/mini-store',query:{tab:'profile'}})
    window.scrollTo({ top: 0, behavior: 'smooth' })
    ElMessage.success('登录成功')
  } catch (error) {
    ElMessage.error(error?.message || (miniAuthMode.value === 'register' ? '注册失败' : '登录失败'))
  } finally {
    miniAuthBusy.value = false
  }
}
function openUserBrowserPage() {
  if (!userInfo.value) { openMiniLogin(); return }
  const href = router.resolve('/manager/store').href
  const browserPage = window.open(href, '_blank')
  if (!browserPage) ElMessage.warning('浏览器拦截了新页面，请允许此站点打开弹出窗口')
  else browserPage.opener = null
}

onMounted(async () => {
  fitMiniViewport()
  window.visualViewport?.addEventListener('resize',fitMiniViewport)
  window.addEventListener('resize',fitMiniViewport)
  refreshMessages()
  buyerTimer = setInterval(() => { if (!document.hidden) refreshMessages() }, 8000)
  window.addEventListener('customer-messages-updated', refreshMessages)
  window.addEventListener('customer-messages-read', refreshMessages)
  window.addEventListener('customer-cart-updated', refreshBuyerState)
  window.addEventListener('focus', refreshBuyerState)
  const requests = [mallPortal(), loadProducts()]
  if (isCustomer.value) requests.push(loadBuyerState())
  const [portalResult] = await Promise.allSettled(requests)
  if (portalResult.status === 'fulfilled') {
    portal.value = portalResult.value.data || {}
    shopName.value = portal.value.shop?.name || '商城精选'
  }
})
onUnmounted(() => {
  window.visualViewport?.removeEventListener('resize',fitMiniViewport)
  window.removeEventListener('resize',fitMiniViewport)
  clearInterval(buyerTimer)
  window.removeEventListener('customer-messages-updated', refreshMessages)
  window.removeEventListener('customer-messages-read', refreshMessages)
  window.removeEventListener('customer-cart-updated', refreshBuyerState)
  window.removeEventListener('focus', refreshBuyerState)
})
</script>

<style scoped>

.mini-page-nav { display:flex; align-items:center; justify-content:space-between; padding:14px 16px; border-bottom:1px solid #edf0f2; }
.mini-page-nav button { border:0; color:#348bea; background:none; cursor:pointer; }
.mini-unread { display:inline-block; padding:1px 6px; border-radius:12px; background:#f05b51; color:white; font-size:11px; }
.mini-product__rating { color:#bb7840; font-size:11px; }
.mini-shared-page { padding-bottom:12px; min-width:0; }
.mini-shared-page :deep(.page-container) { width:100%; max-width:none; margin:0; padding:14px; min-width:0; }
.mini-shared-page :deep(.content-card) { min-width:0; }
@media(max-width:640px) {
  .mini-store { padding-left:0; padding-right:0; }
  .mini-shared-page :deep(.page-container) { padding:10px; }
  .mini-shared-page :deep(.content-card) { padding:14px; }
  .mini-shared-page :deep(.customer-message-center__body) { grid-template-columns:minmax(0,1fr); }
  .mini-shared-page :deep(.customer-message-list__items) { max-height:230px; }
  .mini-shared-page :deep(.support-panel) { grid-template-columns:minmax(0,1fr); }
  .mini-shared-page :deep(.support-panel__history) { max-height:180px; overflow:auto; }
  .mini-shared-page :deep(.order-card__body) { flex-direction:column; align-items:stretch; }
  .mini-shared-page :deep(.order-card__amount) { flex-wrap:wrap; }
  .mini-shared-page :deep(.coupon-grid), .mini-shared-page :deep(.group-grid) { grid-template-columns:minmax(0,1fr); }
}

.mini-store { min-height:100dvh; background:#f3f4f2; color:#243447; padding:0 16px 82px; }
.mini-store__shell { width:min(100%, 860px); min-height:100dvh; margin:0 auto; background:#fff; box-shadow:0 0 28px #1b30400a; }
.mini-header { position:sticky; z-index:5; top:0; display:grid; gap:10px; padding:12px 16px; background:#fff; border-bottom:1px solid #f1f2f2; }
.mini-header__brand { display:flex; align-items:center; justify-content:space-between; min-height:24px; color:#172b3c; }
.mini-header__brand strong { font-size:16px; }
.mini-header__actions { display:flex; align-items:center; gap:12px; }
.mini-header__browser, .mini-header__back { padding:4px 0; border:0; background:transparent; color:#7a8a97; font-size:12px; cursor:pointer; }
.mini-header__browser { color:#b75d48; }
.mini-header__back { border:0; background:transparent; color:#7a8a97; font-size:12px; cursor:pointer; }
.mini-search { display:flex; align-items:center; gap:9px; height:40px; padding:0 13px; border-radius:8px; background:#f5f6f7; color:#9ba6ae; }
.mini-search input { flex:1; width:0; border:0; outline:0; background:transparent; color:#263b4d; font:inherit; }
.mini-search input::placeholder { color:#aab3ba; }
.mini-search button { border:0; background:transparent; color:#81909a; font-size:20px; cursor:pointer; }
.mini-content { min-height:calc(100dvh - 142px); padding:0 0 28px; }
.mini-home { display:grid; gap:14px; }
.mini-hero { padding:0 0 2px; background:#f4f2ed; }
.mini-hero :deep(.el-carousel__container) { height:clamp(180px, 31vw, 270px) !important; }
.mini-hero :deep(.el-carousel__arrow) { width:34px; height:34px; background:#2434478c; }
.mini-hero__slide, .mini-hero__fallback { position:relative; display:block; width:100%; height:100%; overflow:hidden; border:0; background:#e6eadf; text-align:left; cursor:pointer; }
.mini-hero__slide img { width:100%; height:100%; object-fit:cover; }
.mini-hero__shade { position:absolute; inset:0; background:linear-gradient(90deg,#182b2d99,transparent 75%); }
.mini-hero__caption { position:absolute; left:clamp(20px,5vw,46px); top:50%; display:grid; gap:8px; transform:translateY(-50%); color:white; text-shadow:0 1px 8px #0005; }
.mini-hero__caption small, .mini-hero__fallback-copy small, .mini-section__heading small { font-size:10px; letter-spacing:.14em; opacity:.76; }
.mini-hero__caption strong { max-width:420px; font-size:clamp(20px,4vw,34px); }
.mini-hero__caption > span { font-size:13px; }
.mini-hero__caption b { margin-left:5px; font-size:20px; }
.mini-hero__fallback { min-height:clamp(180px,31vw,270px); padding:30px clamp(24px,6vw,56px); color:#714837; background:radial-gradient(circle at 82% 24%,#f6e7cb 0 12%,transparent 12.5%),radial-gradient(circle at 72% 95%,#d7b38e 0 14%,transparent 14.5%),linear-gradient(120deg,#f5eadb,#e9d7bd 52%,#f7f1e8); }
.mini-hero__fallback-copy { display:grid; gap:10px; }
.mini-hero__fallback-copy small { color:#98785f; }
.mini-hero__fallback-copy strong { font-size:clamp(26px,5vw,42px); line-height:1.25; }
.mini-hero__fallback-copy > span { width:max-content; padding:7px 13px; border-radius:4px; color:#fff; background:#b85d47; font-size:13px; }
.mini-hero__shape { position:absolute; right:9%; top:50%; display:grid; width:clamp(74px,13vw,126px); aspect-ratio:1; place-items:center; border:1px solid #fff8; border-radius:50%; color:#fff9; background:#b7886240; font-size:clamp(22px,4vw,38px); transform:translateY(-50%) rotate(-9deg); }
.mini-categories { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:10px 4px; padding:12px 10px 15px; border-bottom:10px solid #f3f4f2; }
.mini-categories button { display:grid; justify-items:center; gap:5px; min-width:0; padding:4px 2px; border:0; background:white; color:#35475a; font-size:12px; cursor:pointer; }
.mini-categories__icon { display:grid; width:38px; height:38px; place-items:center; border-radius:50%; color:#9b7560; background:#f6f2ed; font-size:22px; }
.mini-section { padding:16px 18px 4px; }
.mini-section__heading { display:flex; align-items:end; justify-content:space-between; gap:14px; margin-bottom:12px; }
.mini-section__heading > div { display:grid; gap:4px; }
.mini-section__heading small { color:#91a0a9; }
.mini-section__heading h2 { margin:0; color:#1d3243; font-size:19px; }
.mini-section__heading > span, .mini-section__heading > button { border:0; background:none; color:#98a2a8; font-size:12px; }
.mini-section__heading > button { color:#b75d48; cursor:pointer; }
.mini-coupons { display:grid; gap:8px; }
.mini-coupon { display:grid; grid-template-columns:minmax(112px, 150px) minmax(0,1fr) auto; align-items:center; gap:14px; min-height:84px; padding:10px 14px; border:1px solid #efb9ae; border-radius:6px; background:#fffdfc; }
.mini-coupon__amount { display:grid; grid-template-columns:auto auto; justify-content:start; align-items:baseline; column-gap:3px; color:#eb514e; font-size:24px; }
.mini-coupon__amount small { font-size:12px; }
.mini-coupon__amount span { grid-column:1 / -1; color:#9aa3a8; font-size:11px; }
.mini-coupon__details { display:grid; gap:7px; min-width:0; }
.mini-coupon__details strong { overflow:hidden; color:#293a49; font-size:14px; text-overflow:ellipsis; white-space:nowrap; }
.mini-coupon__details span { color:#a0a8ad; font-size:11px; }
.mini-coupon > button { padding:7px 10px; border:1px solid #eb7770; border-radius:4px; color:#e95853; background:white; font-size:12px; cursor:pointer; }
.mini-coupon > button:disabled { border-color:#e5e8e8; color:#99a1a5; background:#f5f6f6; cursor:default; }
.mini-groups { display:grid; gap:8px; background:linear-gradient(135deg,#fff9f0,#fff); }
.mini-group { display:flex; align-items:center; gap:10px; padding:11px 12px; border:1px solid #f2e2cc; border-radius:8px; background:#fff; text-align:left; cursor:pointer; }
.mini-group__badge { flex:0 0 auto; padding:4px 7px; border-radius:4px; color:#bf6738; background:#fff0dd; font-size:11px; }
.mini-group__name { flex:1; overflow:hidden; color:#394a58; font-size:13px; text-overflow:ellipsis; white-space:nowrap; }
.mini-group strong { color:#e35b3f; font-size:15px; white-space:nowrap; }
.mini-group strong small { color:#9b9c98; font-size:10px; font-weight:400; }
.mini-group__arrow { color:#b2b8b9; font-size:22px; }
.mini-topics { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }
.mini-topics button { display:grid; gap:6px; min-width:0; padding:0 0 10px; overflow:hidden; border:1px solid #edf0ee; border-radius:7px; background:#fff; text-align:left; cursor:pointer; }
.mini-topics img, .mini-topics__placeholder { width:100%; height:110px; object-fit:cover; }
.mini-topics__placeholder { display:grid; place-items:center; color:#9a7c68; background:linear-gradient(135deg,#f1e9dc,#d6e4db); }
.mini-topics strong, .mini-topics small { margin:0 10px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.mini-topics strong { color:#344655; font-size:13px; }
.mini-topics small { color:#9aa3a7; font-size:11px; }
.mini-product-section { border-top:10px solid #f3f4f2; }
.mini-products { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }
.mini-product { display:grid; align-content:start; gap:7px; min-width:0; padding:0 0 12px; overflow:hidden; border:1px solid #edf0ed; border-radius:8px; background:#fff; color:#344452; text-align:left; cursor:pointer; }
.mini-product__image { position:relative; display:grid; width:100%; aspect-ratio:1.2; place-items:center; overflow:hidden; color:#a29484; background:#f4f5f2; }
.mini-product__image img { width:100%; height:100%; object-fit:cover; }
.mini-product__image > span { font-size:26px; }
.mini-product__image small { position:absolute; left:8px; bottom:8px; padding:3px 6px; border-radius:3px; color:white; background:#222b3588; font-size:10px; }
.mini-product > strong, .mini-product__description, .mini-product__price { margin:0 10px; }
.mini-product > strong { overflow:hidden; font-size:13px; text-overflow:ellipsis; white-space:nowrap; }
.mini-product__description { overflow:hidden; color:#9aa3aa; font-size:11px; text-overflow:ellipsis; white-space:nowrap; }
.mini-product__price { display:flex; align-items:baseline; justify-content:space-between; gap:8px; }
.mini-product__price b { color:#e75740; font-size:17px; }
.mini-product__price small { color:#a2a9ad; font-size:10px; }
.mini-load-more { display:block; margin:16px auto 8px; padding:9px 22px; border:1px solid #e6e9e7; border-radius:20px; color:#6c7a82; background:#fff; cursor:pointer; }
.mini-category-page { padding:18px; }
.mini-cart-page { padding:16px 18px 8px; }
.mini-profile-page { display:grid; gap:12px; padding:18px; }
.mini-profile-card, .mini-profile-actions, .mini-login-card { border:1px solid #edf0ed; border-radius:10px; background:#fff; }
.mini-profile-card { display:flex; align-items:center; gap:14px; padding:18px; }
.mini-profile-avatar, .mini-login-card__avatar { display:grid; flex:0 0 54px; width:54px; height:54px; place-items:center; border-radius:50%; color:#fff; background:#21364a; font-size:22px; }
.mini-profile-card > div:last-child { display:grid; gap:4px; }
.mini-profile-card small, .mini-profile-card span { color:#92a0a7; font-size:12px; }
.mini-profile-card strong { color:#21364a; font-size:16px; }
.mini-profile-actions { display:grid; }
.mini-profile-actions button { display:flex; align-items:center; justify-content:space-between; min-height:52px; padding:0 16px; border:0; border-bottom:1px solid #f0f2f0; background:#fff; color:#35495a; text-align:left; cursor:pointer; }
.mini-profile-actions button:last-child { border-bottom:0; }
.mini-profile-actions button span { color:#a4afb3; font-size:20px; }
.mini-login-card { display:grid; justify-items:center; gap:10px; padding:36px 22px; text-align:center; }
.mini-login-card__avatar { color:#bd684f; background:#f8f0e9; font-size:26px; }
.mini-login-card h2 { margin:6px 0 0; color:#24384a; font-size:20px; }
.mini-login-card p { max-width:380px; margin:0 0 8px; color:#85939b; font-size:13px; line-height:1.7; }
.mini-auth-page { display:grid; gap:12px; padding:18px; }
.mini-auth-form { width:min(100%, 360px); margin-top:8px; }
.mini-auth-form :deep(.el-form-item) { margin-bottom:14px; }
.mini-auth-form :deep(.el-button) { width:100%; }
.mini-auth-toggle { border:0; background:transparent; color:#b75d48; font-size:13px; cursor:pointer; }
.mini-addresses-page { display:grid; gap:12px; padding:16px 18px; }
.mini-addresses-back { justify-self:start; padding:6px 0; border:0; background:transparent; color:#72818a; cursor:pointer; }
.mini-addresses-page :deep(.customer-page) { gap:12px; }
.mini-addresses-page :deep(.customer-page__heading h1) { font-size:18px; }
.mini-category-page__list { display:flex; gap:8px; margin-bottom:16px; overflow:auto; padding-bottom:6px; }
.mini-category-page__list button { flex:0 0 auto; padding:8px 12px; border:1px solid #e9ece9; border-radius:20px; color:#697780; background:#fff; cursor:pointer; }
.mini-category-page__list button.active { border-color:#d66d51; color:#bd5c42; background:#fff6f0; }
.mini-tabbar { position:fixed; z-index:10; right:0; bottom:0; left:0; display:grid; grid-template-columns:repeat(4,1fr); width:min(100%, 860px); height:calc(66px + env(safe-area-inset-bottom)); margin:0 auto; padding-bottom:env(safe-area-inset-bottom); border-top:1px solid #edf0ef; background:#fffffffa; box-shadow:0 -4px 18px #2033290b; }
.mini-tabbar button { position:relative; display:grid; grid-template-rows:24px 16px; align-content:center; justify-items:center; min-width:0; padding:0; border:0; color:#79858b; background:transparent; text-align:center; cursor:pointer; }
.mini-tabbar__icon { display:block; width:24px; height:24px; }
.mini-tabbar button span { display:block; min-width:0; font-size:11px; line-height:16px; }
.mini-tabbar button.active { color:#dc514c; }
.mini-tabbar button i { position:absolute; top:6px; left:calc(50% + 8px); min-width:16px; padding:1px 4px; border-radius:10px; color:white; background:#e65c54; font-size:9px; font-style:normal; }
.mini-detail-loading { display:flex; align-items:center; justify-content:center; gap:10px; min-height:220px; color:#78858c; }
.mini-loading-spinner { width:20px; height:20px; border:2px solid #e6ece9; border-top-color:#dc514c; border-radius:50%; animation:mini-spin .8s linear infinite; }
@keyframes mini-spin { to { transform:rotate(360deg); } }
.mini-product-detail { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:20px; }
.mini-product-detail__image { position:relative; display:grid; min-height:300px; align-content:center; place-items:center; overflow:hidden; border-radius:10px; background:#f3f5f2; color:#8b9698; }
.mini-product-detail__image > img { width:100%; max-height:420px; aspect-ratio:1; object-fit:contain; }
.mini-product-detail__image > span { display:grid; min-height:300px; place-items:center; }
.mini-product-detail__image > small { position:absolute; top:10px; right:10px; padding:4px 7px; border-radius:12px; color:#fff; background:#263a4b99; font-size:11px; }
.mini-product-detail__thumbs { position:absolute; right:8px; bottom:8px; left:8px; display:flex; gap:6px; overflow:auto; }
.mini-product-detail__thumbs button { width:46px; height:46px; flex:0 0 46px; padding:2px; border:1px solid transparent; border-radius:5px; background:#fff; cursor:pointer; }
.mini-product-detail__thumbs button.active { border-color:#dc514c; }
.mini-product-detail__thumbs img { width:100%; height:100%; object-fit:cover; }
.mini-product-detail__copy { display:flex; flex-direction:column; align-items:flex-start; gap:13px; padding:8px 2px; }
.mini-product-detail__copy h2 { margin:0; color:#243747; font-size:20px; line-height:1.45; }
.mini-product-detail__copy p { color:#89969c; font-size:13px; line-height:1.65; white-space:pre-wrap; }
.mini-product-detail__price { color:#e4543f; font-size:26px; }
.mini-product-detail__price small { font-size:13px; font-weight:400; }
.mini-product-detail__meta { display:flex; flex-wrap:wrap; gap:8px; color:#849198; font-size:12px; }
.mini-product-detail__meta span { padding:5px 8px; border-radius:4px; background:#f4f6f4; }
.mini-product-detail__variant { width:100%; padding:12px 0; border:0; border-top:1px solid #edf0ee; border-bottom:1px solid #edf0ee; background:#fff; color:#61717b; text-align:left; cursor:pointer; }
.mini-product-detail__actions { display:flex; width:100%; gap:9px; margin-top:auto; padding-top:18px; }
.mini-product-detail__actions button { flex:1; min-height:42px; border:0; border-radius:7px; color:white; font-size:14px; cursor:pointer; }
.mini-product-detail__cart { background:#eba72f; }
.mini-product-detail__buy { background:#e95843; }
.mini-product-detail__buyer-hint { color:#97a0a3; font-size:12px; }
.mini-checkout-form { display:grid; grid-template-columns:1fr; gap:0; }
.mini-checkout-form :deep(.el-form-item) { margin-bottom:10px; }
.mini-checkout-total { display:flex; align-items:center; justify-content:space-between; gap:8px; padding:10px 0; border-top:1px solid #edf0ee; color:#78858b; font-size:12px; }
.mini-checkout-total strong { color:#e4543f; font-size:16px; white-space:nowrap; }
.mini-checkout-note { color:#929da1; font-size:11px; line-height:1.5; }
.mini-detail-dialog :deep(.el-dialog) { border-radius:14px; }
.mini-detail-dialog :deep(.el-dialog__body) { padding:16px 20px 22px; }
.mini-dialog-copy { color:#667782; line-height:1.7; white-space:pre-wrap; }
.mini-topic-products { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }
.mini-topic-products button { display:grid; gap:7px; padding:8px; border:1px solid #edf0ed; border-radius:7px; background:white; text-align:left; cursor:pointer; }
.mini-topic-products img { width:100%; aspect-ratio:1; object-fit:cover; }
.mini-topic-products strong { overflow:hidden; font-size:12px; text-overflow:ellipsis; white-space:nowrap; }
.mini-topic-products span { color:#e75740; font-size:13px; }
@media (max-width:560px) {
  .mini-store { padding:0 0 72px; }
  .mini-header { padding:10px 14px; }
  .mini-section { padding-right:13px; padding-left:13px; }
  .mini-coupon { grid-template-columns:100px minmax(0,1fr) auto; gap:8px; padding:9px; }
  .mini-coupon__amount { font-size:21px; }
  .mini-coupon > button { padding:6px 7px; font-size:11px; }
  .mini-products { gap:8px; }
  .mini-product > strong, .mini-product__description, .mini-product__price { margin-right:8px; margin-left:8px; }
  .mini-product__price b { font-size:15px; }
  .mini-hero :deep(.el-carousel__container) { height:clamp(175px,56vw,250px) !important; }
  .mini-topic-products { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .mini-product-detail { grid-template-columns:1fr; gap:12px; }
  .mini-product-detail__image { min-height:220px; max-height:42vh; }
  .mini-product-detail__image > img { max-height:42vh; }
  .mini-product-detail__image > span { min-height:220px; }
  .mini-product-detail__copy { gap:9px; }
  .mini-product-detail__copy h2 { font-size:17px; }
  .mini-product-detail__price { font-size:22px; }
  .mini-detail-dialog :deep(.el-dialog) { max-height:88vh; margin:6vh auto 0 !important; overflow:auto; }
  .mini-detail-dialog :deep(.el-dialog__body) { padding:12px 14px 16px; }
  .mini-checkout-total { align-items:flex-start; flex-direction:column; }
}

.mini-store { position:fixed; inset:0; height:var(--mini-vh,100dvh); min-height:0; padding:0; overflow:hidden; background:#edf0f2; }
.mini-store__shell { display:flex; flex-direction:column; width:min(100%,480px); height:100%; min-height:0; overflow:hidden; background:#f5f6f8; }
.mini-header { position:relative; flex:none; min-height:52px; padding:10px 14px; gap:8px; z-index:4; }
.mini-header__brand strong { font-size:15px; }
.mini-header__actions { gap:12px; }
.mini-search { height:38px; }
.mini-search input { font-size:16px; }
.mini-content { flex:1; min-height:0; overflow-y:auto; overscroll-behavior:contain; -webkit-overflow-scrolling:touch; padding:0 0 14px; }
.mini-content--detail { overflow:hidden; padding:0; display:flex; }
.mini-shared-page { width:100%; height:100%; padding:0; min-height:0; overflow:hidden; }
.mini-tabbar { position:relative; inset:auto; transform:none; display:flex; flex:none; align-items:center; width:100%; height:calc(58px + env(safe-area-inset-bottom)); min-height:58px; margin:0; padding:5px 0 calc(5px + env(safe-area-inset-bottom)); z-index:5; border-top:1px solid #eef1f3; }
.mini-tabbar>button { min-height:46px; flex:1; font-size:10px; }
.mini-tabbar__icon { width:21px; height:21px; }
.mini-products { grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }
.mini-home { gap:8px; }.mini-section { padding:14px 12px 3px; }.mini-section__heading h2 {font-size:17px;}.mini-section__heading small{display:none}.mini-product-section{padding-bottom:12px}.mini-product__rating{display:block;margin:5px 8px 0}
.mini-profile-page { padding:0 12px 16px; display:block; }
.mini-me-banner { display:flex; align-items:center; gap:14px; margin:0 -12px 12px; padding:28px 22px; background:linear-gradient(120deg,#fff1e5,#fff9f0); }
.mini-me-avatar { display:grid;place-items:center;flex:none;width:62px;height:62px;border-radius:50%;background:#f3ccb2;color:#fff;font-size:25px;overflow:hidden; }
.mini-me-avatar img{width:100%;height:100%;object-fit:cover}.mini-me-banner>div:nth-child(2){flex:1}.mini-me-banner strong{font-size:19px;font-weight:600}.mini-me-banner p{font-size:11px;color:#b19d8f;margin:6px 0 0}.mini-me-banner>button{border:0;background:none;color:#bd977e;font-size:11px;padding:10px}
.mini-me-card{padding:16px;margin-bottom:12px;border-radius:14px;background:#fff}.mini-me-card>header{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}.mini-me-card>header strong{font-size:14px}.mini-me-card>header button{border:0;background:none;color:#a9b1b9;font-size:11px}
.mini-order-shortcuts{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}.mini-order-shortcuts>button{display:grid;justify-items:center;gap:9px;padding:3px 0;border:0;background:none;font-size:11px;color:#7a8995}.mini-order-shortcuts span{color:#de9a77;font-size:25px;line-height:1}
.mini-me-services{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));row-gap:22px;padding:20px 10px}.mini-me-services>button{display:grid;justify-items:center;gap:8px;min-height:58px;border:0;background:none;color:#7e8e99;font-size:11px}.mini-me-services>button>span{position:relative;color:#b6a9bc;font-size:26px;line-height:1}.mini-me-services i{position:absolute;top:-5px;left:18px;border-radius:12px;padding:2px 5px;background:#ed6957;color:#fff;font-size:10px;font-style:normal}
.mini-me-settings{padding:0 16px}.mini-me-settings>button{display:flex;align-items:center;justify-content:space-between;width:100%;min-height:48px;border:0;border-bottom:1px solid #f2f4f6;background:none;color:#748792;font-size:13px}.mini-me-settings>button:last-child{border-bottom:0}.mini-me-settings span{color:#bfc7ce;font-size:20px}.mini-me-signout{display:flex;justify-content:center;gap:20px;padding:6px 0}.mini-me-signout>button{min-height:40px;border:0;background:none;color:#a6afb8;font-size:12px}

</style>
