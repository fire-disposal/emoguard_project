const emotionApi = require('../../../api/emotiontracker');
const noticeApi = require('../../../api/notice');
const subscribeUtil = require('../../../utils/subscribeUtil');

// --- 常量配置：将配置数据独立出来，使代码更清晰 ---
const COGNITIVE_QUESTIONS = [
  {
    key: 'depression',
    title: '情绪状态',
    question: '在过去的几个小时里，您是否觉得心情低落，或者对平常喜欢做的事情提不起兴趣？',
    type: 'radio',
    options: [
      { text: '没有', value: 0, desc: '完全没有这种感觉' },
      { text: '轻微', value: 1, desc: '偶尔有轻微的感觉' },
      { text: '中等', value: 2, desc: '有明显的感觉，影响日常生活' },
      { text: '很严重', value: 3, desc: '感觉非常强烈，严重影响生活' }
    ]
  },
  {
    key: 'anxiety',
    title: '焦虑水平',
    question: '在过去的几个小时里，您是否感到紧张、焦虑，或者坐立不安？',
    type: 'scale',
    min: 0,
    max: 10,
    minText: '完全没有',
    maxText: '非常严重',
    desc: '请根据您的实际感受选择0-10之间的数值'
  },
  {
    key: 'energy',
    title: '精力状态',
    question: '在过去的几个小时里，您是否觉得没有精力，容易感到疲劳？',
    type: 'radio',
    options: [
      { text: '没有', value: 0, desc: '精力充沛，没有疲劳感' },
      { text: '有一点', value: 1, desc: '偶尔感到轻微疲劳' },
      { text: '明显', value: 2, desc: '经常感到疲劳，影响活动' },
      { text: '非常严重', value: 3, desc: '极度疲劳，无法正常生活' }
    ]
  },
  {
    key: 'sleep',
    title: '睡眠质量',
    question: '请回顾今天（或昨晚），您的睡眠情况如何？',
    type: 'radio',
    options: [
      { text: '非常好', value: 0, desc: '睡眠质量极佳，醒来精神饱满' },
      { text: '比较好', value: 1, desc: '睡眠质量良好，基本恢复精力' },
      { text: '一般', value: 2, desc: '睡眠质量一般，略有不足' },
      { text: '不太好', value: 3, desc: '睡眠质量较差，影响精神状态' },
      { text: '很差', value: 4, desc: '睡眠质量极差，严重缺乏休息' }
    ]
  },
  // 主观情绪问题 - 整合到标准问题流程中
  {
    key: 'mainMood',
    title: '主观情绪',
    question: '您现在主要是什么感觉？',
    type: 'mood',
    options: [
      { value: 'happy', text: '快乐/愉快/高兴', icon: 'smile' },
      { value: 'calm', text: '平静/放松', icon: 'calm' },
      { value: 'sad', text: '难过/悲伤', icon: 'cry' },
      { value: 'anxious', text: '焦虑/担心', icon: 'nervous' },
      { value: 'angry', text: '易怒/烦躁', icon: 'angry' },
      { value: 'tired', text: '疲惫/无力', icon: 'tired' },
      { value: 'other', text: '其他', icon: 'other' }
    ]
  },
  {
    key: 'moodIntensity',
    title: '情绪强度',
    question: '您当前感受的强度如何？',
    type: 'radio',
    options: [
      { value: 1, text: '轻微', desc: '情绪感受较弱' },
      { value: 2, text: '中等', desc: '情绪感受适中' },
      { value: 3, text: '明显', desc: '情绪感受较强' }
    ]
  },
  {
    key: 'moodSupplementTags',
    title: '情绪原因',
    question: '导致此情绪的原因（可多选）',
    type: 'checkbox',
    options: [
      { value: 'body', text: '身体不适', desc: '' },
      { value: 'family', text: '家庭事务', desc: '' },
      { value: 'memory', text: '记忆困扰', desc: '' },
      { value: 'sleep', text: '睡眠不好', desc: '' },
      { value: 'work', text: '工作/学习压力', desc: '' },
      { value: 'other', text: '其他', desc: '' }
    ]
  },
  {
    key: 'moodSupplementText',
    title: '补充说明',
    question: '请简短写下导致此情绪的事情（可选）',
    type: 'text',
    placeholder: '可填写具体内容（可跳过）'
  }
];

Page({
  data: {
    // 测评数据 - 统一存储所有问题的答案
    depression: null,
    anxiety: null,
    energy: null,
    sleep: null,
    mainMood: null, // 主观情绪
    mainMoodOther: '', // 其他情绪文本
    moodIntensity: null, // 强度
    moodSupplementTags: [], // 补充标签 (数组)
    moodSupplementText: '', // 补充文本

    // 页面状态
    submitting: false,
    currentStep: 0,
    currentPeriod: '',

    // 问题配置
    questions: COGNITIVE_QUESTIONS, // 所有测评题目（已整合）

    // 总步数
    totalSteps: COGNITIVE_QUESTIONS.length
  },

  onLoad(options) {
    if (options && options.period) {
      this.setData({ currentPeriod: options.period });
    }

    const periodText = this.data.currentPeriod === 'morning' ? '早间' : this.data.currentPeriod === 'evening' ? '晚间' : '情绪';
    wx.setNavigationBarTitle({ title: `${periodText}测评` });
  },

  // --- 统一的数据绑定处理 ---

  // 处理单选变化
  handleRadioChange(e) {
    const { key } = e.currentTarget.dataset;
    this.setData({ [key]: Number(e.detail.value) });
  },

  // 处理滑块变化
  handleSliderChange(e) {
    const { key } = e.currentTarget.dataset;
    this.setData({ [key]: Number(e.detail.value) });
  },

  // 处理多选变化（复选框）
  handleCheckboxChange(e) {
    const { key } = e.currentTarget.dataset;
    const values = e.detail.value;
    this.setData({ [key]: values });
  },

  // 处理文本输入变化
  handleTextChange(e) {
    const { key } = e.currentTarget.dataset;
    this.setData({ [key]: e.detail.value });
  },

  // 处理情绪选择（特殊类型的单选）
  handleMoodSelect(e) {
    const { key, value } = e.currentTarget.dataset;
    const isOther = value === 'other';

    this.setData({
      [key]: value,
      // 如果不是'other'，清空其他情绪文本
      mainMoodOther: isOther ? this.data.mainMoodOther : '',
    });
  },

  // --- 步骤控制逻辑 ---

  // 下一步
  nextStep() {
    const { currentStep, questions } = this.data;

    // 校验当前步骤
    if (currentStep < questions.length) {
      const currentQuestion = questions[currentStep];
      let currentValue = this.data[currentQuestion.key];

      // 基础校验：检查是否已回答（文本类型除外）
      if (currentValue === null || currentValue === undefined || currentValue === '') {
        if (currentQuestion.type !== 'text') {
          wx.showToast({ title: '请完成当前题目', icon: 'none' });
          return;
        }
      }

      // 特殊校验：如果选择了"其他"情绪，需要填写具体文本
      if (currentQuestion.key === 'mainMood' && currentValue === 'other') {
        if (!this.data.mainMoodOther.trim()) {
          wx.showToast({ title: '请填写具体的情绪', icon: 'none' });
          return;
        }
      }
    }

    // 进入下一步或提交
    if (currentStep < questions.length - 1) {
      this.setData({ currentStep: currentStep + 1 });
    } else {
      this.handleSubmit(); // 最后一题，执行提交
    }
  },

  // 上一步
  prevStep() {
    if (this.data.currentStep > 0) {
      this.setData({ currentStep: this.data.currentStep - 1 });
    }
  },

  // 跳转到指定步骤 (保留，用于导航或底部进度条)
  goToStep(e) {
    const step = Number(e.currentTarget.dataset.step);
    if (step >= 0 && step < this.data.totalSteps) {
      this.setData({ currentStep: step });
    }
  },

  // --- 提交数据 (优化和新增) ---

  // 提交数据
  async handleSubmit() {
    this.setData({ submitting: true });

    try {
      // 构建统一的测评数据
      const recordData = {
        depression: this.data.depression,
        anxiety: this.data.anxiety,
        energy: this.data.energy,
        sleep: this.data.sleep,
        mainMood: this.data.mainMood,
        moodIntensity: this.data.moodIntensity,
        mainMoodOther: this.data.mainMood === 'other' ? this.data.mainMoodOther.trim() : '',
        moodSupplementTags: this.data.moodSupplementTags,
        moodSupplementText: this.data.moodSupplementText.trim(),
        period: this.data.currentPeriod || 'unknown',
        device_info: {
          platform: wx.getSystemInfoSync().platform,
          version: wx.getSystemInfoSync().version
        }
      };

      console.log('提交数据包:', recordData);

      const response = await emotionApi.upsertEmotionRecord(recordData);

      if (response && response.alert) {
        this.showSubmissionAlert(response.alert);
      }

      // 只显示完成页，不自动弹订阅，按钮由用户点击触发
      this.setData({ showSuccess: true, submitting: false });

      // 提交成功后，直接更新全局填写状态
      if (this.data.currentPeriod === 'morning') {
        getApp().globalData.morningFilled = true;
      } else if (this.data.currentPeriod === 'evening') {
        getApp().globalData.eveningFilled = true;
      }

    } catch (error) {
      console.error('提交失败:', error);
      let errorMessage = '提交失败，请重试';

      if (error.message && error.message.includes('网络')) {
        errorMessage = '网络连接失败，请检查网络';
      }

      this.setData({ submitting: false });
    }
  },

  // 订阅按钮事件
  handleSubscribe() {
    const templateId = '5er1e9forv8HdkH8X6mBYp0JbkFeo4kNPCRi0uKZEJI';
    subscribeUtil.subscribeMessage(templateId);
  },
  getProgressPercent() {
    return ((this.data.currentStep + 1) / this.data.totalSteps) * 100;
  }
});