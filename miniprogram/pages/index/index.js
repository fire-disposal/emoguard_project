// pages/index/index.js
const auth = require('../../utils/auth');
const emotionApi = require('../../api/emotiontracker');

Page({
  data: {
    currentDate: '',
    currentTime: '',
    userNickname: '',
    currentPeriod: '', // 添加当前时段（早间/晚间）
    // 认知评估引导
    showCognitiveGuide: false,
    hasCompletedAssessment: false,
    morningFilled: false,
    eveningFilled: false
  },

  onShow() {
    if (!auth.isLogined()) {
      auth.navigateToLogin();
      return;
    }
  },

  onLoad() {
    this.getCurrentDate();
    this.getCurrentTime();
    this.loadUserInfo();
    this.updatePeriod(); // 更新时段
    this.loadEmotionStatus();

    // 每分钟更新时间
    this.timer = setInterval(() => {
      this.getCurrentTime();
      this.updatePeriod(); // 同时更新时段
      this.loadEmotionStatus();
    }, 60000);
  },

  onUnload() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  },

  loadEmotionStatus() {
    // 新接口无需 userId，自动识别当前用户
    emotionApi.getTodayStatus().then(res => {
      this.setData({
        morningFilled: !!res.morning_filled,
        eveningFilled: !!res.evening_filled
      });
    }).catch(() => {
      this.setData({ morningFilled: false, eveningFilled: false });
    });
  },

  /**
   * 获取当前日期
   */
  getCurrentDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;
    const day = now.getDate();
    const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
    const weekday = weekdays[now.getDay()];
    
    this.setData({
      currentDate: `${year}年${month}月${day}日 ${weekday}`
    });
  },

  /**
   * 获取当前时间
   */
  getCurrentTime() {
    const now = new Date();
    const hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    
    this.setData({
      currentTime: `${hours}:${minutes}`
    });
  },

  /**
   * 更新当前时段（早间/晚间）
   */
  updatePeriod() {
    const now = new Date();
    const hours = now.getHours();
    let period = '';
    let periodText = '';
    
    if (hours >= 5 && hours < 12) {
      period = 'morning';
      periodText = '早间';
    } else if (hours >= 12 && hours < 18) {
      period = 'afternoon';
      periodText = '下午';
    } else {
      period = 'evening';
      periodText = '晚间';
    }
    
    this.setData({
      currentPeriod: period,
      currentPeriodText: periodText
    });
  },

  /**
   * 加载用户信息
   */
  loadUserInfo() {
    const userInfo = auth.getUserInfo();
    
    // 检查是否完成认知评估
    const hasCompleted = userInfo?.has_completed_cognitive_assessment || false;
    const showGuide = !hasCompleted;
    
    this.setData({
      userNickname: userInfo?.nickname || '用户',
      hasCompletedAssessment: hasCompleted,
      showCognitiveGuide: showGuide
    });
  },

  /**
   * 跳转到情绪记录
   */
  goToMoodRecord() {
    wx.switchTab({ url: '/pages/mood/record/record' });
  },

  /**
   * 跳转到测评页面
   */
  goToAssessment() {
    wx.navigateTo({ url: '/pages/assessment/select/select' });
  },

  /**
   * 跳转到文章列表
   */
  goToArticles() {
    wx.navigateTo({ url: '/pages/articles/list/list' });
  },

  /**
   * 跳转到健康报告
   */
  goToReports() {
    wx.navigateTo({ url: '/pages/reports/list/list' });
  },

  /**
   * 跳转到情绪测试
   */
  goToEmotionTest(e) {
    // e.currentTarget.dataset.period: 'morning' or 'evening'
    const now = new Date();
    const hours = now.getHours();
    let period = '';
    if (e && e.currentTarget && e.currentTarget.dataset && e.currentTarget.dataset.period) {
      period = e.currentTarget.dataset.period;
    } else {
      period = this.data.currentPeriod;
    }
    // 早上不允许填写晚间
    if (period === 'evening' && hours < 14) {
      wx.showToast({
        title: '请于14:00后填写晚间记录',
        icon: 'none'
      });
      return;
    }
    wx.navigateTo({
      url: `/pages/emotiontracker/record/record?period=${period}`
    });
  },

  /**
   * 开始认知评估流程
   */
  startCognitiveFlow() {
    wx.navigateTo({
      url: '/pages/assessment/flow/flow'
    });
  },

  /**
   * 关闭引导卡片
   */
  closeCognitiveGuide() {
    this.setData({
      showCognitiveGuide: false
    });
  }
});
