// movie-system 小程序端 —— 全局逻辑
//
// 【后端地址】四个候选，启动时并发探测，谁通用谁（按优先级取第一个通的）：
//   1) 127.0.0.1          开发者工具模拟器（跑在本机，最快）
//   2) 局域网 IP          手机连上电脑所在的热点/路由器时走这条，最快
//   3) your-domain.example.com 正式地址，服务器上跑着后端；域名备案+证书就绪后，
//                         同学手机上的体验版只有这一条能用（白名单只认 HTTPS 域名）
//   4) 服务器 IP          域名没解析时的过渡通道，IP 进不了合法域名白名单，
//                         只有开发版/预览版（勾了「不校验合法域名」）能用
// 热点重启会换网段，地址 2 可能过期——改了这里重新上传一次即可。
const API_BASES = [
  'http://127.0.0.1:8000',
  'http://192.168.1.100:8000',
  'https://your-domain.example.com',
  'http://YOUR_SERVER_IP'
];

/** 探活：这个接口是公开的，不需要登录，能拿到响应就说明这条地址通。
 *  超时压得短一点：连不上的那条（真机上 127.0.0.1、域名解析不了时）TCP 会挂到
 *  超时才失败，后面的地址全被它拖着。2.5 秒足够本机/服务器返回，慢由 api.js 那边兜底。
 *  返回 {ok, err} 而不是布尔值：err 是微信给的原始 errMsg，出错时要显示给用户看。 */
function probe(base) {
  return new Promise(function (resolve) {
    wx.request({
      url: base + '/api/wx/member/plans',
      method: 'POST',
      data: {},
      header: { 'Content-Type': 'application/json' },
      timeout: 2500,
      success: function () { resolve({ base: base, ok: true, err: '' }); },
      fail: function (e) { resolve({ base: base, ok: false, err: (e && e.errMsg) || 'unknown' }); }
    });
  });
}

/** 并发探测所有候选，取优先级最高且通的；都不通就退回最后一条，保证报错信息一致。
 *  每个地址的结果都记进 globalData.probeDiag，出错时弹出来给用户看。 */
function pickBase(app) {
  return Promise.all(API_BASES.map(probe)).then(function (rs) {
    if (app && app.globalData) {
      app.globalData.probeDiag = rs.map(function (r) {
        return (r.ok ? '[通]   ' : '[不通] ') + r.base + (r.err ? '  ' + r.err : '');
      }).join('\n');
    }
    for (var i = 0; i < rs.length; i++) {
      if (rs[i].ok) {
        return rs[i].base;
      }
    }
    return API_BASES[API_BASES.length - 1];
  });
}

App({
  globalData: {
    // 先按最后一个初始化：探测出结果前的第一条请求也发得出去，随后被覆盖
    apiBase: API_BASES[API_BASES.length - 1],
    userId: null,
    token: null,
    nickName: '',
    isMember: false,
    memberExpireTime: null,
    shareFrom: '',
    isAdmin: false,
    // 三条候选地址的探测结果，出错时弹给用户看，方便远程定位
    probeDiag: ''
  },

  onLaunch(options) {
    // 从好友的分享卡片进来时，路径上带着 shareFrom（分享者的 userId）。
    // 但要等自己登录拿到 userId 才能去领券，所以在 login 成功回调里处理。
    this.globalData.shareFrom = (options && options.query && options.query.shareFrom) || '';
    const that = this;
    // 页面 onLoad/onShow 会在 onLaunch 之后立刻发请求，所以让 api.js 等这个 ready，
    // 否则第一条请求会打到还没探测完的地址上。这里只等地址，不等登录。
    this._baseReady = pickBase(this).then(function (base) {
      that.globalData.apiBase = base;
      console.log('后端地址：', base);
      return base;
    });
    this._baseReady.then(function () {
      that.login();
    });
  },

  /** api.js 在发请求前 await 这个，保证用的是探测出来的地址 */
  ready() {
    return this._baseReady || Promise.resolve();
  },

  /** 微信一键登录：wx.login 拿 code → 换 openid → 后端免注册建号 */
  login() {
    const that = this;
    return new Promise(function (resolve) {
      wx.login({
        success(res) {
          // 开发者工具用游客 appid 时 code 可能是空串，后端会落到 demo_openid_default，
          // 一样能跑通整套流程，方便先看效果。
          wx.request({
            url: that.globalData.apiBase + '/api/wx/login',
            method: 'POST',
            data: { code: res.code || '', nickName: that.globalData.nickName || '' },
            header: { 'Content-Type': 'application/json' },
            success(r) {
              const body = r.data || {};
              if (body.code === 1 && body.response) {
                const d = body.response;
                that.globalData.userId = d.userId;
                that.globalData.token = d.token;
                that.globalData.nickName = d.nickName;
                that.globalData.isMember = d.isMember;
                that.globalData.memberExpireTime = d.memberExpireTime;
                that.globalData.isAdmin = d.isAdmin === true;
                wx.setStorageSync('userId', d.userId);
                console.log('登录成功 userId=', d.userId, ' 会员=', d.isMember);
                that.claimShareCoupon();
              } else {
                console.warn('登录失败：', body.message);
              }
              resolve();
            },
            fail(err) {
              console.error('登录请求失败，后端起了吗？', err);
              resolve();
            }
          });
        },
        fail() {
          resolve();
        }
      });
    });
  },

  /**
   * 我是被好友分享进来的：拿 shareFrom 去后端领券，后端会同时给分享者也发一张。
   * 同一对好友只发一次，重复进不会重复领（后端有唯一索引兜底）。
   */
  claimShareCoupon() {
    const from = Number(this.globalData.shareFrom || 0);
    const me = Number(this.globalData.userId || 0);
    if (!from || !me || from === me) {
      return;
    }
    wx.request({
      url: this.globalData.apiBase + '/api/wx/coupon/share/receive',
      method: 'POST',
      data: { userId: me, sharerId: from },
      header: { 'Content-Type': 'application/json' },
      success(res) {
        const body = res.data || {};
        if (body.code === 1) {
          const t = body.response || {};
          wx.showToast({ title: '已领到「' + (t.title || '优惠券') + '」', icon: 'none', duration: 2500 });
        } else if (body.message && body.message.indexOf('已经领过') < 0) {
          console.warn('分享领券失败：', body.message);
        }
      },
      fail() {}
    });
  }
});
