// pages/assessment/result/result.js
const scaleApi = require('../../../api/scale');

Page({
  data: {
    result: null,
    loading: true
  },

  onLoad(options) {
    const { id } = options;
    if (id) {
      this.loadResult(id);
    }
  },

  /**
   * 加载测评结果
   */
  loadResult(id) {
    this.setData({ loading: true });

    scaleApi.getResult(id)
      .then((res) => {
        this.setData({ result: res });
      })
      .catch((error) => {
        console.error('加载测评结果失败:', error);
        wx.showToast({
          title: error.message || '加载失败',
          icon: 'none'
        });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  /**
   * 返回首页
   */
  goHome() {
    wx.switchTab({ url: '/pages/index/index' });
  },

  /**
   * 查看报告
   */
  goToReports() {
    wx.navigateTo({ url: '/pages/reports/list/list' });
  }
});
