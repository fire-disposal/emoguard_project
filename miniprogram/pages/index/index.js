const auth = require('../../utils/auth');
  // 已全局获取，无需单独请求
const errorUtil = require('../../utils/error');
const subscribeUtil = require('../../utils/subscribeUtil');

Page({
  data: {
    currentDate: '', // 格式：2023年10月26日 星期四
    currentTime: '', // 格式：14:30
    userNickname: '',
    currentPeriod: '', // 当前时段标识: 'morning', 'afternoon', 'evening'
    currentPeriodText: '', // 当前时段中文: '早间', '下午', '晚间'
    showCognitiveGuide: false, // 是否显示认知评估引导卡片
    hasCompletedAssessment: false, // 是否已完成认知评估
    morningFilled: false, // 早上情绪记录是否已填写
    eveningFilled: false, // 晚上情绪记录是否已填写
    isMorningOpen: false, // 早间测评是否开放
    isEveningOpen: false, // 晚间测评是否开放
  },

  onShow() {
    // 统一调用全局防抖鉴权检查
    getApp().debouncedCheckAuth();
    // 页面显示时直接从全局获取填写状态
    this.setData({
      morningFilled: getApp().globalData.morningFilled,
      eveningFilled: getApp().globalData.eveningFilled
    });
  },

  onLoad() {
    this.getCurrentDate();
    this.loadUserInfo();

    // 初始化时间/时段并设置定时器
    this.updateTimeAndPeriod();

    // 每分钟更新时间
    this.timer = setInterval(() => {
      this.updateTimeAndPeriod();
    }, 60000);
  },

  onUnload() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  },

  /**
   * 加载今日情绪记录状态
   */
  // 已废弃，去除 status 请求

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
   * 更新当前时间和时段
   */
  updateTimeAndPeriod() {
    const now = new Date();
    const hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');

    let period = '';
    let periodText = '';

    // 时段划分逻辑：
    if (hours >= 5 && hours < 12) {
      period = 'morning'; // 5:00 - 11:59
      periodText = '早间';
    } else if (hours >= 12 && hours < 18) {
      period = 'afternoon'; // 12:00 - 17:59
      periodText = '下午';
    } else {
      period = 'evening'; // 18:00 - 4:59 (晚间/夜间)
      periodText = '晚间';
    }

    // 判断测评开放时间
    const isMorningOpen = hours >= 8 && hours < 10; 
    const isEveningOpen = hours >= 20 && hours < 22;

    this.setData({
      currentTime: `${hours}:${minutes}`,
      currentPeriod: period,
      currentPeriodText: periodText,
      isMorningOpen: isMorningOpen,
      isEveningOpen: isEveningOpen
    });
  },

  /**
   * 加载用户信息
   */
  async loadUserInfo() {
    let userInfo = getApp().globalData.userInfo;
    if (!userInfo || userInfo.is_profile_complete === undefined) {
      // 若无全局用户信息则异步获取
      userInfo = await getApp().getUserInfoAsync();
    }

    // 检查是否完成认知评估
    const hasCompleted = userInfo?.has_completed_cognitive_assessment || false;

    this.setData({
      userNickname: userInfo?.nickname || '用户',
      hasCompletedAssessment: hasCompleted,
      // 仅在未完成评估时显示引导
      showCognitiveGuide: !hasCompleted
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
   * 获取情绪测试状态
   * @param {string} period - 时段: 'morning' 或 'evening'
   * @returns {string} - 状态: 'completed', 'unopened', 'pending'
   */
  getEmotionTestStatus(period) {
    const isFilled = (period === 'morning' && this.data.morningFilled) ||
      (period === 'evening' && this.data.eveningFilled);
    
    if (isFilled) {
      return 'completed';
    }
    
    const isOpen = period === 'morning' ? this.data.isMorningOpen : this.data.isEveningOpen;
    return isOpen ? 'pending' : 'unopened';
  },

  /**
   * 跳转到情绪测试
   * @param {Object} e - 事件对象，dataset.period 可用于指定早间/晚间
   */
  goToEmotionTest(e) {
    const period = e?.currentTarget?.dataset?.period || this.data.currentPeriod;
    const now = new Date();
    const hours = now.getHours();

    // 严格时间限制：早间测评 8:00-10:00，晚间测评 20:00-22:00
    if (period === 'morning') {
      if (hours < 8 || hours >= 10) {
        wx.showModal({
          title: '测评未开放',
          content: '早间测评时间为 8:00-10:00，您可预约下一次测评并订阅提醒。',
          confirmText: '预约订阅',
          cancelText: '取消',
          success: (res) => {
            if (res.confirm) {
              const templateId = '5er1e9forv8HdkH8X6mBYp0JbkFeo4kNPCRi0uKZEJI';
              subscribeUtil.subscribeMessage(templateId);
            }
          }
        });
        return;
      }
    } else if (period === 'evening') {
      if (hours < 20 || hours >= 22) {
        wx.showModal({
          title: '测评未开放',
          content: '晚间测评时间为 20:00-22:00，您可预约下一次测评并订阅提醒。',
          confirmText: '预约订阅',
          cancelText: '取消',
          success: (res) => {
            if (res.confirm) {
              const templateId = '5er1e9forv8HdkH8X6mBYp0JbkFeo4kNPCRi0uKZEJI';
              subscribeUtil.subscribeMessage(templateId);
            }
          }
        });
        return;
      }
    }

    const status = this.getEmotionTestStatus(period);

    if (status === 'completed') {
      // 已填写，弹窗确认是否重测
      wx.showModal({
        title: '提示',
        content: '您已完成本次情绪测试，是否重新测试？',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({
              url: `/pages/mood/moodtest/moodtest?period=${period}`
            });
          }
        }
      });
    } else {
      // 未填写或未开放，直接跳转
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