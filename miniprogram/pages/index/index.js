// pages/index/index.js
const auth = require('../../utils/auth');

Page({
  data: {
    currentDate: '',
    currentTime: '',
    userNickname: ''
  },

  onLoad() {
    this.getCurrentDate();
    this.getCurrentTime();
    this.loadUserInfo();
    
    // 每分钟更新时间
    this.timer = setInterval(() => {
      this.getCurrentTime();
    }, 60000);
  },

  onUnload() {
    if (this.timer) {
      clearInterval(this.timer);
    }
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
   * 加载用户信息
   */
  loadUserInfo() {
    const userInfo = auth.getUserInfo();
    this.setData({
      userNickname: userInfo?.nickname || '用户'
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
  }
});
