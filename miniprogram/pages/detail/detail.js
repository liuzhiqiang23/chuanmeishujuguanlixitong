// 影片详情：海报 + 简介 + 观影券价格（会员价由后端算）
const api = require('../../utils/api.js');

Page({
  data: {
    base: '',
    videoId: 0,
    detail: null,
    preview: null,
    finalPrice: '--',
    couponCount: 0,
    loading: true,
    err: ''
  },

  onLoad(options) {
    const videoId = Number(options.videoId || 0);
    this.setData({ base: api.baseUrl(), videoId: videoId });
    this.loadDetail();
    this.loadPreview();
  },

  loadDetail() {
    api.post('/api/admin/video/getVideoDetailByVideoId/' + this.data.videoId, {},
      { needLogin: false }).then((d) => {
      this.setData({ detail: d, loading: false });
    }).catch((r) => {
      this.setData({ loading: false, err: (r && r.message) || '影片加载失败' });
    });
  },

  /** 价格明细（含会员价和可用券）都以后端为准，前端不自己算钱 */
  loadPreview() {
    api.post('/api/wx/order/preview', { videoId: this.data.videoId }).then((p) => {
      // WXML 里不能调 toFixed 这类方法，金额都在这里算好
      const final = Number(p.priceAfterMember) - Number(p.bestCouponDiscount || 0);
      this.setData({
        preview: p,
        finalPrice: final.toFixed(2),
        couponCount: (p.usableCoupons || []).length
      });
    }).catch(() => {});
  },

  buy() {
    wx.navigateTo({ url: '/pages/confirm/confirm?videoId=' + this.data.videoId });
  },

  goMember() {
    wx.switchTab({ url: '/pages/member/member' });
  }
});
