<template>
  <div class="page-container customer-page" v-loading="loading">
    <section class="content-card customer-page__heading">
      <div>
        <h1>我的地址</h1>
        <p>维护收货人、联系电话和收货地址；提交订单时可以选择使用。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreate">新增地址</el-button>
    </section>

    <section v-if="addresses.length" class="address-grid">
      <article v-for="address in addresses" :key="address.id" class="content-card address-card">
        <header class="address-card__header">
          <div>
            <strong>{{ address.receiver_name }}</strong>
            <span>{{ address.phone }}</span>
          </div>
          <el-tag v-if="address.is_default" type="success" effect="light" round>默认地址</el-tag>
        </header>
        <p class="address-card__location">
          {{ address.province }}{{ address.city }}{{ address.district }}{{ address.detail }}
        </p>
        <footer class="address-card__actions">
          <el-button v-if="!address.is_default" link type="primary" @click="setDefault(address)">
            设为默认
          </el-button>
          <el-button link type="primary" @click="openEdit(address)">编辑</el-button>
          <el-button link type="danger" @click="removeAddress(address)">删除</el-button>
        </footer>
      </article>
    </section>

    <section v-else-if="!loading" class="content-card customer-empty">
      <el-empty description="还没有收货地址">
        <el-button type="primary" @click="openCreate">添加收货地址</el-button>
      </el-empty>
    </section>

    <el-dialog
      v-model="dialogVisible"
      :title="form.id ? '编辑收货地址' : '新增收货地址'"
      width="560px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="92px">
        <el-form-item label="选择地区"><el-cascader :props="{ lazy: true, lazyLoad: loadRegionOptions, value:'name', label:'name', leaf:'leaf', emitPath:true }" placeholder="选择省 / 市 / 区县，也可在下方填写" clearable style="width:100%" @change="selectRegion" /></el-form-item>
        <el-form-item label="收货人" prop="receiver_name">
          <el-input v-model="form.receiver_name" maxlength="50" placeholder="请输入收货人姓名" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" maxlength="30" placeholder="请输入联系电话" />
        </el-form-item>
        <div class="address-region-fields">
          <el-form-item label="省份" prop="province">
            <el-input v-model="form.province" maxlength="50" placeholder="省/自治区" />
          </el-form-item>
          <el-form-item label="城市" prop="city">
            <el-input v-model="form.city" maxlength="50" placeholder="城市" />
          </el-form-item>
          <el-form-item label="区县" prop="district">
            <el-input v-model="form.district" maxlength="50" placeholder="区/县" />
          </el-form-item>
        </div>
        <el-form-item label="详细地址" prop="detail">
          <el-input
            v-model="form.detail"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
            placeholder="街道、门牌号、小区或楼栋信息"
          />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveAddress">保存地址</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { useCustomerAddresses } from '@/composables/customer/CustomerAddresses'

const {
onMounted,
reactive,
ref,
ElMessage,
ElMessageBox,
Plus,
mallRegionChildren,
createAddress,
deleteAddress,
getAddresses,
updateAddress,
loadRegionOptions,
selectRegion,
addresses,
loading,
saving,
dialogVisible,
formRef,
emptyForm,
form,
rules,
load,
openCreate,
openEdit,
saveAddress,
setDefault,
removeAddress
} = useCustomerAddresses()
</script>

<style scoped>
.customer-page { display: grid; gap: 18px; }
.customer-page__heading { display: flex; align-items: center; justify-content: space-between; gap: 20px; }
.customer-page__heading h1 { margin: 0; color: #102237; font-size: 22px; }
.customer-page__heading p { margin: 6px 0 0; color: #728396; font-size: 14px; }
.address-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 18px; }
.address-card { padding: 22px; }
.address-card__header { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.address-card__header > div { display: flex; flex-wrap: wrap; align-items: center; gap: 14px; }
.address-card__header strong { color: #17324b; font-size: 16px; }
.address-card__header span { color: #62768a; }
.address-card__location { min-height: 48px; margin: 16px 0; color: #62768a; line-height: 1.7; }
.address-card__actions { display: flex; justify-content: flex-end; gap: 8px; padding-top: 12px; border-top: 1px solid #edf1ef; }
.address-region-fields { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.address-region-fields :deep(.el-form-item) { min-width: 0; margin-right: 0; }
.customer-empty { padding: 40px 20px; }
@media (max-width: 700px) { .customer-page__heading { align-items: flex-start; flex-direction: column; } .address-region-fields { grid-template-columns: 1fr; gap: 0; } }
</style>
