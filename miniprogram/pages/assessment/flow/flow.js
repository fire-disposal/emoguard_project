// 认知评估流程引导页面
const scaleApi = require('../../../api/scale');
const auth = require('../../../utils/auth');

Page({
  data: {
    groupId: null,
    currentStep: null,
    flowStatus: 'loading', // loading, in_progress, completed
    nextScales: [],
    completedScales: [],
    comprehensiveAnalysis: null,
    finalConclusion: '',
    scaleNames: {
      'scd_q9': 'SCD-Q9 主观认知下降量表',
      'mmse': 'MMSE 简易精神状态检查',
      'moca': 'MoCA 蒙特利尔认知评估'
    }
  },

  onLoad(options) {
    const { groupId } = options;
    if (groupId) {
      // 继续已有评估
      this.setData({ groupId: parseInt(groupId) });
      this.loadAssessmentGroup();
    } else {
      // 创建新评估
      this.createNewAssessment();
    }
  },

  /**
   * 创建新评估流程
   */
  createNewAssessment() {
    const userInfo = auth.getUserInfo();
    if (!userInfo) return;

    wx.showLoading({ title: '初始化评估...' });

    scaleApi.createAssessmentGroup({
      user_id: userInfo.id,
      flow_type: 'cognitive_assessment'
    })
    .then((res) => {
      this.setData({ 
        groupId: res.id,
        flowStatus: 'in_progress'
      });
      return this.checkNextStep();
    })
    .catch((error) => {
      wx.hideLoading();
      console.error('创建评估失败:', error);
      wx.showToast({
        title: error.message || '创建失败',
        icon: 'none'
      });
    });
  },

  /**
   * 加载评估分组信息
   */
  loadAssessmentGroup() {
    scaleApi.getAssessmentGroup(this.data.groupId)
      .then((res) => {
        this.setData({
          currentStep: res.current_step,
          flowStatus: res.status,
          comprehensiveAnalysis: res.comprehensive_analysis,
          finalConclusion: res.final_conclusion
        });

        if (res.status === 'completed') {
          // 评估已完成
          this.setData({ flowStatus: 'completed' });
        } else {
          // 继续评估
          return this.checkNextStep();
        }
      })
      .catch((error) => {
        console.error('加载评估信息失败:', error);
        wx.showToast({
          title: error.message || '加载失败',
          icon: 'none'
        });
      });
  },

  /**
   * 检查下一步需要做什么
   */
  checkNextStep() {
    return scaleApi.getNextStep(this.data.groupId)
      .then((res) => {
        wx.hideLoading();
        
        if (res.completed) {
          // 流程已完成，重新加载获取综合分析
          return this.loadAssessmentGroup();
        } else {
          // 显示下一步需要完成的量表
          this.setData({
            nextScales: res.next_scales || [],
            currentStep: res.step,
            flowStatus: 'in_progress'
          });
          
          // 显示提示信息
          if (res.reason) {
            wx.showToast({
              title: res.reason,
              icon: 'none',
              duration: 3000
            });
          }
        }
      });
  },

  /**
   * 开始某个量表评估
   */
  startScale(e) {
    const { code } = e.currentTarget.dataset;
    
    // 根据code获取量表配置ID
    scaleApi.listConfigs({ status: 'active' })
      .then((configs) => {
        const scale = configs.find(c => c.code.toLowerCase() === code.toLowerCase());
        if (scale) {
          wx.navigateTo({
            url: `/pages/assessment/detail/detail?id=${scale.id}&groupId=${this.data.groupId}&flowMode=true`
          });
        } else {
          wx.showToast({
            title: '未找到该量表',
            icon: 'none'
          });
        }
      })
      .catch((error) => {
        console.error('加载量表配置失败:', error);
      });
  },

  /**
   * 查看综合报告
   */
  viewReport() {
    wx.navigateTo({
      url: `/pages/assessment/flow-result/flow-result?groupId=${this.data.groupId}`
    });
  },

  /**
   * 重新开始评估
   */
  restartAssessment() {
    wx.showModal({
      title: '确认重新开始',
      content: '将创建新的评估流程，当前评估不会被删除',
      success: (res) => {
        if (res.confirm) {
          this.createNewAssessment();
        }
      }
    });
  }
});
