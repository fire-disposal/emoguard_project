// pages/assessment/detail/detail.js
const scaleApi = require('../../../api/scale');
const auth = require('../../../utils/auth');

Page({
  data: {
    scaleConfig: null,
    questions: [],
    selectedOptions: [],
    currentQuestionIndex: 0,
    startTime: 0,
    loading: true
  },

  onLoad(options) {
    const { id } = options;
    if (id) {
      this.loadScale(id);
    }
  },

  /**
   * 加载量表详情
   */
  loadScale(id) {
    this.setData({ loading: true });

    scaleApi.getConfig(id)
      .then((res) => {
        const selectedOptions = new Array(res.questions.length).fill(-1);
        
        this.setData({
          scaleConfig: res,
          questions: res.questions,
          selectedOptions,
          startTime: Date.now()
        });
      })
      .catch((error) => {
        console.error('加载量表详情失败:', error);
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
   * 选择答案
   */
  selectOption(e) {
    const { index } = e.currentTarget.dataset;
    const selectedOptions = [...this.data.selectedOptions];
    selectedOptions[this.data.currentQuestionIndex] = index;
    
    this.setData({ selectedOptions });
  },

  /**
   * 上一题
   */
  prevQuestion() {
    if (this.data.currentQuestionIndex > 0) {
      this.setData({
        currentQuestionIndex: this.data.currentQuestionIndex - 1
      });
    }
  },

  /**
   * 下一题
   */
  nextQuestion() {
    if (this.data.selectedOptions[this.data.currentQuestionIndex] === -1) {
      wx.showToast({
        title: '请选择答案',
        icon: 'none'
      });
      return;
    }

    if (this.data.currentQuestionIndex < this.data.questions.length - 1) {
      this.setData({
        currentQuestionIndex: this.data.currentQuestionIndex + 1
      });
    }
  },

  /**
   * 提交答题
   */
  submitAssessment() {
    // 检查是否全部答完
    if (this.data.selectedOptions.includes(-1)) {
      wx.showToast({
        title: '请完成所有题目',
        icon: 'none'
      });
      return;
    }

    const userInfo = auth.getUserInfo();
    if (!userInfo) return;

    wx.showLoading({ title: '提交中...' });

    const now = new Date();
    const startedAt = new Date(this.data.startTime).toISOString();
    const completedAt = now.toISOString();
    const durationMs = now.getTime() - this.data.startTime;

    scaleApi.createResult({
      user_id: userInfo.id,
      scale_config_id: this.data.scaleConfig.id,
      selected_options: this.data.selectedOptions,
      duration_ms: durationMs,
      started_at: startedAt,
      completed_at: completedAt
    })
    .then((res) => {
      wx.hideLoading();
      wx.redirectTo({
        url: `/pages/assessment/result/result?id=${res.id}`
      });
    })
    .catch((error) => {
      wx.hideLoading();
      console.error('提交测评失败:', error);
      wx.showToast({
        title: error.message || '提交失败',
        icon: 'none'
      });
    });
  }
});
