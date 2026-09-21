// 搜索：按片名 / 原名模糊查，历史记录存本地缓存
const api = require('../../utils/api.js');

const HISTORY_KEY = 'searchHistory';
const MAX_HISTORY = 10;

Page({
  data: {
    keyword: '',
    history: [],
    videos: [],
    searched: false,
    loading: false,
    total: 0,
    pageIndex: 1,
    hasNext: false,
    isAdmin: false
  },

  onLoad() {
    this.setData({ history: wx.getStorageSync(HISTORY_KEY) || [] });
  },

  /** isAdmin 是登录后才写进 globalData 的，每次显示都重读一次 */
  onShow() {
    const app = getApp();
    this.setData({ isAdmin: (app.globalData && app.globalData.isAdmin) === true });
  },

  onInput(e) {
    this.setData({ keyword: e.detail.value });
  },

  onSearch() {
    const kw = (this.data.keyword || '').trim();
    if (!kw) {
      wx.showToast({ title: '请输入片名', icon: 'none' });
      return;
    }
    this.saveHistory(kw);
    this.loadVideos(1);
  },

  /** 点历史标签直接搜 */
  onTagTap(e) {
    const kw = e.currentTarget.dataset.kw;
    this.setData({ keyword: kw });
    this.saveHistory(kw);
    this.loadVideos(1);
  },

  saveHistory(kw) {
    const list = (this.data.history || []).filter((x) => x !== kw);
    list.unshift(kw);
    const trimmed = list.slice(0, MAX_HISTORY);
    this.setData({ history: trimmed });
    wx.setStorageSync(HISTORY_KEY, trimmed);
  },

  clearHistory() {
    this.setData({ history: [] });
    wx.removeStorageSync(HISTORY_KEY);
  },

  loadVideos(page) {
    this.setData({ loading: true });
    api.post('/api/wx/search/videos', {
      keyword: this.data.keyword.trim(),
      pageIndex: page,
      pageSize: 10
    }, { needLogin: false }).then((res) => {
      const list = (res.list || []).map((v) => ({
        videoId: v.videoId,
        videoName: v.videoName,
        voteAverage: v.voteAverage,
        popularity: v.popularity,
        price: api.videoPrice(v.voteAverage),
        posterSrc: api.posterUrl(v.videoId)
      }));
      const prevLen = page === 1 ? 0 : this.data.videos.length;
      this.setData({
        videos: page === 1 ? list : this.data.videos.concat(list),
        pageIndex: res.pageIndex,
        hasNext: res.pageIndex * res.pageSize < res.total,
        total: res.total,
        searched: true,
        loading: false
      });
      api.cachePosters(this, 'videos', prevLen, list.length);
    }).catch(() => {
      this.setData({ loading: false, searched: true, videos: [], total: 0 });
    });
  },

  onReachBottom() {
    if (this.data.hasNext && !this.data.loading) {
      this.loadVideos(this.data.pageIndex + 1);
    }
  },

  goDetail(e) {
    wx.navigateTo({ url: '/pages/detail/detail?videoId=' + e.currentTarget.dataset.id });
  },

  /** 点海报看大图。用 catchtap 拦下，不会连带触发整行的进详情 */
  previewPoster(e) {
    const src = e.currentTarget.dataset.src;
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

  /**
   * 管理员删片：后端会校验 role == 3，前端只是不给普通用户显示按钮。
   * 删完把这条从列表里摘掉，不重新请求。
   */
  removeVideo(e) {
    const id = e.currentTarget.dataset.id;
    const name = e.currentTarget.dataset.name || '';
    const that = this;
    wx.showModal({
      title: '删除影片',
      content: '确定删除《' + name + '》？会同时清掉它的标签关联，不可恢复。',
      confirmColor: '#E55A5A',
      success(res) {
        if (!res.confirm) {
          return;
        }
        api.post('/api/wx/admin/video/delete', { videoId: id }).then(() => {
          wx.showToast({ title: '已删除', icon: 'success' });
          const left = (that.data.videos || []).filter((v) => v.videoId !== id);
          that.setData({ videos: left, total: Math.max(0, that.data.total - 1) });
        }).catch(() => {});
      }
    });
  }
});
