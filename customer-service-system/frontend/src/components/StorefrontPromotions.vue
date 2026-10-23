<template>
  <section v-if="portal.ads?.length || portal.keywords?.length || portal.topics?.length" class="store-promotions content-card">
    <el-carousel v-if="portal.ads?.length" height="190px" :interval="5000" :autoplay="portal.ads.length > 1" indicator-position="outside">
      <el-carousel-item v-for="ad in portal.ads" :key="ad.id"><button class="ad-banner" @click="openAd(ad)"><el-image :src="ad.image_url" fit="cover" /><span>{{ ad.name }}</span></button></el-carousel-item>
    </el-carousel>
    <div v-if="portal.keywords?.length" class="keyword-list"><span>热门搜索</span><el-button v-for="item in portal.keywords" :key="item.id" round size="small" @click="emit('search', item.redirect_keyword)">{{ item.name }}</el-button></div>
    <div v-if="portal.topics?.length" class="topic-list"><button v-for="topic in portal.topics" :key="topic.id" @click="openTopic(topic)"><el-image v-if="topic.image_url" :src="topic.image_url" fit="cover" /><div><strong>{{ topic.name }}</strong><p>{{ topic.content }}</p></div><span>查看专题 →</span></button></div>
  </section>
  <el-dialog v-model="topicVisible" :title="selectedTopic?.name" width="min(840px,94vw)">
    <p class="topic-text">{{ selectedTopic?.content }}</p>
    <div v-loading="loading" class="topic-products"><button v-for="item in topicProducts" :key="item.id" @click="router.push(`/manager/store/products/${item.id}`)"><el-image v-if="item.image_url" :src="item.image_url" fit="cover" /><strong>{{ item.name }}</strong><span>¥{{ Number(item.price).toFixed(2) }}</span></button></div>
    <el-empty v-if="!loading && !topicProducts.length" description="专题暂未关联在售商品" />
  </el-dialog>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { mallPortal, mallTopicProducts } from '@/api/mall'
const emit = defineEmits(['search'])
const router = useRouter(), portal = ref({}), topicVisible = ref(false), selectedTopic = ref(null), topicProducts = ref([]), loading = ref(false)
function openAd(ad) {
  if (ad.product_id) router.push(`/manager/store/products/${ad.product_id}`)
  else if (ad.link && /^(https?:\/\/|\/(?!\/))/.test(ad.link)) window.open(ad.link, '_blank', 'noopener,noreferrer')
}
async function openTopic(topic) {
  selectedTopic.value = topic
  topicProducts.value = []
  topicVisible.value = true
  loading.value = true
  try { topicProducts.value = (await mallTopicProducts(topic.id)).data.list } catch {} finally { loading.value = false }
}
onMounted(async () => { try { portal.value = (await mallPortal()).data } catch {} })
</script>

<style scoped>
.store-promotions { display:grid; gap:16px; }.ad-banner { width:100%;height:100%;border:0;padding:0;background:#e6f3eb;position:relative;cursor:pointer;border-radius:12px;overflow:hidden; }.ad-banner .el-image { width:100%;height:100%; }.ad-banner>span { position:absolute;bottom:18px;left:24px;background:#102237c9;color:white;padding:8px 15px;border-radius:7px; }.keyword-list { display:flex;align-items:center;gap:9px;flex-wrap:wrap; }.keyword-list>span { font-size:12px;color:#819082; }.topic-list { display:flex;gap:12px;overflow:auto; }.topic-list>button { flex:1;min-width:200px;display:flex;align-items:center;gap:12px;padding:15px;background:#f3f8f4;border:1px solid #dfebe2;border-radius:10px;text-align:left;cursor:pointer; }.topic-list .el-image { width:55px;height:55px;flex-shrink:0; }.topic-list p { max-width:230px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin:6px 0 0;color:#7c8c84;font-size:12px; }.topic-list button>span { margin-left:auto;color:#168771;font-size:12px;white-space:nowrap; }.topic-text { white-space:pre-wrap;line-height:1.8; }.topic-products { display:grid;grid-template-columns:repeat(3,1fr);gap:14px; }.topic-products button { display:grid;gap:10px;padding:14px;border:1px solid #dfe8e0;background:white;border-radius:10px;cursor:pointer; }.topic-products .el-image { width:100%;height:130px; }.topic-products span { color:#c15d41; } @media(max-width:600px) { .topic-products { grid-template-columns:repeat(2,1fr); } }
</style>
