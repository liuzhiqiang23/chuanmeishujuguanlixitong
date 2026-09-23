// 分类：按影片标签浏览（标签体系是项目现成的 t_tag / t_video_tag，不另建分类表）
const api = require('../../utils/api.js');

Page({
  data: {
    categories: [],
    activeTagId: 0,
    activeName: '',
    videos: [],
    loading: true,
    pageIndex: 1,
    hasNext: false,
    status: '',
    isAdmin: false
  },

  onLoad(options) {
    // 首页分类宫格带 tagId 进来：加载完分类后直接选中该分类
    if (options && options.tagId) {
      this._pendingTag = {
        id: Number(options.tagId),
        name: decodeURIComponent(options.tagName || '')
      };
    }
    this.loadCategories();
  },

  /** isAdmin 是登录后才写进 globalData 的，每次显示都重读一次 */
  onShow() {
    const app = getApp();
    this.setData({ isAdmin: (app.globalData && app.globalData.isAdmin) === true });
  },

  loadCategories() {
    // 只取关联影片 >= 20 部的标签，最多 24 个：9830 个标签里长尾太多，全列出来没法用
    api.post('/api/wx/category/list', { minCount: 20, limit: 24 }, { needLogin: false }).then((list) => {
      const cats = list || [];
      this.setData({ categories: cats });
      if (cats.length > 0) {
        const p = this._pendingTag;
        this._pendingTag = null;
        const hit = p && cats.find((c) => c.tagId === p.id);
        if (hit) {
          this.pick(hit.tagId, hit.tagName);
        } else if (p && p.id) {
          // 带的分类不在前 24 里也照选：列表页照常能拉到该分类的影片
          this.pick(p.id, p.name || '');
        } else {
          this.pick(cats[0].tagId, cats[0].tagName);
        }
      } else {
        this.setData({ loading: false, status: '暂无分类' });
      }
    }).catch(() => {
      this.setData({ loading: false, status: '分类加载失败' });
    });
  },

  onTag(e) {
    this.pick(e.currentTarget.dataset.id, e.currentTarget.dataset.name);
  },

  pick(tagId, tagName) {
    if (this.data.activeTagId === tagId && this.data.videos.length > 0) {
      return;
    }
    this.setData({ activeTagId: tagId, activeName: tagName, videos: [], hasNext: false });
    this.loadVideos(1);
  },

  loadVideos(page) {
    this.setData({ loading: true, status: '加载中...' });
    api.post('/api/wx/category/videos', {
      tagId: this.data.activeTagId,
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
        loading: false,
        status: '共 ' + res.total + ' 部'
      });
      api.cachePosters(this, 'videos', prevLen, list.length);
    }).catch(() => {
      this.setData({ loading: false, status: '加载失败' });
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

  /** 管理员删片：后端每次都会再校验一次 role，前端只是不给普通用户显示按钮 */
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
          that.setData({ videos: left, status: '共 ' + left.length + ' 部' });
        }).catch(() => {});
      }
    });
  }
});
