// movie-system 小程序端 —— 全局逻辑
//
// 【后端地址】开发者工具跑在本机，用 127.0.0.1 就行；
// 真机预览要改成电脑的局域网 IP（ipconfig 看 WLAN 的 IPv4），
// 并且真机默认不允许 http，要么在开发者工具里勾「不校验合法域名」，
// 要么给后端配 HTTPS 域名（上线必须走这一步）。
const API_BASE = 'http://127.0.0.1:8000';

App({
  globalData: {
    apiBase: API_BASE,
    userId: null,
    token: null,
    nickName: '',
    isMember: false,
    memberExpireTime: null
  },

  onLaunch() {
    this.login();
  },

  /** 微信一键登录：wx.login 拿 code → 换 openid → 后端免注册建号 */
  login() {
    const that = this;
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
              wx.setStorageSync('userId', d.userId);
              console.log('登录成功 userId=', d.userId, ' 会员=', d.isMember);
            } else {
              console.warn('登录失败：', body.message);
            }
          },
          fail(err) {
            console.error('登录请求失败，后端起了吗？', err);
          }
        });
      }
    });
  }
});
