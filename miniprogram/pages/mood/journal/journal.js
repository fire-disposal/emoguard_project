// pages/mood/journal/journal.js
const journalApi = require('../../../api/journal');
const authCenter = require('../../../utils/authCenter');

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
      { value: '身体不适', text: '身体不适' },
      { value: '家庭事务', text: '家庭事务' },
      { value: '记忆困扰', text: '记忆困扰' },
      { value: '睡眠不好', text: '睡眠不好' },
      { value: '工作/学习压力', text: '工作/学习压力' },
      { value: '其他', text: '其他' }
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

const MOOD_EMOJIS = JOURNAL_QUESTIONS[0].options.reduce((acc, mood) => {
  acc[mood.value] = mood.emoji;
  return acc;
}, {});

Page({
  data: {
    // 答案数据
    mainMood: "",
    mainMoodOther: "",
    moodIntensity: 5, // 默认值
    moodSupplementTags: [], // 应该为数组
    moodSupplementText: "",
    startedAt: null, // 新增：开始作答时间

    // 页面状态
    submitting: false,
    journals: [],
    loading: false,
    showHistory: true,

    // 题目配置
    questions: JOURNAL_QUESTIONS,
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
  async loadJournals() {
    const userInfo = authCenter.getUserInfo();
    if (!userInfo) return;

    this.setData({ loading: true });

    try {
      const res = await journalApi.listJournals({
        user_id: userInfo.id,
        page: 1,
        page_size: 10
      });
      const journals = (res || []).map(item => ({
        ...item,
        emoji: MOOD_EMOJIS[item.mainMood || item.label] || '🤔',
        mainMood: item.mainMood || item.label || '未知',
        mainMoodText: this.getMoodText(item.mainMood, item.mainMoodOther),
        mood_score: item.mood_score || item.score || item.moodIntensity || 5,
        text: item.moodSupplementText || '', // 使用 moodSupplementText 字段
        created_at: item.created_at || new Date().toISOString()
      }));

      this.setData({ journals });
    } catch (error) {
      console.error('加载历史记录失败:', error);
      this.setData({ journals: [] });
    } finally {
      this.setData({ loading: false });
    }
  },

  // 处理情绪选择（特殊类型的单选）
  handleMoodSelect(e) {
    const { key, value } = e.currentTarget.dataset;
    const isOther = value === '其他';

    // 如果是第一题第一次选择，记录开始作答时间
    if (!this.data.startedAt) {
      this.setData({ startedAt: new Date().toISOString() });
    }

    this.setData({
      [key]: value,
      mainMoodOther: isOther ? this.data.mainMoodOther : '',
    });
  },

  // 滑动题事件处理
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

  // 处理文本输入变化 (通用，用于 mainMoodOther)
  handleTextChange(e) {
    const { key } = e.currentTarget.dataset;
    this.setData({ [key]: e.detail.value });
  },

  // 绑定补充说明文本框输入
  handleSupplementTextInput(e) {
    this.setData({
      moodSupplementText: e.detail.value
    });
  },

  // 获取复选框选中状态
  isCheckboxSelected(questionKey, optionValue) {
    return (this.data[questionKey] || []).includes(optionValue);
  },

  /**
   * 提交心情记录
   */
  async submitMoodRecord() {
    const { mainMood, mainMoodOther, moodIntensity, moodSupplementTags, moodSupplementText, submitting, startedAt } = this.data;

    if (!mainMood || (mainMood === '其他' && !mainMoodOther.trim())) {
      wx.showToast({ title: '请选择主观情绪并填写其他情绪', icon: 'none' });
      return;
    }
    if (moodIntensity < 1 || moodIntensity > 10) {
      wx.showToast({ title: '请选择情绪强度', icon: 'none' });
      return;
    }
    if (submitting) return;

    this.setData({ submitting: true });
    wx.showLoading({ title: '记录中...' });

    const submitData = {
      mainMood: mainMood === '其他' ? mainMoodOther : mainMood,
      moodIntensity: moodIntensity,
      mainMoodOther: mainMood === '其他' ? mainMoodOther : '',
      moodSupplementTags: moodSupplementTags,
      moodSupplementText: moodSupplementText.trim(),
      started_at: startedAt, // 新增：上传开始作答时间
    };

    try {
      await journalApi.createJournal(submitData);
      wx.showToast({ title: '心情记录成功', icon: 'success' });
      this.resetFormData();
      if (this.data.showHistory) {
        this.loadJournals();
      }
    } catch (error) {
      console.error('提交心情记录失败:', error);
      wx.showToast({ title: error.message || '记录失败，请重试', icon: 'none' });
    } finally {
      this.setData({ submitting: false });
      wx.hideLoading();
    }
  },

  // 重置表单数据
  resetFormData() {
    this.setData({
      mainMood: "",
      mainMoodOther: "",
      moodIntensity: 5,
      moodSupplementTags: [],
      moodSupplementText: "",
      startedAt: null, // 新增：重置开始作答时间
    });
  },

  /**
   * 获取情绪文本（历史记录展示用）
   */
  getMoodText(moodValue, otherText) {
    return moodValue === '其他' ? (otherText || '其他情绪') : moodValue;
  },

  /**
   * 切换历史记录显示
   */
  toggleHistory() {
    this.setData({ showHistory: !this.data.showHistory });
  },

  /**
   * 格式化时间
   */
  formatTime(dateString) {
    const date = new Date(dateString);
    return `${date.getMonth() + 1}月${date.getDate()}日 ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
  }
});