const debounce = require('../../../utils/debounce.js');

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
  ...debounce,
  data: {
    depression: null,
    anxiety: null,
    energy: null,
    sleep: null,
    mainMood: null,
    mainMoodOther: '',
    moodIntensity: null,
    moodSupplementTags: [],
    moodSupplementText: '',
    submitting: false,
    currentStep: 0,
    currentPeriod: '',
    questions: COGNITIVE_QUESTIONS,
    totalSteps: COGNITIVE_QUESTIONS.length
  },

  onLoad(options) {
    if (options && options.period) {
      this.setData({ currentPeriod: options.period });
    }
    const periodText = this.data.currentPeriod === 'morning' ? '早间' : this.data.currentPeriod === 'evening' ? '晚间' : '情绪';
    wx.setNavigationBarTitle({ title: `${periodText}训练测试` });
  },

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
      mainMoodOther: isOther ? this.data.mainMoodOther : '',
    });
  },

  // 下一步
  nextStep() {
    const { currentStep, questions } = this.data;
    if (currentStep < questions.length) {
      const currentQuestion = questions[currentStep];
      let currentValue = this.data[currentQuestion.key];
      if (currentValue === null || currentValue === undefined || currentValue === '') {
        if (currentQuestion.type !== 'text') {
          wx.showToast({ title: '请完成当前题目', icon: 'none' });
          return;
        }
      }
      if (currentQuestion.key === 'mainMood' && currentValue === 'other') {
        if (!this.data.mainMoodOther.trim()) {
          wx.showToast({ title: '请填写具体的情绪', icon: 'none' });
          return;
        }
      }
    }
    if (currentStep < questions.length - 1) {
      this.setData({ currentStep: currentStep + 1 });
    } else {
      this.setData({ showSuccess: true, submitting: false });
    }
  },

  // 上一步
  prevStep() {
    if (this.data.currentStep > 0) {
      this.setData({ currentStep: this.data.currentStep - 1 });
    }
  },

  // 跳转到指定步骤
  goToStep(e) {
    const step = Number(e.currentTarget.dataset.step);
    if (step >= 0 && step < this.data.totalSteps) {
      this.setData({ currentStep: step });
    }
  },

  // 订阅按钮事件（训练测试页面无订阅，仅提示）
  handleSubscribe() {
    wx.showToast({ title: '本页面仅供练习，无订阅功能', icon: 'none' });
  },

  getProgressPercent() {
    return ((this.data.currentStep + 1) / this.data.totalSteps) * 100;
  },

  // tap事件绑定：模拟训练结果展示
  handleSubmit() {
    const { questions } = this.data;
    let answers = {};
    let missing = [];

    // 收集答案并校验
    questions.forEach(q => {
      let val = this.data[q.key];
      // 主观情绪other校验
      if (q.key === 'mainMood' && val === 'other' && !this.data.mainMoodOther.trim()) {
        missing.push('请填写具体的主观情绪');
      }
      // 必填校验（除补充说明外）
      if (q.type !== 'text' && (val === null || val === undefined || val === '' || (Array.isArray(val) && val.length === 0))) {
        missing.push(q.title);
      }
      answers[q.key] = val;
    });

    if (missing.length > 0) {
      wx.showModal({
        title: '未完成',
        content: '请完成以下题目：' + missing.join('、'),
        showCancel: false
      });
      return;
    }

    // 生成模拟训练结果
    let scoreSummary = {
      depression: answers.depression,
      anxiety: answers.anxiety,
      energy: answers.energy,
      sleep: answers.sleep
    };
    let totalScore = 0;
    Object.keys(scoreSummary).forEach(k => {
      totalScore += Number(scoreSummary[k] || 0);
    });

    // 情绪标签
    let moodLabel = '';
    switch (answers.mainMood) {
      case 'happy': moodLabel = '积极'; break;
      case 'calm': moodLabel = '平稳'; break;
      case 'sad': moodLabel = '低落'; break;
      case 'anxious': moodLabel = '焦虑'; break;
      case 'angry': moodLabel = '易怒'; break;
      case 'tired': moodLabel = '疲惫'; break;
      case 'other': moodLabel = this.data.mainMoodOther || '其他'; break;
      default: moodLabel = '未选择';
    }

    // 构造结果数据
    const resultData = {
      scoreSummary,
      totalScore,
      moodLabel,
      moodIntensity: answers.moodIntensity,
      moodSupplementTags: answers.moodSupplementTags,
      moodSupplementText: answers.moodSupplementText
    };

    // 展示结果（前端模拟，不提交）
    this.setData({
      showResult: true,
      resultData
    });

    wx.showModal({
      title: '模拟训练结果',
      content: `总分：${totalScore}\n主观情绪：${moodLabel}\n强度：${answers.moodIntensity}\n补充：${answers.moodSupplementText || '无'}`,
      showCancel: false
    });
  }
});