// pages/reports/detail/detail.js
const reportApi = require('../../../api/report');

Page({
  data: {
    report: null,
    loading: true
  },

  onLoad(options) {
    const { id } = options;
    if (id) {
      this.loadReport(id);
    }
  },

  /**
   * 加载报告详情
   */
  loadReport(id) {
    this.setData({ loading: true });

    reportApi.getReport(id)
      .then((res) => {
        this.setData({ report: res });
      })
      .catch((error) => {
        console.error('加载报告详情失败:', error);
        wx.showToast({
          title: error.message || '加载失败',
          icon: 'none'
        });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  }
});
