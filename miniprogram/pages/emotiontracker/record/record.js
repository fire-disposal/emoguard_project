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
    // 无需初始化用户，后端通过JWT识别
  },

  handleRadioChange(e) {
    const { name } = e.currentTarget.dataset;
    const value = Number(e.detail.value);
    this.setData({ [name]: value });
  },

  async handleSubmit() {
    // 无需检查userId，后端通过JWT识别用户
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
      // 直接传分数，不传user_id，后端通过JWT识别
      await emotionApi.upsertEmotionRecord({
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