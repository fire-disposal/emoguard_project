// 答题详情页面 - 支持单问卷、流程、智能测评模式
const scaleApi = require('../../../api/scale');
const authCenter = require('../../../utils/authCenter');

Page({
  data: {
    scaleConfig: null,
    questions: [],
    selectedOptions: [],
    currentQuestionIndex: 0,
    startTime: 0,
    loading: true,
    // 只保留单问卷模式
    mode: 'single',
    assessmentId: null
  },

  onLoad(options) {
    const { id } = options;
    
    if (!id) {
      wx.showToast({ title: '缺少参数', icon: 'none' });
      wx.navigateBack();
      return;
    }

    this.setData({
      // 强制单问卷模式
      mode: 'single',
      assessmentId: null
    });

    this.loadScale(id);
  },

  // 加载量表
  async loadScale(id) {
    try {
      // 加载量表配置
      const res = await scaleApi.getConfig(id);

      // 校验问题数据
      const questions = Array.isArray(res.questions) ? res.questions : [];
      const selectedOptions = new Array(questions.length).fill(-1);

      this.setData({
        scaleConfig: res,
        questions,
        selectedOptions,
        startTime: Date.now(),
        loading: false
      });
    } catch (error) {
      wx.showToast({ title: '加载失败', icon: 'none' });
      this.setData({ loading: false });
    }
  },

  // 选择答案
  selectOption(e) {
    const { index } = e.currentTarget.dataset;
    const { currentQuestionIndex, selectedOptions } = this.data;
    if (
      Array.isArray(selectedOptions) &&
      currentQuestionIndex >= 0 &&
      currentQuestionIndex < selectedOptions.length
    ) {
      const updatedOptions = [...selectedOptions];
      updatedOptions[currentQuestionIndex] = index;
      this.setData({ selectedOptions: updatedOptions });
    }
  },

  // 上一题
  prevQuestion() {
    const { currentQuestionIndex } = this.data;
    if (currentQuestionIndex > 0) {
      this.setData({
        currentQuestionIndex: currentQuestionIndex - 1
      });
    }
  },

  // 下一题
  nextQuestion() {
    const { questions, selectedOptions, currentQuestionIndex } = this.data;
    if (!Array.isArray(questions) || questions.length === 0) {
      wx.showToast({ title: '没有题目', icon: 'none' });
      return;
    }
    if (
      !Array.isArray(selectedOptions) ||
      selectedOptions[currentQuestionIndex] === -1
    ) {
      wx.showToast({ title: '请选择答案', icon: 'none' });
      return;
    }
    if (currentQuestionIndex < questions.length - 1) {
      this.setData({
        currentQuestionIndex: currentQuestionIndex + 1
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

    const userInfo = authCenter.getUserInfo();
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

      // 只保留单问卷模式
      let result;
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
    } catch (error) {
      wx.hideLoading();
      console.error('提交失败:', error);
      wx.showToast({ title: '提交失败', icon: 'none' });
    }
  }
});
