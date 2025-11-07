// 认知评估流程综合报告页面
const scaleApi = require('../../../api/scale');

Page({
  data: {
    groupId: null,
    group: null,
    comprehensiveAnalysis: null,
    loading: true
  },

  onLoad(options) {
    const { groupId } = options;
    if (groupId) {
      this.setData({ groupId: parseInt(groupId) });
      this.loadReport();
    }
  },

  /**
   * 加载综合报告
   */
  loadReport() {
    scaleApi.getAssessmentGroup(this.data.groupId)
      .then((res) => {
        this.setData({
          group: res,
          comprehensiveAnalysis: res.comprehensive_analysis,
          loading: false
        });
      })
      .catch((error) => {
        console.error('加载报告失败:', error);
        wx.showToast({
          title: error.message || '加载失败',
          icon: 'none'
        });
        this.setData({ loading: false });
      });
  },

  /**
   * 返回首页
   */
  backToHome() {
    wx.switchTab({
      url: '/pages/index/index'
    });
  }
});
