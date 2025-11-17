// pages/index/index.js
const auth = require('../../utils/auth');
const emotionApi = require('../../api/emotiontracker');

Page({
  data: {
    currentDate: '',
    currentTime: '',
    userNickname: '',
    currentPeriod: '', 
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
    // 页面显示时加载情绪状态（从其他页面返回时会触发）
    this.loadEmotionStatus();
  },

  onLoad() {
    this.getCurrentDate();
    this.getCurrentTime();
    this.loadUserInfo();
    this.updatePeriod(); // 更新时段
    this.loadEmotionStatus();

    // 每分钟更新时间（仅时间显示，不再轮询情绪状态）
    this.timer = setInterval(() => {
      this.getCurrentTime();
      this.updatePeriod(); // 同时更新时段
    }, 60000);
  },

  onUnload() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  },

  loadEmotionStatus() {
    emotionApi.getTodayStatus().then(res => {
      console.log('获取今日状态成功:', res);

      this.setData({
        morningFilled: !!res.morning_filled,
        eveningFilled: !!res.evening_filled
      });



    }).catch((error) => {
      console.error('获取今日状态失败:', error);
      console.error('错误详情:', error.message);

      this.setData({
        morningFilled: false,
        eveningFilled: false
      });

      // 只在首次加载时显示错误提示
      if (!this.data.morningFilled && !this.data.eveningFilled) {
        console.log('使用默认状态: 均未完成');
      }
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
    wx.switchTab({ url: '/pages/mood/journal/journal' });
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
    const period = e?.currentTarget?.dataset?.period || this.data.currentPeriod;
    const isMorning = period === 'morning';
    const isEvening = period === 'evening';
    const now = new Date();
    const hours = now.getHours();

    // 早上不允许填写晚间
    if (isEvening && hours < 14) {
      wx.showToast({
        title: '请于14:00后填写晚间记录',
        icon: 'none'
      });
      return;
    }

    const isFilled = (isMorning && this.data.morningFilled) || (isEvening && this.data.eveningFilled);

    if (isFilled) {
      wx.showModal({
        title: '提示',
        content: '您已经完成了今天的情绪测试，是否重新测试？',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({
              url: `/pages/mood/moodtest/moodtest?period=${period}`
            });
          }
        }
      });
    } else {
      wx.navigateTo({
        url: `/pages/mood/moodtest/moodtest?period=${period}`
      });
    }
  },

  /**
   * 开始认知评估流程 - 直接跳转到智能测评
   */
  startCognitiveFlow() {
    wx.navigateTo({
      url: '/pages/assessment/smart/smart'
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
