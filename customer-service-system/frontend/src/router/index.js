import { getToken, getUserInfo } from '@/utils/auth'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/manager/home' },
    { path:'/mini-store',name:'MiniStore',component:()=>import('@/views/MiniStore.vue'),children:[
      {path:'products/:id',component:()=>import('@/views/mini/MiniProduct.vue'),meta:{title:'商品详情'}},
      {path:'cart',component:()=>import('@/views/mini/MiniCart.vue'),meta:{title:'购物车'}},
      {path:'orders',component:()=>import('@/views/mini/MiniOrders.vue'),meta:{title:'订单记录'}},
      {path:'favorites',component:()=>import('@/views/mini/MiniFavorites.vue'),meta:{title:'我的收藏'}},
      {path:'messages',component:()=>import('@/views/mini/MiniMessages.vue'),meta:{title:'我的消息'}},
      {path:'addresses',component:()=>import('@/views/mini/MiniAddresses.vue'),meta:{title:'收货地址'}},
      {path:'profile',component:()=>import('@/views/mini/MiniProfile.vue'),meta:{title:'个人资料'}},
      {path:'password',component:()=>import('@/views/mini/MiniPassword.vue'),meta:{title:'修改密码'}},
      {path:'offers',component:()=>import('@/views/mini/MiniServices.vue'),meta:{title:'优惠与团购',mallMode:'offers'}},
      {path:'help',component:()=>import('@/views/mini/MiniServices.vue'),meta:{title:'公告与帮助',mallMode:'help'}},
      {path:'feedback',component:()=>import('@/views/mini/MiniServices.vue'),meta:{title:'意见反馈',mallMode:'feedback'}}
    ] },
    {
      path: '/manager',
      name: 'Layout',
      component: () => import('@/layouts/Layout.vue'),
      children: [
        { path: 'mall/:resource', name: 'CommerceAdmin', component: () => import('@/views/CommerceAdmin.vue') },
        { path: 'offers', name: 'CustomerOffers', component: () => import('@/views/CustomerMall.vue'), meta: { mallMode: 'offers' } },
        { path: 'help', name: 'CustomerHelp', component: () => import('@/views/CustomerMall.vue'), meta: { mallMode: 'help' } },
        { path: 'feedback', name: 'CustomerFeedback', component: () => import('@/views/CustomerMall.vue'), meta: { mallMode: 'feedback' } },
        { path: 'home', name: 'Home', component: () => import('@/views/Home.vue') },
        { path: 'platform-logs', name: 'PlatformLogs', component: () => import('@/views/PlatformLogs.vue') },
        { path: 'store', name: 'Storefront', component: () => import('@/views/Storefront.vue') },
        { path: 'cart', name: 'CustomerCart', component: () => import('@/views/CustomerCart.vue') },
        { path: 'favorites', name: 'CustomerFavorites', component: () => import('@/views/CustomerFavorites.vue') },
        { path: 'messages', name: 'CustomerMessages', component: () => import('@/views/CustomerMessages.vue') },
        { path: 'my-orders', name: 'CustomerOrders', component: () => import('@/views/CustomerOrders.vue') },
        { path: 'addresses', name: 'CustomerAddresses', component: () => import('@/views/CustomerAddresses.vue') },
        {
          path: 'store/products/:id',
          name: 'StorefrontProductDetail',
          component: () => import('@/views/ProductDetail.vue'),
          props: true
        },
        { path: 'chat', name: 'Chat', component: () => import('@/views/Chat.vue') },
        { path: 'history', name: 'History', component: () => import('@/views/History.vue') },
        { path: 'metrics', name: 'Metrics', component: () => import('@/views/Metrics.vue') },
        { path: 'products', name: 'Products', component: () => import('@/views/ProductList.vue') },
        { path: 'product-listing/:id?', name: 'ProductListing', component: () => import('@/views/ProductListingPage.vue'), meta: { productEditorOnly: true } },
        {
          path: 'products/:id',
          name: 'ProductDetail',
          component: () => import('@/views/ProductDetail.vue'),
          props: true
        },
        { path: 'orders', name: 'Orders', component: () => import('@/views/OrderList.vue') },
        { path: 'after-sales', name: 'AfterSales', component: () => import('@/views/AfterSaleTickets.vue') },
        { path: 'message-center', name: 'StaffMessageCenter', component: () => import('@/views/StaffMessageCenter.vue') },
        { path: 'reviews', name: 'Reviews', component: () => import('@/views/ReviewList.vue') },
        { path: 'reports', name: 'Reports', component: () => import('@/views/ReportList.vue') },
        {
          path: 'semantic',
          name: 'Semantic',
          component: () => import('@/views/SemanticSearch.vue')
        },
        { path: 'profile', name: 'Profile', component: () => import('@/views/Profile.vue') },
        { path: 'password', name: 'Password', component: () => import('@/views/Password.vue') },
        { path: 'user', name: 'User', component: () => import('@/views/User.vue') }
      ]
    },
    { path: '/login', name: 'Login', component: () => import('@/views/Login.vue') },
    { path: '/register', name: 'Register', component: () => import('@/views/Register.vue') },
    {
      path: '/switch-user',
      name: 'SwitchAccount',
      component: () => import('@/views/SwitchAccount.vue')
    }
  ]
})

// 路由守卫：验证token
router.beforeEach((to) => {
  if (to.path === '/mini-store' || to.path.startsWith('/mini-store/')) {
    const publicPage = to.path === '/mini-store' || to.path === '/mini-store/help' || (to.path.startsWith('/mini-store/products/') && getToken())
    if (!publicPage && (!getToken() || getUserInfo()?.role !== 'customer')) return {path:'/mini-store',query:{tab:'login',next:to.fullPath}}
    return true
  }
  const token = getToken()
  const user = getUserInfo()

  if (to.path === '/login' || to.path === '/register' || to.path === '/switch-user') {
    return true
  } else {
    if (!token) {
      const userPaths = [
        '/manager/store',
        '/mini-store',
        '/manager/profile',
        '/manager/password',
        '/manager/cart',
        '/manager/favorites',
        '/manager/messages',
        '/manager/my-orders',
        '/manager/addresses',
        '/manager/offers',
        '/manager/help',
        '/manager/feedback'
      ]
      const isUserPath = userPaths.includes(to.path) || to.path.startsWith('/manager/store/products/')
      return { path: '/login', query: isUserPath ? { mode: 'user', redirect: to.fullPath } : {} }
    }
    if (to.meta.productEditorOnly && !['admin', 'user'].includes(user?.role)) {
      return user?.role === 'customer' ? '/manager/store' : '/manager/home'
    }
    if (user?.role === 'customer') {
      const allowedPaths = [
        '/manager/store',
        '/mini-store',
        '/manager/profile',
        '/manager/password',
        '/manager/cart',
        '/manager/favorites',
        '/manager/messages',
        '/manager/my-orders',
        '/manager/addresses',
        '/manager/offers',
        '/manager/help',
        '/manager/feedback'
      ]
      const allowed = allowedPaths.includes(to.path) || to.path.startsWith('/manager/store/products/')
      if (!allowed) return '/manager/store'
    }
    if (['/manager/offers', '/manager/feedback'].includes(to.path) && user?.role !== 'customer') return '/manager/store'
    if (to.path.startsWith('/manager/user') && user?.role !== 'admin') {
      return user?.role === 'customer' ? '/manager/store' : '/manager/home'
    }
    return true
  }
})

export default router
