// pages/mood/journal/journal.js
const journalApi = require('../../../api/journal');
const auth = require('../../../utils/auth');

// 题目配置 - 根据TODO.MD要求
const JOURNAL_QUESTIONS = [
  {
    key: 'mainMood',
    title: '主观情绪',
    question: '您现在主要是什么感觉？',
    type: 'mood',
    options: [
      { value: 'happy', text: '愉快/高兴', emoji: '😄' },
      { value: 'calm', text: '平静/放松', emoji: '😌' },
      { value: 'sad', text: '难过/悲伤', emoji: '😢' },
      { value: 'anxious', text: '焦虑/担心', emoji: '😰' },
      { value: 'angry', text: '易怒/烦躁', emoji: '😡' },
      { value: 'tired', text: '疲惫/无力', emoji: '😫' },
      { value: 'other', text: '其他', emoji: '🤔' }
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
    question: '请简短写下导致此情绪的事情',
    type: 'text',
    placeholder: '可填写具体内容'
  }
];

Page({
  data: {
    // 答案数据
    mainMood: null,
    mainMoodOther: '',
    moodIntensity: null,
    moodSupplementTags: [],
    moodSupplementText: '',
    
    // 页面状态
    submitting: false,
    journals: [],
    loading: false,
    
    // 题目配置
    questions: JOURNAL_QUESTIONS,
    
    // 历史记录相关
    showHistory: true
  },

  onShow() {
    if (!auth.isLogined()) {
      auth.navigateToLogin();
      return;
    }
    this.loadJournals();
  },

  onLoad() {
    this.loadJournals();
  },

  /**
   * 加载历史记录
   */
  loadJournals() {
    const userInfo = auth.getUserInfo();
    if (!userInfo) return;

    this.setData({ loading: true });

    journalApi.listJournals({
      user_id: userInfo.id,
      page: 1,
      page_size: 10
    })
    .then((res) => {
      const journals = (res || []).map(item => {
        const moodName = item.mood_name || item.label || '未知';
        return {
          ...item,
          emoji: this.getEmojiByMoodName(moodName),
          mood_name: moodName,
          mood_score: item.mood_score || item.score || 5,
          text: item.text || '',
          created_at: item.created_at || new Date().toISOString()
        };
      });
      
      this.setData({
        journals: journals
      });
    })
    .catch((error) => {
      console.error('加载历史记录失败:', error);
      this.setData({
        journals: []
      });
    })
    .finally(() => {
      this.setData({ loading: false });
    });
  },

  /**
   * 根据心情类型文本获取表情
   */
  getEmojiByMoodName(moodName) {
    const moodMap = {
      '快乐': '😄',
      '开心': '😊',
      '平静': '😌',
      '一般': '😐',
      '难过': '😔',
      '悲伤': '😢',
      '焦虑': '😰',
      '担心': '😟',
      '烦躁': '😠',
      '易怒': '😡',
      '疲惫': '😫',
      '无力': '😩'
    };
    
    for (let key in moodMap) {
      if (moodName.includes(key)) {
        return moodMap[key];
      }
    }
    return '😐';
  },

  // --- 数据绑定处理 ---
  
  // 处理单选变化
  handleRadioChange(e) {
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

  // 获取选项选中状态
  getOptionSelected(questionIndex, optionValue) {
    const question = this.data.questions[questionIndex];
    const currentValue = this.data[question.key];
    return currentValue === optionValue;
  },

  // 获取复选框选中状态
  getCheckboxSelected(questionIndex, optionValue) {
    const question = this.data.questions[questionIndex];
    const currentValues = this.data[question.key] || [];
    return currentValues.includes(optionValue);
  },

  // 获取当前值
  getCurrentValue(questionIndex) {
    const question = this.data.questions[questionIndex];
    return this.data[question.key];
  },

  /**
   * 提交心情记录
   */
  submitMoodRecord() {
    // 验证必填项
    if (!this.data.mainMood) {
      wx.showToast({
        title: '请选择主观情绪',
        icon: 'none'
      });
      return;
    }

    if (!this.data.moodIntensity) {
      wx.showToast({
        title: '请选择情绪强度',
        icon: 'none'
      });
      return;
    }

    if (this.data.submitting) return;

    this.setData({ submitting: true });
    wx.showLoading({ title: '记录中...' });

    // 构建提交数据
    const submitData = {
      mainMood: this.data.mainMood,
      moodIntensity: this.data.moodIntensity,
      mainMoodOther: this.data.mainMoodOther,
      moodSupplementTags: this.data.moodSupplementTags,
      moodSupplementText: this.data.moodSupplementText.trim()
    };

    journalApi.createJournal(submitData)
    .then(() => {
      wx.showToast({
        title: '心情记录成功',
        icon: 'success'
      });

      // 清空输入
      this.setData({
        mainMood: null,
        mainMoodOther: '',
        moodIntensity: null,
        moodSupplementTags: [],
        moodSupplementText: ''
      });

      // 刷新列表
      this.loadJournals();
    })
    .catch((error) => {
      console.error('提交心情记录失败:', error);
      wx.showToast({
        title: error.message || '记录失败，请重试',
        icon: 'none'
      });
    })
    .finally(() => {
      wx.hideLoading();
      this.setData({ submitting: false });
    });
  },

  /**
   * 获取情绪文本
   */
  getMoodText(moodValue, otherText) {
    const moodMap = {
      'happy': '快乐/愉快',
      'calm': '平静/放松',
      'sad': '难过/悲伤',
      'anxious': '焦虑/担心',
      'angry': '易怒/烦躁',
      'tired': '疲惫/无力',
      'other': otherText || '其他情绪'
    };
    return moodMap[moodValue] || '未知情绪';
  },

  /**
   * 构建补充说明文本
   */
  buildSupplementText() {
    let text = '';
    
    // 添加标签信息
    if (this.data.moodSupplementTags.length > 0) {
      const tagMap = {
        'body': '身体不适',
        'family': '家庭事务',
        'memory': '记忆困扰',
        'sleep': '睡眠不好',
        'work': '工作/学习压力',
        'other': '其他原因'
      };
      const tagTexts = this.data.moodSupplementTags.map(tag => tagMap[tag] || tag);
      text += '原因：' + tagTexts.join('、') + '。';
    }
    
    // 添加详细说明
    if (this.data.moodSupplementText.trim()) {
      if (text) text += ' ';
      text += this.data.moodSupplementText.trim();
    }
    
    return text || '暂无详细说明';
  },

  /**
   * 切换历史记录显示
   */
  toggleHistory() {
    this.setData({
      showHistory: !this.data.showHistory
    });
  },

  /**
   * 格式化时间
   */
  formatTime(dateString) {
    const date = new Date(dateString);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${month}月${day}日 ${hours}:${minutes}`;
  }
});
