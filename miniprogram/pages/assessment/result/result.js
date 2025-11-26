// pages/assessment/result/result.js
const scaleApi = require('../../../api/scale');

Page({
  data: {
    result: null,
    loading: true,
    // 只保留单问卷结果
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
  async loadResult(id) {
    this.setData({ loading: true });
    try {
      const res = await scaleApi.getResult(id);
      // 结论字段适配（兼容后端返回的 conclusion 字段）
      let conclusion = '';
      if (res && typeof res.conclusion === 'string') {
        conclusion = res.conclusion;
      } else if (res && res.analysis && typeof res.analysis.interpretation === 'string') {
        conclusion = res.analysis.interpretation;
      }
      this.setData({ result: { ...res, conclusion } });
    } catch (error) {
      wx.showToast({
        title: (error && error.message) || '加载失败',
        icon: 'none'
      });
    } finally {
      this.setData({ loading: false });
    }
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
