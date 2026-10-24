<template>

<div class="m-view"><MiniHeader title="收货地址" /><div class="m-scroll" v-loading="loading"><article v-for="address in addresses" :key="address.id" class="m-card"><div class="m-address-person"><strong>{{ address.receiver_name }}</strong><span>{{ address.phone }}</span><b v-if="address.is_default" class="m-pill">默认</b></div><p class="m-address-location">{{ address.province }}{{ address.city }}{{ address.district }}{{ address.detail }}</p><div class="m-actions"><button v-if="!address.is_default" class="m-quiet" @click="setDefault(address)">设为默认</button><button class="m-secondary" @click="openEdit(address)">编辑</button><button class="m-secondary" @click="removeAddress(address)">删除</button></div></article><div v-if="!loading && !addresses.length" class="m-empty"><span>⌖</span><p>还没有收货地址</p></div></div><footer class="m-footer"><button class="m-primary m-wide" @click="openCreate">＋ 新增收货地址</button></footer>
    <MiniSheet
      v-model="dialogVisible"
      :title="form.id ? '编辑收货地址' : '新增收货地址'"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
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
    </MiniSheet>
</div>
</template>
<script setup>
import MiniHeader from '@/components/mini/MiniHeader.vue'
import MiniSheet from '@/components/mini/MiniSheet.vue'
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
.m-address-person{display:flex;align-items:center;gap:9px}.m-address-person strong{font-size:15px}.m-address-person>span{color:#97a3ad;font-size:13px}.m-address-person .m-pill{margin-left:auto}.m-address-location{font-size:13px;line-height:1.8;color:#6e808d;overflow-wrap:anywhere}.m-wide{width:100%}
</style>
