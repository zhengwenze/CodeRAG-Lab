<template>
  <el-config-provider :locale="localeConfig" :size="config.size" :zIndex="config.zIndex">
    <router-view />
  </el-config-provider>
</template>

<script setup>
import { computed, reactive } from 'vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

const localeConfig = computed(() => zhCn)

const config = reactive({
  size: 'default',
  zIndex: 2000,
})
</script>

<style>
html,
body,
#app {
  height: 100%;
  margin: 0;
  padding: 0;
}
</style>
