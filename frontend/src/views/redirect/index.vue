<template>
  <div />
</template>

<script>
export default {
  name: 'Redirect',
  created () {
    const { params, query } = this.$route
    const { path } = params
    this.$router.replace({ path: '/' + path, query })
  }
}
</script>
