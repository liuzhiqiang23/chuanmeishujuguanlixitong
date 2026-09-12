// 注意：这里不能 `import store from '@/store'`。
// 该 mixin 被 layout/index.vue 引入，而 layout 又被 router.js 引入；
// store/modules/router.js 又引回 @/router 的 constantRoutes，形成循环依赖，
// 打包后在模块初始化阶段抛出 "Cannot access 'constantRoutes' before initialization" 导致白屏。
// 因此改用在运行时通过 this.$store 访问（方法已在 Vue 3 中被绑定到组件实例）。

const { body } = document
const WIDTH = 992 // refer to Bootstrap's responsive design

export default {
  watch: {
    $route (route) {
      if (this.device === 'mobile' && this.sidebar.opened) {
        this.$store.dispatch('app/closeSideBar', { withoutAnimation: false })
      }
    }
  },
  beforeMount () {
    window.addEventListener('resize', this.$_resizeHandler)
  },
  beforeUnmount () {
    window.removeEventListener('resize', this.$_resizeHandler)
  },
  mounted () {
    const isMobile = this.$_isMobile()
    if (isMobile) {
      this.$store.dispatch('app/toggleDevice', 'mobile')
      this.$store.dispatch('app/closeSideBar', { withoutAnimation: true })
    }
  },
  methods: {
    // use $_ for mixins properties
    // https://vuejs.org/v2/style-guide/index.html#Private-property-names-essential
    $_isMobile () {
      const rect = body.getBoundingClientRect()
      return rect.width - 1 < WIDTH
    },
    $_resizeHandler () {
      if (!document.hidden) {
        const isMobile = this.$_isMobile()
        this.$store.dispatch('app/toggleDevice', isMobile ? 'mobile' : 'desktop')

        if (isMobile) {
          this.$store.dispatch('app/closeSideBar', { withoutAnimation: true })
        }
      }
    }
  }
}
