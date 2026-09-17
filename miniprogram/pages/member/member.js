// 会员中心：套餐 + 开卡/续费 + 我的券提醒
const api = require('../../utils/api.js');

Page({
  data: {
    member: null,
    plans: [],
    selectedMonths: 0,
    payAmount: '0.00',
    coupons: [],
    selectedId: 0,
    preview: null,
    submitting: false
  },

  onShow() {
    this.loadInfo();
  },

  loadInfo() {
    api.post('/api/wx/member/info', {}).then((res) => {
      const plans = res.plans || [];
      this.setData({
        member: {
          isMember: res.isMember,
          expireTime: api.fmtTime(res.expireTime),
          discountRate: res.discountRate
        },
        plans: plans
      });
      if (!this.data.selectedMonths && plans.length > 0) {
        this.choosePlan({ currentTarget: { dataset: { months: plans[0].months } } });
      }
      this.loadCoupons();
    }).catch(() => {});
  },

  loadCoupons() {
    api.post('/api/wx/coupon/mine', { status: 0 }).then((list) => {
      this.setData({ coupons: list || [] });
      this.refresh();
    }).catch(() => {});
  },

  choosePlan(e) {
    const months = Number(e.currentTarget.dataset.months);
    this.setData({ selectedMonths: months });
    api.post('/api/wx/order/preview', { months: months }).then((p) => {
      this.setData({ preview: p });
      this.refresh();
    }).catch(() => {});
  },

  chooseCoupon(e) {
    this.setData({ selectedId: Number(e.currentTarget.dataset.id || 0) });
    this.refresh();
  },

  refresh() {
    const p = this.data.preview;
    if (!p) {
      return;
    }
    let amount = 0;
    for (const c of this.data.coupons) {
      if (c.id === this.data.selectedId) {
        amount = Number(c.amount);
      }
    }
    let pay = Number(p.priceAfterMember) - amount;
    if (pay < 0) {
      pay = 0;
    }
    this.setData({ payAmount: pay.toFixed(2) });
  },

  open() {
    if (this.data.submitting || !this.data.selectedMonths) {
      return;
    }
    this.setData({ submitting: true });
    const body = { months: this.data.selectedMonths };
    if (this.data.selectedId) {
      body.userCouponId = this.data.selectedId;
    }
    api.post('/api/wx/member/open', body).then((res) => {
      wx.showToast({ title: '开通成功', icon: 'success' });
      this.setData({ submitting: false, selectedId: 0 });
      this.loadInfo();
    }).catch(() => {
      this.setData({ submitting: false });
    });
  },

  goIndex() {
    wx.switchTab({ url: '/pages/index/index' });
  }
});
