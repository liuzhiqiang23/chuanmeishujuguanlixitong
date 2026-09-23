// 首页：会员状态条 + 可领券 + 热门影片（复用后台已有的影片列表接口）
const api = require('../../utils/api.js');

Page({
  data: {
    base: '',
    member: null,
    videos: [],
    coupons: [],
    cates: [],
    loading: true,
    pageIndex: 1,
    hasNext: false,
    status: '',
    isAdmin: false
  },

  onLoad() {
    this.setData({ base: api.baseUrl() });
    this.loadCates();
  },

  onShow() {
    // isAdmin 是登录成功后才写进 globalData 的，onLoad 时往往还没回来，
    // 所以每次页面显示都重读一次，管理员从别的页面切回来也能立刻看到删除按钮
    const app = getApp();
    this.setData({ isAdmin: (app.globalData && app.globalData.isAdmin) === true });
    this.loadMember();
    this.loadCoupons();
    this.loadVideos(1);
  },

  loadMember() {
    api.post('/api/wx/member/info', {}).then((res) => {
      this.setData({
        member: {
          isMember: res.isMember,
          expireTime: api.fmtTime(res.expireTime),
          discountRate: res.discountRate
        }
      });
    }).catch(() => {});
  },

  /** 首页分类宫格：和分类页同一个接口，只取前 12 个（按影片数排序，热度高的在前） */
  loadCates() {
    api.post('/api/wx/category/list', { minCount: 20, limit: 24 }, { needLogin: false }).then((list) => {
      this.setData({ cates: (list || []).slice(0, 12) });
    }).catch(() => {});
  },

  /** 点宫格里的分类：进分类页并直接选中该分类 */
  goCategoryTag(e) {
    const id = e.currentTarget.dataset.id;
    const name = e.currentTarget.dataset.name || '';
    wx.navigateTo({ url: '/pages/category/category?tagId=' + id + '&tagName=' + encodeURIComponent(name) });
  },

  loadCoupons() {
    api.post('/api/wx/coupon/list', {}).then((list) => {
      this.setData({ coupons: list || [] });
    }).catch(() => {});
  },

  loadVideos(page) {
    this.setData({ loading: true, status: '加载中...' });
    // 影片列表用的是后台已有的接口，不在 /api/wx 下
    api.post('/api/admin/video/page/list', {
      pageIndex: page,
      pageSize: 10
    }, { needLogin: false }).then((res) => {
      const list = (res.list || []).map((v) => ({
        videoId: v.videoId,
        videoName: v.videoName,
        voteAverage: v.voteAverage,
        popularity: v.popularity,
        price: api.videoPrice(v.voteAverage),
        posterSrc: api.posterUrl(v.videoId)
      }));
      const prevLen = page === 1 ? 0 : this.data.videos.length;
      this.setData({
        videos: page === 1 ? list : this.data.videos.concat(list),
        pageIndex: res.pageNum,
        hasNext: res.hasNextPage,
        loading: false,
        status: '共 ' + res.total + ' 部，第 ' + res.pageNum + ' / ' + res.pages + ' 页'
      });
      api.cachePosters(this, 'videos', prevLen, list.length);
    }).catch(() => {
      this.setData({ loading: false, status: '影片加载失败，后端起了吗？' });
    });
  },

  onReachBottom() {
    if (this.data.hasNext && !this.data.loading) {
      this.loadVideos(this.data.pageIndex + 1);
    }
  },

  onPullDownRefresh() {
    this.loadMember();
    this.loadCoupons();
    this.loadVideos(1);
    wx.stopPullDownRefresh();
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/detail/detail?videoId=' + id });
  },

  /** 点海报看大图。用 catchtap 拦下，不会连带触发整行的进详情 */
  previewPoster(e) {
    const src = e.currentTarget.dataset.src;
    if (!src) {
      return;
    }
    wx.previewImage({
      urls: [src],
      current: src,
      fail: () => {
        wx.showToast({ title: '图片还没加载完，稍后再点', icon: 'none' });
      }
    });
  },

  /** 管理员删片：后端每次都会再校验一次 role，前端只是不给普通用户显示按钮 */
  removeVideo(e) {
    const id = e.currentTarget.dataset.id;
    const name = e.currentTarget.dataset.name || '';
    const that = this;
    wx.showModal({
      title: '删除影片',
      content: '确定删除《' + name + '》？会同时清掉它的标签关联，不可恢复。',
      confirmColor: '#E55A5A',
      success(res) {
        if (!res.confirm) {
          return;
        }
        api.post('/api/wx/admin/video/delete', { videoId: id }).then(() => {
          wx.showToast({ title: '已删除', icon: 'success' });
          const left = (that.data.videos || []).filter((v) => v.videoId !== id);
          that.setData({ videos: left, status: '共 ' + left.length + ' 部' });
        }).catch(() => {});
      }
    });
  },

  receiveCoupon(e) {
    const id = e.currentTarget.dataset.id;
    api.post('/api/wx/coupon/receive', { couponId: id }).then(() => {
      wx.showToast({ title: '领取成功', icon: 'success' });
      this.loadCoupons();
    }).catch(() => {});
  },

  goMember() {
    wx.switchTab({ url: '/pages/member/member' });
  },

  goMine() {
    wx.switchTab({ url: '/pages/mine/mine' });
  },

  goSearch() {
    wx.navigateTo({ url: '/pages/search/search' });
  },

  goCategory() {
    wx.navigateTo({ url: '/pages/category/category' });
  },

  /**
   * 分享给好友：把当前 userId 塞进路径，好友点开时 shareFrom 会带进 onLoad，
   * 由 app.js 在登录后调 /api/wx/coupon/share/receive 给双方发券。
   */
  onShareAppMessage() {
    const uid = getApp().globalData.userId || '';
    // 分享动作本身也给自己发一张奖励券（后端每人限 1 张，重复分享不会重复发）
    this.claimShareReward();
    return {
      title: '电影票务演示 —— 新用户领观影券',
      path: '/pages/index/index?shareFrom=' + uid
    };
  },

  claimShareReward() {
    api.post('/api/wx/coupon/share/reward', {}, { silent: true }).then((c) => {
      if (c && c.title) {
        wx.showToast({ title: '分享成功，送你「' + c.title + '」', icon: 'none', duration: 2500 });
      }
    }).catch(() => {});
  }
});
