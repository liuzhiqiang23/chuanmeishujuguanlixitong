// AI 客服小影：私有知识（FAQ + 影片库）检索 + GLM 生成，后端 /api/wx/chat。
// 页面只管对话展示；知识检索和模型调用全在后端，小程序里不出现任何 key。
const api = require('../../utils/api');

let seq = 0;

Page({
  data: {
    messages: [],       // [{id, role: 'ai'|'me', text, meta}]
    input: '',
    thinking: false,
    suggestions: [],
    anchor: '',
  },

  onInput(e) {
    this.setData({ input: e.detail.value });
  },

  onSuggest(e) {
    this.setData({ input: e.currentTarget.dataset.q });
    this.onSend();
  },

  onSend() {
    const q = (this.data.input || '').trim();
    if (!q || this.data.thinking) return;
    seq += 1;
    const meMsg = { id: seq, role: 'me', text: q };
    this.setData({
      messages: this.data.messages.concat([meMsg]),
      input: '',
      thinking: true,
      suggestions: [],
      anchor: 'thinking',
    });

    api.post('/api/wx/chat', { question: q }, { silent: true })
      .then((res) => {
        seq += 1;
        const meta = [];
        if (res && res.source === 'glm') meta.push('AI 生成');
        if (res && res.refs && res.refs.length) meta.push('引用资料 ' + res.refs.length + ' 条');
        if (res && res.costMs != null) meta.push((res.costMs / 1000).toFixed(1) + 's');
        this.setData({
          messages: this.data.messages.concat([{
            id: seq,
            role: 'ai',
            text: (res && res.answer) || '小影走神了，再问一次试试',
            meta: meta.join(' · '),
          }]),
          thinking: false,
          suggestions: (res && res.suggestions) || [],
          anchor: 'm' + seq,
        });
      })
      .catch(() => {
        seq += 1;
        this.setData({
          messages: this.data.messages.concat([{
            id: seq,
            role: 'ai',
            text: '网络不太顺畅，小影没收到消息，请稍后再试。',
          }]),
          thinking: false,
          anchor: 'm' + seq,
        });
      });
  },
});
