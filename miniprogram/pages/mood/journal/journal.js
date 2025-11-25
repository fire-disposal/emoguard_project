// pages/mood/journal/journal.js
const journalApi = require('../../../api/journal');
const authCenter = require('../../../utils/authCenter');

// 题目配置 - 根据TODO.MD要求
const JOURNAL_QUESTIONS = [
  {
    key: 'mainMood',
    title: '主观情绪',
    question: '您现在主要是什么感觉？',
    type: 'mood',
    options: [
      { value: '愉快/高兴', text: '愉快/高兴', emoji: '😄' },
      { value: '平静/放松', text: '平静/放松', emoji: '😌' },
      { value: '难过/悲伤', text: '难过/悲伤', emoji: '😢' },
      { value: '焦虑/担心', text: '焦虑/担心', emoji: '😰' },
      { value: '易怒/烦躁', text: '易怒/烦躁', emoji: '😡' },
      { value: '疲惫/无力', text: '疲惫/无力', emoji: '😫' },
      { value: '其他', text: '其他', emoji: '🤔' }
    ]
  },
  {
    key: 'moodIntensity',
    title: '情绪强度',
    question: '您当前感受的强度如何？',
    type: 'slider',
    min: 1,
    max: 10,
    step: 1
  },
  {
    key: 'moodSupplementTags',
    title: '情绪原因',
    question: '导致此情绪的原因（可多选）',
    type: 'checkbox',
    options: [
      { value: '身体不适', text: '身体不适', desc: '' },
      { value: '家庭事务', text: '家庭事务', desc: '' },
      { value: '记忆困扰', text: '记忆困扰', desc: '' },
      { value: '睡眠不好', text: '睡眠不好', desc: '' },
      { value: '工作/学习压力', text: '工作/学习压力', desc: '' },
      { value: '其他', text: '其他', desc: '' }
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
    mainMood: "",
    mainMoodOther: "",
    moodIntensity: 0,
    moodSupplementTags: {},
    moodSupplementText: "",
    supplementMoodList: [],
    
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
    if (!authCenter.logined) {
      authCenter.logout();
      wx.reLaunch({ url: '/pages/login/login' });
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
    const userInfo = authCenter.getUserInfo();
    if (!userInfo) return;

    this.setData({ loading: true });

    journalApi.listJournals({
      user_id: userInfo.id,
      page: 1,
      page_size: 10
    })
    .then((res) => {
      const journals = (res || []).map(item => {
        const moodName = item.mainMood || item.label || '未知';
        return {
            ...item,
            emoji: this.getEmojiByMoodName(moodName),
            mainMood: moodName,
            mainMoodText: this.getMoodText(item.mainMood, item.mainMoodOther),
            mood_score: item.mood_score || item.score || item.moodIntensity || 5,
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
  // 直接用中文匹配 emoji
  getEmojiByMoodName(moodName) {
    const moodMap = {
      '愉快/高兴': '😄',
      '平静/放松': '😌',
      '难过/悲伤': '😢',
      '焦虑/担心': '😰',
      '易怒/烦躁': '😡',
      '疲惫/无力': '😫',
      '其他': '🤔'
    };
    return moodMap[moodName] || '🤔';
  },

  // 滑动题事件处理
  handleSliderChange(e) {
    const { key } = e.currentTarget.dataset;
    this.setData({ [key]: Number(e.detail.value) });
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
    const isOther = value === '其他';

    this.setData({
      [key]: value,
      mainMoodOther: isOther ? this.data.mainMoodOther : '',
    });
  },

  // 处理补充情绪多选
  handleSupplementMoodSelect(e) {
    const value = e.currentTarget.dataset.value;
    let list = this.data.supplementMoodList || [];
    if (list.includes(value)) {
      list = list.filter(v => v !== value);
    } else {
      list = [...list, value];
    }
    this.setData({ supplementMoodList: list });
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
    // 精简校验逻辑，适配后端参数
    if (!this.data.mainMood || typeof this.data.mainMood !== "string" || this.data.mainMood.trim() === "") {
      wx.showToast({ title: '请选择主观情绪', icon: 'none' });
      return;
    }
    if (typeof this.data.moodIntensity !== "number" || this.data.moodIntensity < 1 || this.data.moodIntensity > 10) {
      wx.showToast({ title: '请选择情绪强度', icon: 'none' });
      return;
    }
    if (this.data.submitting) return;

    this.setData({ submitting: true });
    wx.showLoading({ title: '记录中...' });

    // 直接存储中文情绪文本和说明文本，无需映射
    // 直接使用中文值，无需映射
    let mainMoodText = this.data.mainMood;
    if (mainMoodText === '其他' && this.data.mainMoodOther) {
      mainMoodText = this.data.mainMoodOther;
    }

    let moodSupplementTagsText = this.data.moodSupplementTags;
    // moodSupplementTags 必须为 dict，若为数组则转为 {}
    if (Array.isArray(moodSupplementTagsText)) {
      moodSupplementTagsText = {};
    }

    const submitData = {
      mainMood: mainMoodText,
      moodIntensity: this.data.moodIntensity,
      mainMoodOther: this.data.mainMoodOther,
      moodSupplementTags: moodSupplementTagsText,
      moodSupplementText: this.data.moodSupplementText.trim(),
      supplementMoodList: this.data.supplementMoodList || []
    };

    journalApi.createJournal(submitData)
      .then(() => {
        wx.showToast({ title: '心情记录成功', icon: 'success' });
        // 清空输入
        this.setData({
          mainMood: "",
          mainMoodOther: "",
          moodIntensity: 0,
          moodSupplementTags: {},
          moodSupplementText: ""
        }, () => {
          // 状态重置后再刷新提交按钮状态
          this.setData({ submitting: false });
        });
        this.loadJournals();
      })
      .catch((error) => {
        console.error('提交心情记录失败:', error);
        wx.showToast({ title: error.message || '记录失败，请重试', icon: 'none' });
        this.setData({ submitting: false });
      })
      .finally(() => {
        wx.hideLoading();
      });
  },

  /**
   * 获取情绪文本
   */
  // 已用中文 value，无需映射
  getMoodText(moodValue, otherText) {
    return moodValue || (otherText || '其他情绪');
  },

  /**
   * 构建补充说明文本
   */
  buildSupplementText() {
    let text = '';
    
    // 添加标签信息
    if (this.data.moodSupplementTags.length > 0) {
      text += '原因：' + this.data.moodSupplementTags.join('、') + '。';
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
