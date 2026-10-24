<template>
  <el-menu :default-active="active" :default-openeds="opened" :collapse="collapsed" :collapse-transition="true" router class="sidebar-menu commerce-sidebar" background-color="transparent" text-color="#566477" active-text-color="#102237">
    <el-menu-item v-if="staff" index="/manager/chat"><el-icon><ChatDotRound /></el-icon><template #title>智能运营助手</template></el-menu-item>
    <el-menu-item v-if="staff" index="/manager/home"><el-icon><House /></el-icon><template #title>系统首页</template></el-menu-item>
    <el-menu-item index="/manager/store"><el-icon><Shop /></el-icon><template #title>商品首页</template></el-menu-item>
    <el-menu-item index="/mini-store"><el-icon><Goods /></el-icon><template #title>小程序商城</template></el-menu-item>
    <el-sub-menu v-if="staff" index="analysis"><template #title><el-icon><DataAnalysis /></el-icon><span>智能分析</span><el-icon class="menu-chevron"><ArrowDown /></el-icon></template>
      <el-menu-item v-for="item in analysisItems" :key="item[0]" :index="item[0]">{{ item[1] }}</el-menu-item>
    </el-sub-menu>
    <template v-if="!staff">
      <el-menu-item index="/manager/messages?tab=support"><el-icon><Service /></el-icon><template #title>联系客服</template></el-menu-item>
      <el-menu-item index="/manager/feedback"><el-icon><ChatDotRound /></el-icon><template #title>意见反馈</template></el-menu-item>
      <el-menu-item index="/manager/help"><el-icon><Service /></el-icon><template #title>公告与帮助</template></el-menu-item>
      <el-menu-item index="/manager/offers"><el-icon><Present /></el-icon><template #title>优惠与团购</template></el-menu-item>
      <el-sub-menu index="shopping"><template #title><el-icon><ShoppingCart /></el-icon><span>我的购物</span><el-icon class="menu-chevron"><ArrowDown /></el-icon></template>
        <el-menu-item index="/manager/cart">购物车</el-menu-item><el-menu-item index="/manager/favorites">我的收藏</el-menu-item><el-menu-item index="/manager/my-orders">订单记录</el-menu-item><el-menu-item index="/manager/addresses">我的地址</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="system"><template #title><el-icon><Setting /></el-icon><span>系统管理</span><el-icon class="menu-chevron"><ArrowDown /></el-icon></template>
        <el-menu-item index="/manager/messages"><span>我的消息 <el-badge v-if="customerUnread" :value="customerUnread" :max="99" class="nav-badge" /></span></el-menu-item>
        <el-menu-item index="/manager/profile">个人资料</el-menu-item>
      </el-sub-menu>
    </template>
    <template v-else>
      <template v-for="group in visibleGroups" :key="group.id">
        <el-sub-menu :index="group.id"><template #title><el-icon><component :is="group.icon" /></el-icon><span>{{ group.title }}</span><el-icon class="menu-chevron"><ArrowDown /></el-icon></template>
          <el-menu-item v-for="[key,label] in group.items" :key="key" :index="mallPath(key)">{{ label }}</el-menu-item>
          <template v-if="group.id === 'goods'"><el-menu-item index="/manager/products">商品列表</el-menu-item><el-menu-item v-if="['admin','user'].includes(user?.role)" index="/manager/product-listing">商品上架</el-menu-item><el-menu-item index="/manager/reviews">商品评论</el-menu-item></template>
          <template v-if="group.id === 'mall'"><el-menu-item index="/manager/orders">订单管理</el-menu-item><el-menu-item index="/manager/after-sales">售后工单</el-menu-item></template>
          <template v-if="group.id === 'system'">
            <el-menu-item v-if="user?.role === 'admin'" index="/manager/user">账号管理</el-menu-item>
            <el-menu-item index="/manager/platform-logs">操作日志</el-menu-item>
            <el-menu-item index="/manager/message-center"><span>消息中心 <el-badge v-if="staffUnread" :value="staffUnread" :max="99" class="nav-badge" /></span></el-menu-item>
            <el-menu-item index="/manager/profile">个人资料</el-menu-item>
          </template>
        </el-sub-menu>
      </template>
    </template>
    <el-menu-item v-if="staff" index="/manager/help"><el-icon><Service /></el-icon><template #title>公告与帮助</template></el-menu-item>
  </el-menu>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { House, Shop, ShoppingCart, Present, Service, ChatDotRound, Setting, Goods, DataAnalysis, ArrowDown } from '@element-plus/icons-vue'
import { mallGroups, mallPath, mallPermissionKey } from '@/utils/mallNavigation'
import { mallPermissions } from '@/api/mall'
const props = defineProps({ active:String, collapsed:Boolean, user:Object, customerUnread:Number, staffUnread:Number })
const staff = computed(() => ['admin','user'].includes(props.user?.role))
const granted = ref([])
const opened = computed(() => {
  if (['/manager/profile','/manager/password','/manager/message-center','/manager/messages','/manager/user','/manager/platform-logs'].includes(props.active)) return ['system']
  if (['/manager/orders','/manager/after-sales'].includes(props.active)) return ['mall']
  if (['/manager/products','/manager/product-listing','/manager/reviews'].includes(props.active)) return ['goods']
  const group = mallGroups.find(g => g.items.some(([key]) => mallPath(key) === props.active))
  return group ? [group.id] : props.active?.includes('/manager/mall/') ? [] : ['analysis','shopping']
})
const visibleGroups = computed(() => mallGroups.map(g => ({ ...g, items:g.items.filter(([key]) => granted.value.includes(mallPermissionKey(key))) })).filter(g => g.items.length || ['mall','system','goods'].includes(g.id)))
const analysisItems = [['/manager/history','运行历史'],['/manager/reports','诊断报告'],['/manager/metrics','观测看板'],['/manager/semantic','语义检索']]
async function refreshPermissions() {
  if (!staff.value) return
  try { granted.value = (await mallPermissions()).data.permissions } catch { granted.value = [] }
}
onMounted(() => { refreshPermissions(); window.addEventListener('mall-permissions-updated', refreshPermissions) })
onUnmounted(() => window.removeEventListener('mall-permissions-updated', refreshPermissions))
</script>

<style scoped>
.commerce-sidebar { border-right:0; min-height:0; overflow-y:auto; overflow-x:hidden; }
.commerce-sidebar:not(.el-menu--collapse) { width:100%; }
.commerce-sidebar :deep(.el-sub-menu__title), .commerce-sidebar :deep(.el-menu-item) { border-radius:9px; min-height:44px; height:44px; line-height:44px; }
.commerce-sidebar :deep(.el-sub-menu__title) { margin-top:5px; font-weight:600; }
.commerce-sidebar :deep(.el-sub-menu__icon-arrow) { display:none !important; }
.commerce-sidebar :deep(.menu-chevron) { flex:0 0 12px; width:12px; height:12px; margin-left:auto; color:#aebac8; transition:transform .2s ease; }
.commerce-sidebar :deep(.el-sub-menu.is-opened > .el-sub-menu__title .menu-chevron) { transform:rotate(180deg); }
.commerce-sidebar.el-menu--collapse :deep(.menu-chevron), .commerce-sidebar.el-menu--collapse :deep(.el-sub-menu__icon-arrow) { display:none !important; }
.commerce-sidebar :deep(.el-sub-menu .el-menu-item) { font-size:13px; min-width:0; }
.commerce-sidebar :deep(.el-menu) { background:transparent; }
.commerce-sidebar :deep(.is-active > .el-sub-menu__title) { color:#159c80; }
.commerce-sidebar :deep(.el-menu-item.is-active) { color:#0e7864; background:#daf0e5; }
.nav-badge { margin-left:9px; }
</style>
