// 智能测评页面 - 后端主导，前端极简
const scaleApi = require('../../../api/scale');
const auth = require('../../../utils/auth');

Page({
  data: {
    assessmentId: null,
    currentScale: null,
    totalScales: 0,
    completedScales: 0,
    loading: false,
    errorMessage: ''
  },

  async onLoad(options) {
    const userInfo = auth.getUserInfo();
    if (!userInfo) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
      return;
    }

    // 开始智能测评（无需传user_id，后端通过JWT识别）
    await this.startSmartAssessment();
  },

  // 开始智能测评（无需传user_id，后端通过JWT识别）
  async startSmartAssessment() {
    this.setData({ loading: true, errorMessage: '' });
    
    try {
      const result = await scaleApi.startSmartAssessment();
      
      if (result.success) {
        this.setData({
          assessmentId: result.assessment_id,
          currentScale: result.next_scale,
          totalScales: result.total_scales,
          completedScales: 0
        });
        
        // 如果有量表，直接进入答题
        if (result.next_scale) {
          this.navigateToScale(result.next_scale.config_id);
        }
      } else {
        throw new Error(result.error || '开始测评失败');
      }
    } catch (error) {
      console.error('开始智能测评失败:', error);
      this.setData({
        errorMessage: error.message || '开始测评失败',
        loading: false
      });
    }
  },

  // 跳转到量表答题页面
  navigateToScale(configId) {
    wx.navigateTo({
      url: `/pages/assessment/detail/detail?id=${configId}&assessmentId=${this.data.assessmentId}&mode=smart`
    });
  },

  // 处理答题完成返回
  async onShow() {
    if (this.data.assessmentId && this.data.currentScale) {
      // 检查是否还有下一个量表
      await this.checkAssessmentStatus();
    }
  },

  // 检查测评状态
  async checkAssessmentStatus() {
    try {
      const result = await scaleApi.getSmartAssessmentResult(this.data.assessmentId);
      
      if (result && result.status === 'completed') {
        // 测评完成，跳转到结果页面
        wx.redirectTo({
          url: `/pages/assessment/smart-result/smart-result?assessmentId=${this.data.assessmentId}`
        });
      }
    } catch (error) {
      console.error('检查测评状态失败:', error);
    }
  },

  // 返回首页
  goHome() {
    wx.switchTab({ url: '/pages/index/index' });
  }
});