// 首页：会员状态条 + 可领券 + 热门影片（复用后台已有的影片列表接口）
const api = require('../../utils/api.js');

Page({
  data: {
    base: '',
    member: null,
    videos: [],
    coupons: [],
    loading: true,
    pageIndex: 1,
    hasNext: false,
    status: ''
  },

  onLoad() {
    this.setData({ base: api.baseUrl() });
  },

  onShow() {
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
        price: this.videoPrice(v.voteAverage)
      }));
      this.setData({
        videos: page === 1 ? list : this.data.videos.concat(list),
        pageIndex: res.pageNum,
        hasNext: res.hasNextPage,
        loading: false,
        status: '共 ' + res.total + ' 部，第 ' + res.pageNum + ' / ' + res.pages + ' 页'
      });
    }).catch(() => {
      this.setData({ loading: false, status: '影片加载失败，后端起了吗？' });
    });
  },

  /** 和后台 OrderServiceImpl.videoPrice 保持一致：>=8.5 → 12 元，>=7.5 → 9 元，其余 6 元 */
  videoPrice(vote) {
    const v = Number(vote || 0);
    if (v >= 8.5) {
      return '12.00';
    }
    if (v >= 7.5) {
      return '9.00';
    }
    return '6.00';
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
  }
});
