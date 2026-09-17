// 确认订单：价格明细 + 选券 + 提交
// 所有金额都由后端 /api/wx/order/preview 算，前端只做展示和"选了哪张券"的本地重算。
const api = require('../../utils/api.js');

Page({
  data: {
    videoId: 0,
    months: 0,
    preview: null,
    coupons: [],
    selectedId: 0,     // 0 = 不用券
    payAmount: '0.00',
    saving: '0.00',
    submitting: false
  },

  onLoad(options) {
    const videoId = Number(options.videoId || 0);
    const months = Number(options.months || 0);
    this.setData({ videoId: videoId, months: months });
    this.loadPreview();
  },

  loadPreview() {
    const body = this.data.videoId ? { videoId: this.data.videoId } : { months: this.data.months };
    api.post('/api/wx/order/preview', body).then((p) => {
      this.setData({ preview: p, coupons: p.usableCoupons || [] });
      this.recalc(0);
    }).catch(() => {});
  },

  /** 选券：只改本地展示，真正的校验和核销在后端 */
  choose(e) {
    const id = Number(e.currentTarget.dataset.id || 0);
    this.recalc(id);
  },

  recalc(couponId) {
    const p = this.data.preview;
    if (!p) {
      return;
    }
    let couponAmount = 0;
    for (const c of this.data.coupons) {
      if (c.id === couponId) {
        couponAmount = Number(c.amount);
      }
    }
    const after = Number(p.priceAfterMember);
    let pay = after - couponAmount;
    if (pay < 0) {
      pay = 0;
    }
    // 省下的钱 = 会员折扣 + 券
    const saved = Number(p.memberDiscount || 0) + Math.min(couponAmount, after);
    this.setData({
      selectedId: couponId,
      payAmount: pay.toFixed(2),
      saving: saved.toFixed(2)
    });
  },

  submit() {
    if (this.data.submitting) {
      return;
    }
    this.setData({ submitting: true });
    const body = this.data.videoId ? { videoId: this.data.videoId } : { months: this.data.months };
    if (this.data.selectedId) {
      body.userCouponId = this.data.selectedId;
    }
    api.post('/api/wx/order/create', body).then((order) => {
      wx.showToast({ title: '下单成功', icon: 'success' });
      setTimeout(() => {
        wx.switchTab({ url: '/pages/mine/mine' });
      }, 800);
    }).catch(() => {
      this.setData({ submitting: false });
    });
  }
});
