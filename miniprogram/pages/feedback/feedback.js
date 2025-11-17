// pages/feedback/feedback.js
const request = require('../../utils/request');

Page({
  data: {
    rating: 0,
    content: '',
    submitting: false
  },

  onStarTap(e) {
    const rating = e.currentTarget.dataset.rating;
    this.setData({ rating });
  },

  onContentInput(e) {
    this.setData({ content: e.detail.value });
  },

  onSubmit() {
    if (this.data.rating === 0) {
      wx.showToast({
        title: '请选择评分',
        icon: 'none'
      });
      return;
    }

    if (this.data.submitting) return;

    this.setData({ submitting: true });
    wx.showLoading({ title: '提交中...' });

    request.post('/api/feedback/feedback', {
      rating: this.data.rating,
      content: this.data.content
    })
    .then(res => {
      wx.hideLoading();
      wx.showToast({
        title: '提交成功',
        icon: 'success',
        duration: 2000
      });
      
      setTimeout(() => {
        wx.navigateBack();
      }, 2000);
    })
    .catch(error => {
      wx.hideLoading();
      wx.showToast({
        title: error.message || '提交失败',
        icon: 'none'
      });
    })
    .finally(() => {
      this.setData({ submitting: false });
    });
  }
});