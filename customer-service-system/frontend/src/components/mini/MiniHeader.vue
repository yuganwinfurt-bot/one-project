<template><header class="m-header"><button type="button" class="m-icon-button" aria-label="返回" @click="router.push(back)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="m14 5-7 7 7 7" /></svg></button><h1>{{ title }}</h1><slot name="right"><span class="m-header-spacer"></span></slot></header></template>
<script setup>
import {useRouter} from 'vue-router'
defineProps({title:String,back:{type:String,default:'/mini-store?tab=profile'}})
const router=useRouter()
</script>
