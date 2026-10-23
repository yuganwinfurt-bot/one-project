export const mallGroups = [
  { id:'members', title:'用户管理', icon:'User', items:[['members','会员管理'],['addresses','收货地址'],['favorites','会员收藏'],['footprints','会员足迹'],['search-history','搜索历史'],['feedback','意见反馈']] },
  { id:'mall', title:'商场管理', icon:'Shop', items:[['regions','行政区域'],['brands','品牌制造商'],['faqs','通用问题'],['keywords','关键词']] },
  { id:'promotion', title:'推广管理', icon:'Present', items:[['ads','广告管理'],['coupons','优惠券管理'],['topics','专题管理'],['group-rules','团购规则'],['groups','团购活动']] },
  { id:'system', title:'系统管理', icon:'Setting', items:[['notices','通知管理'],['roles','角色管理'],['storage','文件存储']] },
  { id:'config', title:'配置管理', icon:'Tools', items:[['settings-mall','商场配置'],['settings-shipping','运费配置'],['settings-order','订单配置'],['settings-miniapp','小程序配置']] },
  { id:'statistics', title:'统计报表', icon:'TrendCharts', items:[['statistics-users','用户统计'],['statistics-orders','订单统计'],['statistics-products','商品统计']] },
  { id:'goods', title:'商品管理', icon:'Goods', items:[['categories','商品类目'],['catalog-products','商品归属']] }
]
export const mallTitles = Object.fromEntries(mallGroups.flatMap(group => group.items))
export const mallPath = (resource) => `/manager/mall/${resource}`
export const mallPermissionKey = (resource) => resource.startsWith('settings-') ? 'settings' : resource.startsWith('statistics-') ? 'statistics' : resource
