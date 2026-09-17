// 统一请求封装
//
// 后端所有接口都是 POST + JSON，返回 {code, message, response}，
// 而且 **code === 1 才是成功**（不是 0，也不是 HTTP 状态码）。
// 业务错误也带 HTTP 200 返回，所以只看网络层判断不出来。

const app = getApp();

function baseUrl() {
  return (app && app.globalData && app.globalData.apiBase) || 'http://127.0.0.1:8000';
}

function userId() {
  // 先看内存，再看本地缓存：小程序冷启动时 app.onLaunch 的登录请求可能还没回来，
  // 页面 onLoad 就已经发请求了，这时用缓存里的 userId 顶一下。
  if (app && app.globalData && app.globalData.userId) {
    return app.globalData.userId;
  }
  return wx.getStorageSync('userId') || null;
}

/**
 * @param {string} path  完整路径，如 '/api/wx/order/list'
 * @param {object} data  请求体
 * @param {object} opt   { needLogin: 默认 true, silent: 默认 false }
 */
function post(path, data, opt) {
  const options = opt || {};
  const needLogin = options.needLogin !== false;
  const body = Object.assign({}, data || {});
  if (needLogin) {
    const uid = userId();
    if (uid) {
      body.userId = uid;
    }
  }
  return new Promise((resolve, reject) => {
    wx.request({
      url: baseUrl() + path,
      method: 'POST',
      data: body,
      header: { 'Content-Type': 'application/json' },
      success(res) {
        const r = res.data || {};
        if (r.code === 1) {
          resolve(r.response);
          return;
        }
        if (!options.silent) {
          wx.showToast({ title: r.message || '请求失败', icon: 'none' });
        }
        reject(r);
      },
      fail(err) {
        if (!options.silent) {
          wx.showToast({ title: '连不上后端，检查是否已启动', icon: 'none' });
        }
        reject(err);
      }
    });
  });
}

/** 格式化时间：后端返回的是 ISO 字符串，截成 年-月-日 或 年-月-日 时:分 */
function fmtTime(s, withTime) {
  if (!s) {
    return '';
  }
  const t = String(s).replace('T', ' ');
  return withTime ? t.substring(0, 16) : t.substring(0, 10);
}

/** 金额统一保留 2 位 */
function fmtMoney(v) {
  const n = Number(v || 0);
  return n.toFixed(2);
}

/** 订单状态文案 */
function orderStatusText(status) {
  if (status === 0) {
    return '待支付';
  }
  if (status === 1) {
    return '已支付';
  }
  if (status === 2) {
    return '已取消';
  }
  return '未知';
}

/** 券状态文案 */
function couponStatusText(status) {
  if (status === 0) {
    return '未使用';
  }
  if (status === 1) {
    return '已使用';
  }
  if (status === 2) {
    return '已过期';
  }
  return '';
}

module.exports = { post, fmtTime, fmtMoney, orderStatusText, couponStatusText, baseUrl };
