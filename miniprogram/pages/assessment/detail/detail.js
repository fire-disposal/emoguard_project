// 网络量表专用测评详情页
const scaleApi = require('../../../api/scale');
const authCenter = require('../../../utils/authCenter');

Page({
  data: {
    scaleCode: '', // 量表唯一标识
    scaleInfo: null, // 量表元信息
    questions: [],
    selectedOptions: [],
    currentQuestionIndex: 0,
    startTime: 0,
    loading: true,
    submitting: false
  },

  async onLoad(options) {
    const { id } = options;
    if (!id) {
      wx.showToast({ title: '缺少参数', icon: 'none' });
      wx.navigateBack();
      return;
    }
    this.setData({
      scaleCode: id,
      startTime: Date.now(),
      loading: true
    });
    await this.loadScaleInfo();
    await this.loadQuestions();
  },

  // 加载量表元信息
  async loadScaleInfo() {
    try {
      const info = await scaleApi.getScale(this.data.scaleCode);
      this.setData({ scaleInfo: info });
    } catch (error) {
      wx.showToast({ title: '量表信息加载失败', icon: 'none' });
    }
  },

  // 加载题目
  async loadQuestions() {
    try {
      const questions = await scaleApi.getQuestions(this.data.scaleCode);
      const formatted = Array.isArray(questions)
        ? questions.map(q => ({
            id: q.id || '',
            text: q.text || '',
            options: Array.isArray(q.options) ? q.options : [],
            type: q.type || 'single',
            required: typeof q.required === 'boolean' ? q.required : true,
            order: typeof q.order === 'number' ? q.order : 0
          }))
        : [];
      this.setData({
        questions: formatted,
        selectedOptions: new Array(formatted.length).fill(-1),
        currentQuestionIndex: 0,
        loading: false
      });
    } catch (error) {
      wx.showToast({ title: '题目加载失败', icon: 'none' });
      this.setData({ loading: false });
    }
  },

  // 选择答案
  selectOption(e) {
    const { currentQuestionIndex, selectedOptions } = this.data;
    const value = Number(e.detail.value); // radio-group change事件返回选中的value
    if (
      Array.isArray(selectedOptions) &&
      currentQuestionIndex >= 0 &&
      currentQuestionIndex < selectedOptions.length
    ) {
      const updatedOptions = [...selectedOptions];
      updatedOptions[currentQuestionIndex] = value;
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
    const userInfo = authCenter.getUserInfo();
    if (!userInfo) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }
    this.setData({ submitting: true });
    wx.showLoading({ title: '提交中...' });
    try {
      const now = new Date();
      const payload = {
        scale_code: this.data.scaleCode,
        selected_options: this.data.selectedOptions,
        started_at: new Date(this.data.startTime).toISOString(),
        completed_at: now.toISOString()
      };
      const result = await scaleApi.createResult(payload);
      wx.hideLoading();
      this.setData({ submitting: false });
      if (result.success) {
        wx.redirectTo({
          url: `/pages/assessment/result/result?id=${result.id}`
        });
      } else {
        throw new Error(result.error || '提交失败');
      }
    } catch (error) {
      wx.hideLoading();
      this.setData({ submitting: false });
      wx.showToast({ title: '提交失败', icon: 'none' });
    }
  }
});
