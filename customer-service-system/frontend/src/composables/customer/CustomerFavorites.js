import { useCustomerRouter } from '@/utils/customerRouter'
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete, Picture, ShoppingCart } from '@element-plus/icons-vue'
import { addCartItem, deleteFavorite, getFavorites } from '@/api/customer'

export function useCustomerFavorites() {
const router = useCustomerRouter()
const items = ref([])
const loading = ref(false)
const busyId = ref(null)
function isAvailable(product) {
  return product.shelf_status === 'on_sale' && product.review_status === 'normal' && product.stock > 0
}
async function load() {
  loading.value = true
  try {
    const response = await getFavorites()
    items.value = response.data?.list || []
  } catch (error) {
    ElMessage.error(error?.message || '加载收藏失败')
  } finally {
    loading.value = false
  }
}
function openProduct(productId) {
  router.push(`/manager/store/products/${productId}`)
}
async function addToCart(product) {
  busyId.value = product.id
  try {
    if (product.variants?.length) {
      await router.push(`/manager/store/products/${product.id}`)
      return
    }
    await addCartItem(product.id)
    ElMessage.success('已加入购物车')
  } catch (error) {
    ElMessage.error(error?.message || '加入购物车失败')
  } finally {
    busyId.value = null
  }
}
async function removeFavorite(product) {
  busyId.value = product.id
  try {
    await deleteFavorite(product.id)
    items.value = items.value.filter((item) => item.product.id !== product.id)
    ElMessage.success('已取消收藏')
  } catch (error) {
    ElMessage.error(error?.message || '取消收藏失败')
  } finally {
    busyId.value = null
  }
}
onMounted(load)
return {
useCustomerRouter,
onMounted,
ref,
ElMessage,
Delete,
Picture,
ShoppingCart,
addCartItem,
deleteFavorite,
getFavorites,
router,
items,
loading,
busyId,
isAvailable,
load,
openProduct,
addToCart,
removeFavorite
};
}
