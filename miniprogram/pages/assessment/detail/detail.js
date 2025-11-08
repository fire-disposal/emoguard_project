// 答题详情页面 - 支持单问卷、流程、智能测评模式
const scaleApi = require('../../../api/scale');
const auth = require('../../../utils/auth');

Page({
  data: {
    scaleConfig: null,
    questions: [],
    selectedOptions: [],
    currentQuestionIndex: 0,
    startTime: 0,
    loading: true,
    mode: 'single', // 'single', 'smart'
    assessmentId: null
  },

  onLoad(options) {
    const { id, groupId, assessmentId, mode } = options;
    
    if (!id) {
      wx.showToast({ title: '缺少参数', icon: 'none' });
      wx.navigateBack();
      return;
    }

    this.setData({
      mode: mode || 'single',
      assessmentId: assessmentId ? parseInt(assessmentId) : null
    });
    
    this.loadScale(id);
  },

  // 加载量表
  async loadScale(id) {
    try {
      console.log('开始加载量表，ID:', id);
      const res = await scaleApi.getConfig(id);
      
      console.log('量表配置原始数据:', res);
      console.log('问题数据:', res.questions);
      console.log('问题数量:', res.questions ? res.questions.length : 0);
      
      // 确保问题数据存在且为数组
      const questions = res.questions || [];
      const selectedOptions = new Array(questions.length).fill(-1);

      
      this.setData({
        scaleConfig: res,
        questions: questions,
        selectedOptions: selectedOptions,
        startTime: Date.now(),
        loading: false
      });
      
      console.log('页面数据设置完成，当前问题索引:', 0);
    } catch (error) {
      console.error('加载失败:', error);
      wx.showToast({ title: '加载失败', icon: 'none' });
      this.setData({ loading: false });
    }
  },

  // 选择答案
  selectOption(e) {
    const { index } = e.currentTarget.dataset;
    const selectedOptions = [...this.data.selectedOptions];
    
    // 确保当前题目索引有效
    if (this.data.currentQuestionIndex >= 0 && this.data.currentQuestionIndex < selectedOptions.length) {
      selectedOptions[this.data.currentQuestionIndex] = index;
      this.setData({ selectedOptions });
    }
  },

  // 上一题
  prevQuestion() {
    if (this.data.currentQuestionIndex > 0) {
      this.setData({
        currentQuestionIndex: this.data.currentQuestionIndex - 1
      });
    }
  },

  // 下一题
  nextQuestion() {
    // 检查是否有题目
    if (this.data.questions.length === 0) {
      wx.showToast({ title: '没有题目', icon: 'none' });
      return;
    }
    
    // 检查是否已选择答案
    if (this.data.selectedOptions[this.data.currentQuestionIndex] === -1) {
      wx.showToast({ title: '请选择答案', icon: 'none' });
      return;
    }

    if (this.data.currentQuestionIndex < this.data.questions.length - 1) {
      this.setData({
        currentQuestionIndex: this.data.currentQuestionIndex + 1
      });
    }
  },

  // 提交
  async submitAssessment() {
    if (this.data.selectedOptions.includes(-1)) {
      wx.showToast({ title: '请完成所有题目', icon: 'none' });
      return;
    }

    if (!this.data.scaleConfig || !this.data.scaleConfig.id) {
      wx.showToast({ title: '量表ID异常', icon: 'none' });
      return;
    }

    const userInfo = auth.getUserInfo();
    if (!userInfo) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '提交中...' });

    try {
      const now = new Date();
      const data = {
        scale_config_id: this.data.scaleConfig.id,
        selected_options: this.data.selectedOptions,
        duration_ms: now.getTime() - this.data.startTime,
        started_at: new Date(this.data.startTime).toISOString(),
        completed_at: now.toISOString()
      };

      let result;
      
      if (this.data.mode === 'smart' && this.data.assessmentId) {
        // 智能测评模式
        result = await scaleApi.submitSmartAnswer(
          this.data.assessmentId,
          this.data.scaleConfig.id,
          data
        );
        
        wx.hideLoading();
        
        if (result.success) {
          if (result.completed) {
            // 测评完成，跳转到结果页面
            wx.redirectTo({
              url: `/pages/assessment/smart-result/smart-result?assessmentId=${this.data.assessmentId}`
            });
          } else if (result.next_scale) {
            // 还有下一个量表，继续答题
            // 兼容后端返回 id/config_id 字段
            const nextScaleId = result.next_scale.id || result.next_scale.config_id;
            this.setData({
              currentQuestionIndex: 0,
              selectedOptions: new Array(result.next_scale.questions.length).fill(-1),
              startTime: Date.now(),
              scaleConfig: { ...result.next_scale, id: nextScaleId },
              questions: result.next_scale.questions
            }, () => {
              // 回调中校验新量表ID，确保健壮
              if (!this.data.scaleConfig || !this.data.scaleConfig.id) {
                wx.showToast({ title: '量表ID异常', icon: 'none' });
              }
              // 打印页面数据设置完成
              console.log('页面数据设置完成，当前问题索引:', this.data.currentQuestionIndex);
            });
            wx.showToast({ title: '继续下一个量表', icon: 'success' });
          }
        } else {
          throw new Error(result.error || '提交失败');
        }
      } else {
        // 单问卷模式
        result = await scaleApi.createResult({
          ...data,
          user_id: userInfo.id
        });
        
        wx.hideLoading();
        
        if (result.success) {
          // 跳转到结果页面
          wx.redirectTo({
            url: `/pages/assessment/result/result?id=${result.id}`
          });
        } else {
          throw new Error(result.error || '提交失败');
        }
      }
    } catch (error) {
      wx.hideLoading();
      console.error('提交失败:', error);
      wx.showToast({ title: '提交失败', icon: 'none' });
    }
  }
});
