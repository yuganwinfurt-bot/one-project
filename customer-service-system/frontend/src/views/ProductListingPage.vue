<template>
  <div class="page-container">
    <section v-if="loading" class="content-card listing-page-loading" v-loading="loading"></section>
    <ProductListingDialog
      v-else
      embedded
      :product="product"
      @saved="returnToList"
      @cancel="returnToList"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ProductListingDialog from '@/components/ProductListingDialog.vue'
import { getProductDetail } from '@/api/ecommerce'

const route = useRoute()
const router = useRouter()
const product = ref(null)
const loading = ref(Boolean(route.params.id))
const returnPath = computed(() => route.query.returnTo === '/manager/store' ? '/manager/store' : '/manager/products')
let requestId = 0

watch(
  () => route.params.id,
  async (id) => {
    const currentRequest = ++requestId
    if (!id) {
      product.value = null
      loading.value = false
      return
    }

    loading.value = true
    try {
      const response = await getProductDetail(id)
      if (currentRequest !== requestId) return
      const record = response.data?.product
      if (!record) {
        router.replace(returnPath.value)
        return
      }
      product.value = record
    } catch {
      if (currentRequest === requestId) router.replace(returnPath.value)
    } finally {
      if (currentRequest === requestId) loading.value = false
    }
  },
  { immediate: true }
)

function returnToList() {
  router.push(returnPath.value)
}
</script>