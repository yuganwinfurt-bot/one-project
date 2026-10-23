"""运营页面字段白名单，同时用于服务端校验和页面表单。"""
def field(key, label, type='text', **kwargs):
    return dict(key=key, label=label, type=type, **kwargs)


CONTENT = {
    'brands': dict(title='品牌制造商', fields=[field('description', '品牌介绍', 'textarea'), field('image_url', '品牌图片', 'image')]),
    'categories': dict(title='商品类目', fields=[field('parent_id', '上级类目', 'category'), field('description', '类目介绍', 'textarea'), field('image_url', '类目图片', 'image')]),
    'faqs': dict(title='通用问题', fields=[field('answer', '解答', 'textarea', required=True)]),
    'keywords': dict(title='关键词', fields=[field('redirect_keyword', '搜索词', required=True)]),
    'ads': dict(title='广告管理', fields=[field('image_url', '广告图片', 'image', required=True), field('product_id', '关联商品', 'product'), field('link', '跳转地址', 'url'), field('starts_at', '开始时间', 'datetime'), field('ends_at', '结束时间', 'datetime')]),
    'topics': dict(title='专题管理', fields=[field('content', '专题内容', 'textarea', required=True), field('image_url', '封面图片', 'image'), field('product_ids', '专题商品', 'products')]),
    'coupons': dict(title='优惠券管理', fields=[field('discount', '减免金额（元）', 'money', required=True, min=0.01), field('min_amount', '使用门槛（元）', 'money', default=0), field('quantity', '发放总量', 'number', required=True, min=1, max=1000000), field('starts_at', '开始时间', 'datetime', required=True), field('ends_at', '结束时间', 'datetime', required=True)]),
    'group-rules': dict(title='团购规则', fields=[field('product_id', '团购商品', 'product', required=True), field('price', '团购单价（元）', 'money', required=True, min=0.01), field('target_size', '成团人数', 'number', required=True, min=2, max=99), field('hours', '组团时限（小时）', 'number', required=True, min=1, max=168), field('starts_at', '开始时间', 'datetime', required=True), field('ends_at', '结束时间', 'datetime', required=True)]),
    'notices': dict(title='通知管理', fields=[field('content', '通知内容', 'textarea', required=True), field('audience', '接收人群', 'select', options=[{'value': 'all', 'label': '所有用户'}, {'value': 'customer', 'label': '买家'}, {'value': 'user', 'label': '运营人员'}], default='all'), field('starts_at', '发布时间', 'datetime'), field('ends_at', '结束时间', 'datetime')]),
    'roles': dict(title='角色管理', admin_only=True, fields=[field('permissions', '可使用的运营模块', 'permissions', required=True), field('user_ids', '绑定运营账号', 'staff')]),
}
PERMISSIONS = {key: value['title'] for key, value in CONTENT.items() if key != 'roles'} | {
    'members': '会员管理', 'addresses': '收货地址', 'favorites': '会员收藏', 'footprints': '会员足迹',
    'search-history': '搜索历史', 'feedback': '意见反馈', 'regions': '行政区域', 'catalog-products': '商品品牌与类目',
    'groups': '团购活动', 'storage': '文件存储', 'statistics': '统计报表',
}
SETTINGS = {
    'mall': dict(title='商场配置', fields=[field('name', '商城名称', required=True, default='电商分析平台'), field('description', '商城介绍', 'textarea'), field('phone', '客服电话'), field('email', '联系邮箱'), field('address', '联系地址')]),
    'shipping': dict(title='运费配置', fields=[field('base_fee', '每次结算运费（元）', 'money', default=0), field('free_over', '满额包邮门槛（元，0 为不启用）', 'money', default=0)]),
    'order': dict(
        title='订单配置',
        fields=[
            field('unpaid_timeout_minutes', '用户下单后超时', 'number', min=1, max=10080, default=30, unit='分钟', help='用户未付款，则订单自动取消并返还库存、释放优惠券。', required=True),
            field('auto_confirm_days', '订单发货后超期', 'number', min=1, max=90, default=7, unit='天', help='未确认收货，则订单自动确认收货；处理中售后暂停自动确认。', required=True),
            field('review_expire_days', '确认收货后超期', 'number', min=1, max=365, default=7, unit='天', help='未评价商品，则取消评价资格。', required=True),
            field('checkout_enabled', '允许创建订单', 'switch', default=True),
            field('max_quantity', '单项商品购买上限', 'number', min=1, max=99, default=99),
        ],
    ),
    'miniapp': dict(title='小程序配置', fields=[field('app_id', '小程序 AppID'), field('name', '小程序名称'), field('description', '小程序介绍', 'textarea')], hint='保存小程序展示资料；微信登录、支付需要另行接入微信服务。请勿在此填写 AppSecret。'),
}
READONLY = {
    'members': ('会员管理', [('username', '账号'), ('name', '姓名'), ('phone', '手机号'), ('email', '邮箱'), ('status', '状态'), ('create_time', '注册时间')]),
    'addresses': ('收货地址', [('user_id', '用户 ID'), ('username', '用户'), ('receiver_name', '收货人'), ('phone', '电话'), ('address', '详细地址'), ('is_default', '默认地址')]),
    'favorites': ('会员收藏', [('user_id', '用户 ID'), ('username', '用户'), ('product_name', '商品'), ('create_time', '收藏时间')]),
    'footprints': ('会员足迹', [('user_id', '用户 ID'), ('username', '用户'), ('product_name', '商品'), ('create_time', '浏览时间')]),
    'search-history': ('搜索历史', [('user_id', '用户 ID'), ('username', '用户'), ('keyword', '关键词'), ('create_time', '搜索时间')]),
    'feedback': ('意见反馈', [('user_id', '用户 ID'), ('username', '用户'), ('name', '主题'), ('content', '反馈内容'), ('contact', '联系方式'), ('reply', '回复'), ('status', '状态'), ('create_time', '提交时间')]),
    'catalog-products': ('商品品牌与类目', [('name', '商品'), ('category', '类目'), ('brand', '品牌'), ('shelf_status', '销售状态')]),
    'groups': ('团购活动', [('id', '团号'), ('product_name', '商品'), ('leader', '团长'), ('member_count', '已参团'), ('target_size', '成团人数'), ('price', '团购价'), ('status', '状态'), ('expires_at', '截止时间')]),
    'storage': ('文件存储', [('name', '文件名'), ('size', '字节数'), ('url', '文件地址'), ('update_time', '更新时间')]),
}
