<template>
  <a v-if="external" :href="to" target="_blank" rel="noopener">
    <slot />
  </a>
  <router-link v-else :to="to">
    <slot />
  </router-link>
</template>

<script>
import { isExternal } from '@/utils/validate'

export default {
  name: 'AppLink',
  props: {
    to: {
      type: String,
      required: true
    }
  },
  computed: {
    external () {
      return isExternal(this.to)
    }
  }
}
</script>
