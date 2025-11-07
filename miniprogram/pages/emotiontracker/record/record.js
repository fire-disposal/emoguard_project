// miniprogram/pages/emotiontracker/record/record.js
const emotionApi = require('../../../api/emotiontracker');
const userApi = require('../../../api/user');

Page({
  data: {
    depression: null,
    anxiety: null,
    energy: null,
    sleep: null,
    submitting: false,
    userId: null,
    q1Options: [
      { text: '没有', value: 0 },
      { text: '轻微', value: 1 },
      { text: '中等', value: 2 },
      { text: '很严重', value: 3 }
    ],
    q2Options: [
      { text: '完全没有', value: 0 },
      { text: '非常严重', value: 10 }
    ],
    q3Options: [
      { text: '没有', value: 0 },
      { text: '有一点', value: 1 },
      { text: '明显', value: 2 },
      { text: '非常严重', value: 3 }
    ],
    q4Options: [
      { text: '非常好', value: 0 },
      { text: '比较好', value: 1 },
      { text: '一般', value: 2 },
      { text: '不太好', value: 3 },
      { text: '很差', value: 4 }
    ]
  },

  onLoad() {
    this.initUser();
  },

  async initUser() {
    try {
      const res = await userApi.getCurrentUser();
      this.setData({ userId: res.id });
    } catch (e) {
      wx.showToast({ title: '获取用户信息失败', icon: 'none' });
    }
  },

  handleRadioChange(e) {
    const { name } = e.currentTarget.dataset;
    const value = Number(e.detail.value);
    this.setData({ [name]: value });
  },

  async handleSubmit() {
    if (this.data.userId == null) {
      wx.showToast({ title: '用户未登录', icon: 'none' });
      return;
    }
    // 校验必填
    if (
      this.data.depression === null ||
      this.data.anxiety === null ||
      this.data.energy === null ||
      this.data.sleep === null
    ) {
      wx.showToast({ title: '请完成所有题目', icon: 'none' });
      return;
    }
    this.setData({ submitting: true });
    try {
      // 直接传分数，不传问题
      await emotionApi.upsertEmotionRecord({
        user_id: this.data.userId,
        depression: this.data.depression,
        anxiety: this.data.anxiety,
        energy: this.data.energy,
        sleep: this.data.sleep
      });
      wx.showToast({ title: '提交成功', icon: 'success' });
      wx.navigateBack();
    } catch (e) {
      wx.showToast({ title: '提交失败', icon: 'none' });
    } finally {
      this.setData({ submitting: false });
    }
  }
});