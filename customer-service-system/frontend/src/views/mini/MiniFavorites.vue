<template>

<div class="m-view"><MiniHeader title="我的收藏" /><div class="m-scroll" v-loading="loading"><article v-for="item in items" :key="item.product.id" class="m-card"><div class="m-item" @click="openProduct(item.product.id)"><img v-if="item.product.image_url" :src="item.product.image_url" class="m-item-image" /><span v-else class="m-item-fallback">好物</span><div><h3>{{ item.product.name }}</h3><p>{{ item.product.category }}</p><strong class="m-price">¥{{ Number(item.product.price).toFixed(2) }}</strong></div></div><div class="m-actions"><button class="m-secondary" :disabled="busyId===item.product.id" @click="removeFavorite(item.product)">取消收藏</button><button class="m-primary" :disabled="!isAvailable(item.product) || busyId===item.product.id" @click="addToCart(item.product)">{{ isAvailable(item.product) ? '加入购物车' : '暂时缺货' }}</button></div></article><div v-if="!items.length && !loading" class="m-empty"><span>♡</span><p>收藏喜欢的商品，下次更好找</p><button class="m-primary" @click="router.push('/manager/store')">去逛逛</button></div></div></div>
</template>
<script setup>
import MiniHeader from '@/components/mini/MiniHeader.vue'
import MiniSheet from '@/components/mini/MiniSheet.vue'
import { useCustomerFavorites } from '@/composables/customer/CustomerFavorites'

const {
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
} = useCustomerFavorites()


</script>
<style scoped>

</style>
