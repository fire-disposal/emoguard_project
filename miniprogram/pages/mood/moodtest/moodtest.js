const emotionApi = require('../../../api/emotiontracker');
const subscribeUtil = require('../../../utils/subscribeUtil');
const { moodtestQ } = require('../../../utils/scales');

Page({
  data: {
    // 存储所有问题的最终答案
    answers: {
      depression: null,
      anxiety: null,
      energy: null,
      sleep: null,
      mainMood: null,
      mainMoodOther: '',
      moodIntensity: null,
      moodSupplementTags: [],
      moodSupplementText: '',
    },
    
    // --- 当前题目专用的渲染数据 (核心修改) ---
    currentValue: null,      // 当前题目的值（用于滑块、文本、单选对比）
    currentOptions: [],      // 当前题目的选项（已计算好 checked 状态，用于多选/单选）
    mainMoodOther: '',       // 专门暂存"其他情绪"的文本
    // ------------------------------------

    submitting: false,
    currentStep: 0,
    currentPeriod: '',
    isMockMode: false,
    showSuccess: false,
    questions: moodtestQ,
    totalSteps: moodtestQ.length
  },

  onLoad(options) {
    if (options && options.period) {
      this.setData({ currentPeriod: options.period });
    }
    if (options && options.mock === 'true') {
      this.setData({ isMockMode: true });
    }

    const periodText = this.data.currentPeriod === 'morning' ? '早间' : this.data.currentPeriod === 'evening' ? '晚间' : '情绪';
    const modeText = this.data.isMockMode ? '训练测试' : '测评';
    wx.setNavigationBarTitle({ title: `${periodText}${modeText}` });

    // 初始化第一题视图
    this.updateCurrentStepData(0);
  },

  // --- 核心：更新当前步骤的视图数据 ---
  // 每次切换步骤，都手动计算一次 checked 状态，而不是在 WXML 里算
  updateCurrentStepData(stepIndex) {
    const question = this.data.questions[stepIndex];
    const key = question.key;
    // 获取之前的回答，如果没有则是 null/默认值
    let val = this.data.answers[key];

    // 处理滑块的默认值
    if (question.type === 'scale' && (val === null || val === undefined)) {
      val = question.min; 
    }

    // 处理选项的选中状态 (针对 Radio 和 Checkbox)
    let processedOptions = [];
    if (question.options) {
      processedOptions = question.options.map(opt => {
        let isChecked = false;
        if (question.type === 'checkbox') {
          // 多选：判断值是否在数组中
          isChecked = Array.isArray(val) && val.map(String).includes(String(opt.value));
        } else {
          // 单选/情绪：直接相等比较
          isChecked = String(val) === String(opt.value);
        }
        return {
          ...opt,
          checked: isChecked // 在 JS 里算好，WXML 直接用
        };
      });
    }

    // 处理 "其他情绪" 的文本回显
    const otherText = key === 'mainMood' ? (this.data.answers.mainMoodOther || '') : '';

    this.setData({
      currentStep: stepIndex,
      currentValue: val, 
      currentOptions: processedOptions,
      mainMoodOther: otherText
    });
  },

  // --- 交互处理 ---

  // 通用单选/滑块变化
  handleCommonChange(e) {
    const { key } = e.currentTarget.dataset;
    const val = Number(e.detail.value);
    
    // 1. 更新总答案
    this.setData({ [`answers.${key}`]: val });
    // 2. 更新当前视图状态 (为了立刻看到选中效果)
    this.updateCurrentStepData(this.data.currentStep);
  },

  // 多选变化
  handleCheckboxChange(e) {
    const { key } = e.currentTarget.dataset;
    const values = e.detail.value; // 数组
    
    this.setData({ [`answers.${key}`]: values });
    this.updateCurrentStepData(this.data.currentStep);
  },

  // 文本输入
  handleTextChange(e) {
    const { key } = e.currentTarget.dataset;
    const val = e.detail.value;
    
    // 文本输入不需要重算 options，直接更新值即可，防抖动
    this.setData({ 
      [`answers.${key}`]: val,
      currentValue: val 
    });
  },

  // 情绪选择 (特殊单选)
  handleMoodSelect(e) {
    const { key, value } = e.currentTarget.dataset;
    const isOther = value === 'other';

    // 更新答案
    this.setData({
      [`answers.${key}`]: value,
      // 如果切走了other，清空补充说明；如果是other，保持原样
      [`answers.mainMoodOther`]: isOther ? this.data.answers.mainMoodOther : ''
    }, () => {
        // 更新视图高亮
        this.updateCurrentStepData(this.data.currentStep);
    });
  },

  // 情绪-其他文本输入
  handleMoodOtherInput(e) {
      const val = e.detail.value;
      this.setData({
          [`answers.mainMoodOther`]: val,
          mainMoodOther: val
      });
  },

  // --- 导航逻辑 ---

  nextStep() {
    const { currentStep, questions, answers } = this.data;

    // 校验
    if (currentStep < questions.length) {
      const currentQ = questions[currentStep];
      const val = answers[currentQ.key];

      // 1. 基础空值校验
      if (val === null || val === undefined || val === '') {
        if (currentQ.type !== 'text') { // 文本题若非必填可放行，这里假设非文本题必填
          wx.showToast({ title: '请完成当前题目', icon: 'none' });
          return;
        }
      }

      // 2. 多选校验空数组
      if (currentQ.type === 'checkbox' && (!val || val.length === 0)) {
         wx.showToast({ title: '请至少选择一项', icon: 'none' });
         return;
      }

      // 3. "其他"情绪的特殊校验
      if (currentQ.key === 'mainMood' && val === 'other') {
        if (!answers.mainMoodOther || !answers.mainMoodOther.trim()) {
          wx.showToast({ title: '请填写具体的情绪', icon: 'none' });
          return;
        }
      }
    }

    if (currentStep < questions.length - 1) {
      // 切换到下一步，必须调用 updateCurrentStepData
      this.updateCurrentStepData(currentStep + 1);
    } else {
      this.handleSubmit();
    }
  },

  prevStep() {
    if (this.data.currentStep > 0) {
      // 切换到上一步，回显数据
      this.updateCurrentStepData(this.data.currentStep - 1);
    }
  },

  // --- 提交 ---
  async handleSubmit() {
    this.setData({ submitting: true });
    const { answers, currentPeriod, isMockMode } = this.data;

    try {
      const recordData = {
        ...answers,
        mainMoodOther: answers.mainMood === 'other' ? answers.mainMoodOther.trim() : '',
        moodSupplementText: answers.moodSupplementText ? answers.moodSupplementText.trim() : '',
        period: currentPeriod || 'unknown',
      };

      console.log('提交数据:', recordData);
      
      // 模拟模式下不发送请求，直接视为成功
      if (isMockMode) {
        console.log('模拟模式：跳过实际提交');
      } else {
        const response = await emotionApi.upsertEmotionRecord(recordData);
      }

      this.setData({ showSuccess: true, submitting: false });

      // 模拟模式下不影响本地的填写状态
      if (!isMockMode) {
        if (currentPeriod === 'morning') getApp().globalData.morningFilled = true;
        if (currentPeriod === 'evening') getApp().globalData.eveningFilled = true;
      }

    } catch (error) {
      console.error('提交失败:', error);
      wx.showToast({ title: '提交失败，请重试', icon: 'none' });
      this.setData({ submitting: false });
    }
  },

  handleSubscribe() {
    const templateId = '5er1e9forv8HdkH8X6mBYp0JbkFeo4kNPCRi0uKZEJI';
    subscribeUtil.subscribeMessage(templateId);
  }
});