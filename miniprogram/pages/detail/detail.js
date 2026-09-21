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
    posterSrc: '',
    loading: true,
    err: ''
  },

  onLoad(options) {
    const videoId = Number(options.videoId || 0);
    const base = api.baseUrl();
    this.setData({
      base: base,
      videoId: videoId,
      posterSrc: base + '/posters/' + videoId + '.jpg?v=2'
    });
    this.cachePoster();
    this.loadDetail();
    this.loadPreview();
  },

  /** 同首页：真机 <image> 引不了 http 图，先 downloadFile 到本地再显示 */
  cachePoster() {
    const url = this.data.posterSrc;
    wx.downloadFile({
      url: url,
      success: (r) => {
        if (r.statusCode === 200 && r.tempFilePath) {
          this.setData({ posterSrc: r.tempFilePath });
        }
      },
      fail: () => {}
    });
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

  /**
   * 点海报看大图。urls 用本地临时路径（cachePoster 下好的），
   * 真机上 http 图片既进不了 <image> 也进不了 previewImage，只有本地文件能用。
   */
  previewPoster() {
    const src = this.data.posterSrc;
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

  goMember() {
    wx.switchTab({ url: '/pages/member/member' });
  }
});
