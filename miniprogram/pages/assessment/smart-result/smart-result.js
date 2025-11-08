// 智能测评结果页面 - 后端主导，前端极简
const scaleApi = require('../../../api/scale');
const auth = require('../../../utils/auth');

Page({
  data: {
    assessmentId: null,
    assessmentResult: null,
    loading: true,
    errorMessage: ''
  },

  async onLoad(options) {
    const { assessmentId } = options;
    
    if (!assessmentId) {
      this.handleError('缺少测评ID参数', false);
      return;
    }

    this.setData({ assessmentId: parseInt(assessmentId) });
    
    try {
      await this.loadAssessmentResult();
    } catch (error) {
      console.error('页面加载失败:', error);
      this.handleError(error.message || '页面加载失败');
    }
  },

  // 加载测评结果
  async loadAssessmentResult() {
    try {
      this.setData({ loading: true, errorMessage: '' });
      
      // 获取测评结果
      const result = await scaleApi.getSmartAssessmentResult(this.data.assessmentId);
      
      if (!result) {throw new Error('测评结果不存在');
      }
      
      // 验证用户权限
      const userInfo = auth.getUserInfo();
      if (!userInfo || result.user_id !== userInfo.id) {
        throw new Error('无权查看此测评结果');
      }
      
      // 检查测评状态
      if (result.status !== 'completed') {
        // 如果测评未完成，跳转到测评页面
        wx.showModal({
          title: '提示',
          content: '该测评尚未完成，是否继续？',
          confirmText: '继续',
          cancelText: '返回',
          success: (res) => {
            if (res.confirm) {
              wx.redirectTo({
                url: `/pages/assessment/smart/smart`
              });
            } else {
              wx.navigateBack();
            }
          }
        });
        return;
      }
      
      this.setData({
        assessmentResult: result,
        loading: false
      });
      
    } catch (error) {
      console.error('加载测评结果失败:', error);
      this.handleError(error.message || '加载失败');
    } finally {
      this.setData({ loading: false });
    }
  },

  // 查看单项结果详情
  viewResultDetail(e) {
    const { resultId } = e.currentTarget.dataset;
    
    if (resultId) {
      wx.navigateTo({
        url: `/pages/assessment/result/result?id=${resultId}`
      });
    }
  },
  
  // 格式化时间显示
  formatDateTime(dateString) {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return dateString;
    }
  },
  
  // 获取量表名称
  getScaleName(scaleScore) {
    return scaleScore.scale_name || '未知量表';
  },

  // 重新测评
  reevaluate() {
    wx.showModal({
      title: '确认重新测评',
      content: '将创建新的智能测评，当前测评结果将保留',
      confirmText: '确定',
      cancelText: '取消',
      success: async (res) => {
        if (res.confirm) {
          try {
            // 跳转到智能测评页面
            wx.redirectTo({
              url: '/pages/assessment/smart/smart'
            });
          } catch (error) {
            console.error('重新测评失败:', error);
            wx.showToast({
              title: '操作失败',
              icon: 'none'
            });
          }
        }
      }
    });
  },

  // 返回首页
  backToHome() {
    wx.switchTab({
      url: '/pages/index/index'
    });
  },

  // 分享报告
  onShareAppMessage() {
    if (!this.data.assessmentResult) {
      return {
        title: '智能测评报告',
        path: '/pages/index/index'
      };
    }
    
    // 格式化分享标题
    const startedAt = this.data.assessmentResult.started_at;
    const finalResult = this.data.assessmentResult.final_result || {};
    const riskLevel = finalResult.risk_level || '未知';
    const conclusion = finalResult.conclusion || '测评完成';
    
    return {
      title: `智能测评报告 - ${riskLevel} - ${conclusion}`,
      path: `/pages/assessment/smart-result/smart-result?assessmentId=${this.data.assessmentId}`,
      imageUrl: '/images/share-report.jpg'
    };
  },

  // 处理错误
  handleError(message, canRetry = true) {
    console.error('处理错误:', message);
    
    this.setData({
      errorMessage: message,
      canRetry: canRetry,
      loading: false
    });
    
    if (!canRetry) {
      wx.showModal({
        title: '错误',
        content: message,
        showCancel: false,
        success: () => {
          wx.navigateBack();
        }
      });
    }
  },

  // 重新加载
  async reload() {
    try {
      this.setData({ 
        loading: true, 
        errorMessage: '',
        canRetry: true
      });
      
      await this.loadAssessmentResult();
    } catch (error) {
      console.error('重新加载失败:', error);
      this.handleError('重新加载失败');
    }
  }
});