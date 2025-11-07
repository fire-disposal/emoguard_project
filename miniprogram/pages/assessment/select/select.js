// pages/assessment/select/select.js
const scaleApi = require('../../../api/scale');

Page({
  data: {
    scales: [],
    loading: true,
    // 显示流程入口
    showFlowEntry: true
  },

  onLoad() {
    this.loadScales();
  },

  /**
   * 加载量表列表
   */
  loadScales() {
    this.setData({ loading: true });

    scaleApi.listConfigs({ status: 'active' })
      .then((res) => {
        this.setData({
          scales: res || []
        });
      })
      .catch((error) => {
        console.error('加载量表列表失败:', error);
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
   * 开始测评
   */
  startAssessment(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/assessment/detail/detail?id=${id}`
    });
  },

  /**
   * 开始认知评估流程
   */
  startCognitiveFlow() {
    wx.navigateTo({
      url: '/pages/assessment/flow/flow'
    });
  }
});
