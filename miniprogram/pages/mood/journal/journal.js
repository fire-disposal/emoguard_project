// pages/mood/journal/journal.js
const journalApi = require('../../../api/journal');
const auth = require('../../../utils/auth');

Page({
  data: {
    selectedMood: '',
    moodReason: '',
    moodOptions: [
      { value: 'very-happy', emoji: '😄', label: '非常开心', score: 9, name: '非常开心' },
      { value: 'happy', emoji: '😊', label: '开心', score: 7, name: '开心' },
      { value: 'normal', emoji: '😐', label: '一般', score: 5, name: '一般' },
      { value: 'sad', emoji: '😔', label: '难过', score: 3, name: '难过' },
      { value: 'very-sad', emoji: '😢', label: '很难过', score: 1, name: '很难过' },
      { value: 'anxious', emoji: '😰', label: '焦虑', score: 2, name: '焦虑' }
    ],
    journals: [],
    loading: false,
    submitting: false
  },

  onShow() {
    if (!auth.isLogined()) {
      auth.navigateToLogin();
      return;
    }
    // 刷新列表
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
      page_size: 20
    })
    .then((res) => {
      this.setData({
        journals: res || []
      });
    })
    .catch((error) => {
      console.error('加载历史记录失败:', error);
    })
    .finally(() => {
      this.setData({ loading: false });
    });
  },

  /**
   * 选择心情
   */
  selectMood(e) {
    const { value } = e.currentTarget.dataset;
    this.setData({ selectedMood: value });
  },

  /**
   * 输入心情原因
   */
  onReasonInput(e) {
    this.setData({ moodReason: e.detail.value });
  },

  /**
   * 提交心情记录
   */
  submitMoodRecord() {
    if (!this.data.selectedMood) {
      wx.showToast({
        title: '请选择心情',
        icon: 'none'
      });
      return;
    }

    if (this.data.submitting) return;

    const moodConfig = this.data.moodOptions.find(m => m.value === this.data.selectedMood);
    if (!moodConfig) {
      wx.showToast({
        title: '无效的心情选择',
        icon: 'none'
      });
      return;
    }

    this.setData({ submitting: true });
    wx.showLoading({ title: '记录中...' });

    const now = new Date();
    const recordDate = now.toISOString();

    journalApi.createJournal({
      mood_score: moodConfig.score,
      mood_name: moodConfig.name,
      text: this.data.moodReason.trim() || ''
    })
    .then(() => {
      wx.showToast({
        title: '心情记录成功',
        icon: 'success'
      });

      // 清空输入
      this.setData({
        selectedMood: '',
        moodReason: ''
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
