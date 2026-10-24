<template><el-dialog class="m-sheet" :model-value="modelValue" :title="title" width="min(480px,100vw)" top="0" append-to-body :close-on-click-modal="false" @update:model-value="$emit('update:modelValue',$event)"><slot /><template v-if="$slots.footer" #footer><slot name="footer" /></template></el-dialog></template>
<script setup>
defineProps({modelValue:Boolean,title:String})
defineEmits(['update:modelValue'])
</script>
