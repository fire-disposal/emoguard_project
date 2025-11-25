// 测评选择页面 - 支持单问卷和智能测评模式
const scaleApi = require('../../../api/scale');
const authCenter = require('../../../utils/authCenter');

Page({
  data: {
    scales: [],
    loading: true
  },

  async onLoad() {
    await this.loadScales();
  },

  // 加载量表列表
  async loadScales() {
    try {
      this.setData({ loading: true });
      const res = await scaleApi.listConfigs({ status: 'active' });
      
      if (res && res.length > 0) {
        this.setData({ scales: res });
      } else {
        wx.showModal({
          title: '无可用问卷',
          content: '当前没有可用的问卷，请联系管理员',
          showCancel: false
        });
      }
    } catch (error) {
      console.error('加载量表失败:', error);
      wx.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      this.setData({ loading: false });
    }
  },

  // 开始智能测评
  async startSmartAssessment() {
    try {
      const userInfo = authCenter.getUserInfo();
      if (!userInfo) {
        wx.showToast({ title: '请先登录', icon: 'none' });
        return;
      }

      wx.showLoading({ title: '初始化中...' });
      
      // 跳转到新的流程测评页面
      wx.hideLoading();
      wx.navigateTo({
        url: '/pages/assessment/flow/flow'
      });
      
    } catch (error) {
      wx.hideLoading();
      console.error('开始智能测评失败:', error);
      wx.showToast({ title: '操作失败', icon: 'none' });
    }
  },

  // 单问卷模式 - 直接开始单个量表
  async startSingleScale(e) {
    const { id, name } = e.currentTarget.dataset;
    
    wx.showModal({
      title: '确认开始',
      content: `即将开始${name}评估，是否继续？`,
      confirmText: '开始',
      cancelText: '取消',
      success: async (res) => {
        if (res.confirm) {
          wx.navigateTo({
            url: `/pages/assessment/detail/detail?id=${id}&mode=single`
          });
        }
      }
    });
  },

  // 返回首页
  goHome() {
    wx.switchTab({ url: '/pages/index/index' });
  }
});
