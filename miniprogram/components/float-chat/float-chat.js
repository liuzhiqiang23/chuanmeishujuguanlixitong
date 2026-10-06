// 悬浮客服球：只做一件事——跳转 AI 客服小影聊天页
Component({
  methods: {
    go() {
      wx.navigateTo({ url: '/pages/chat/chat' });
    },
  },
});
