import { useRoute, useRouter } from 'vue-router'

export function useCustomerRouter() {
  const route = useRoute(), router = useRouter()
  function destination(target) {
    if (!route.path.startsWith('/mini-store')) return target
    const resolved = router.resolve(target)
    let path = resolved.path
    const paths = { '/manager/store':'/mini-store', '/manager/cart':'/mini-store/cart',
      '/manager/my-orders':'/mini-store/orders', '/manager/addresses':'/mini-store/addresses',
      '/manager/favorites':'/mini-store/favorites', '/manager/messages':'/mini-store/messages',
      '/manager/profile':'/mini-store/profile', '/manager/password':'/mini-store/password',
      '/manager/offers':'/mini-store/offers', '/manager/feedback':'/mini-store/feedback',
      '/manager/help':'/mini-store/help' }
    if (path === '/login') return {path:'/mini-store',query:{tab:'login',next:route.fullPath}}
    path = paths[path] || path.replace(/^\/manager\/store\/products\//, '/mini-store/products/')
    return {path, query:resolved.query, hash:resolved.hash}
  }
  return { push: target => router.push(destination(target)),
    replace: target => router.replace(destination(target)),
    resolve: target => router.resolve(destination(target)), back: () => router.back() }
}
