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
  // 等 app 探测出可用的后端地址再发，否则冷启动时的第一条请求会打到还没确定的地址上。
  // 但最多只等 1.5 秒：某条候选连不通时（真机上的 127.0.0.1、域名还没解析时），
  // TCP 会一直挂到超时才失败，不能让整页请求陪着它一起卡住。超时就先用当前地址发。
  const ready = (app && app.ready) ? app.ready() : Promise.resolve();
  const bounded = Promise.race([
    ready,
    new Promise((resolve) => setTimeout(resolve, 1500))
  ]);
  return bounded.then(() => new Promise((resolve, reject) => {
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
          // 真机上没地方看 console，把「请求到哪个地址」「微信给的原始错误」
          // 「三条候选各自的探测结果」一次弹出来 —— 排查连不上时这几条就够了。
          const diag = (app && app.globalData && app.globalData.probeDiag) || '(探测还没结束)';
          wx.showModal({
            title: '连不上后端',
            content: '请求地址：\n' + baseUrl() + path +
                     '\n\n微信错误：\n' + ((err && err.errMsg) || String(err)) +
                     '\n\n候选地址探测：\n' + diag,
            showCancel: false
          });
        }
        reject(err);
      }
    });
  }));
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

/** 海报的网络地址。真机上不能直接给 <image> 用，要先过 cachePosters */
function posterUrl(videoId) {
  return baseUrl() + '/posters/' + videoId + '.jpg?v=2';
}

/** 和后台 OrderServiceImpl.videoPrice 保持一致：>=8.5 → 12 元，>=7.5 → 9 元，其余 6 元 */
function videoPrice(vote) {
  const v = Number(vote || 0);
  if (v >= 8.5) {
    return '12.00';
  }
  if (v >= 7.5) {
    return '9.00';
  }
  return '6.00';
}

/**
 * 把列表里的网络海报下到本地临时文件，再替换列表项的 posterSrc。
 *
 * 真机上 <image> 直接引 http 图片会被小程序拦掉（接口能通、图片一张都不出），
 * 而本地文件不受域名限制。wx.downloadFile 受「不校验合法域名」开关保护，预览版可用。
 * 微信限制 downloadFile 并发 10 个，这里用 6 个并发的小队列。
 *
 * @param {object} page   页面实例（用它的 data / setData）
 * @param {string} key    列表在 data 里的字段名，如 'videos'
 * @param {number} offset 从第几项开始
 * @param {number} count  处理多少项
 */
function cachePosters(page, key, offset, count) {
  let i = 0;
  const CONCURRENCY = 6;
  const next = () => {
    if (i >= count) {
      return;
    }
    const idx = offset + i;
    i++;
    const list = page.data[key] || [];
    const item = list[idx];
    if (!item || !item.posterSrc || item.posterSrc.indexOf('http') !== 0) {
      next();
      return;
    }
    wx.downloadFile({
      url: item.posterSrc,
      success: (r) => {
        if (r.statusCode === 200 && r.tempFilePath) {
          const patch = {};
          patch[key + '[' + idx + '].posterSrc'] = r.tempFilePath;
          page.setData(patch);
        }
      },
      fail: () => {},
      complete: () => next()
    });
  };
  for (let k = 0; k < CONCURRENCY; k++) {
    next();
  }
}

module.exports = {
  post,
  fmtTime,
  fmtMoney,
  orderStatusText,
  couponStatusText,
  baseUrl,
  posterUrl,
  videoPrice,
  cachePosters
};
