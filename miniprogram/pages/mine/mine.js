// 我的：登录状态 + 会员卡 + 我的券 + 我的订单（含取消）
const api = require('../../utils/api.js');

Page({
  data: {
    userId: null,
    nickName: '',
    member: null,
    coupons: [],
    orders: [],
    couponFilter: -1,   // -1 全部，0 未使用，1 已使用，2 已过期
    tab: 'order',       // order | coupon
    isAdmin: false
  },

  onShow() {
    const app = getApp();
    this.setData({
      userId: (app.globalData && app.globalData.userId) || wx.getStorageSync('userId') || null,
      isAdmin: (app.globalData && app.globalData.isAdmin) === true
    });
    this.loadMember();
    this.loadCoupons();
    this.loadOrders();
  },

  /**
   * 管理员身份由后端白名单（wx.open-ids 那条配置）授予，登录时自动生效，
   * 这里只读全局标记来决定显不显示入口。
   */
  activateAdmin() {
    wx.showToast({ title: '管理员由后台配置，无需操作', icon: 'none' });
  },

  loadMember() {
    api.post('/api/wx/member/info', {}).then((res) => {
      this.setData({
        member: {
          isMember: res.isMember,
          expireTime: api.fmtTime(res.expireTime)
        }
      });
    }).catch(() => {});
  },

  loadCoupons() {
    const body = {};
    if (this.data.couponFilter >= 0) {
      body.status = this.data.couponFilter;
    }
    api.post('/api/wx/coupon/mine', body).then((list) => {
      const coupons = (list || []).map((c) => Object.assign({}, c, {
        expireText: api.fmtTime(c.expireTime),
        statusText: api.couponStatusText(c.status)
      }));
      this.setData({ coupons: coupons });
    }).catch(() => {});
  },

  loadOrders() {
    api.post('/api/wx/order/list', { pageIndex: 1, pageSize: 20 }).then((res) => {
      const orders = (res.list || []).map((o) => Object.assign({}, o, {
        createText: api.fmtTime(o.createTime, true),
        statusText: api.orderStatusText(o.status),
        canCancel: o.status === 1 && o.orderType === 1
      }));
      this.setData({ orders: orders });
    }).catch(() => {});
  },

  switchTab(e) {
    this.setData({ tab: e.currentTarget.dataset.tab });
  },

  filterCoupon(e) {
    this.setData({ couponFilter: Number(e.currentTarget.dataset.status) });
    this.loadCoupons();
  },

  cancelOrder(e) {
    const no = e.currentTarget.dataset.no;
    const that = this;
    wx.showModal({
      title: '取消订单',
      content: '取消后订单里用掉的优惠券会退回',
      success(res) {
        if (!res.confirm) {
          return;
        }
        api.post('/api/wx/order/cancel', { orderNo: no }).then(() => {
          wx.showToast({ title: '已取消', icon: 'success' });
          that.loadOrders();
          that.loadCoupons();
        }).catch(() => {});
      }
    });
  },

  relogin() {
    getApp().login();
    wx.showToast({ title: '正在重新登录', icon: 'none' });
    setTimeout(() => {
      this.onShow();
    }, 1200);
  },

  goMember() {
    wx.switchTab({ url: '/pages/member/member' });
  },

  goIndex() {
    wx.switchTab({ url: '/pages/index/index' });
  },

  onPullDownRefresh() {
    this.onShow();
    wx.stopPullDownRefresh();
  }
});
